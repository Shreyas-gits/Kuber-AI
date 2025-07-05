"""conversation_router.py.

This module defines the FastAPI router for handling conversation endpoints,
including the /ask endpoint which creates and runs a LangGraph ReAct agent
with tools and returns the output.

Functions:
    ask_endpoint(request: AskRequest, fastapi_request: Request): Handles the /ask endpoint.
"""

import logging
from typing import TypedDict

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastmcp import Client
from langchain.agents import Tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from mcp_client.src.models.conversation_model import AskRequest

router = APIRouter()

logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """State schema for LangGraph conversation flow.

    Attributes:
        messages: List of messages exchanged during the conversation.
    """

    messages: list


@router.post("/ask")
async def ask_endpoint(request: AskRequest, fastapi_request: Request):
    """Handles the /ask endpoint by creating and running a LangGraph ReAct agent with tools.

    Args:
        request (AskRequest): The request body containing the user's query.
        fastapi_request (Request): The FastAPI request object, used to access app state.

    Returns:
        dict: A dictionary containing the output from the agent, or an error message.

    Raises:
        HTTPException: Returns a 500 error with the exception message if agent invocation fails.
    """
    logger.info(f"Received ask request with query: {request.query}")

    mcp_client: Client = fastapi_request.app.state.mcp_client
    logger.debug("Retrieved MCP client from app state")

    # Setup LLM
    logger.info("Setting up ChatGoogleGenerativeAI LLM")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001", temperature=0, max_tokens=None, timeout=None, max_retries=2
    )
    logger.debug("LLM setup completed")

    # Fetch tools from FastMCP and wrap them into LangChain Tool objects
    logger.info("Fetching tools from MCP client")
    async with mcp_client:
        tools = await mcp_client.list_tools()
        logger.info(f"Retrieved {len(tools)} tools from MCP client")
        logger.debug(f"Available tools: {[tool.name for tool in tools]}")

        langchain_tools = [
            Tool(
                name=tool.name,
                func=(lambda tool=tool: (lambda **kwargs: mcp_client.call_tool(tool.name, kwargs)))(),
                description=tool.description,
            )
            for tool in tools
        ]
        logger.debug("Successfully wrapped MCP tools into LangChain Tool objects")

    # Create LangGraph ReAct agent with LLM and tools
    logger.info("Creating LangGraph ReAct agent")
    agent = create_react_agent(llm, langchain_tools)
    logger.debug("ReAct agent created successfully")

    try:
        output = await agent.ainvoke({"messages": [HumanMessage(content=request.query)]})
        logger.info("Agent execution completed successfully")
        response_content = output.get("messages", [])
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content[-1].content if response_content else {"message": "No response from agent"},
        )
    except Exception as e:
        logger.error(f"Error during agent execution: {str(e)}", exc_info=True)
        error_response = {"error": str(e)}
        logger.warning("Returning error response")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)
