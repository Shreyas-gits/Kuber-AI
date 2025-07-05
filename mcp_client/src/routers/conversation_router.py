"""conversation_router.py.

This module defines the FastAPI router for handling conversation endpoints,
including the /ask endpoint which creates and runs a LangGraph ReAct agent
with tools and returns the output.

Functions:
    ask_endpoint(request: AskRequest, fastapi_request: Request): Handles the /ask endpoint.
"""

import logging
import os

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from ..models.conversation_model import AskRequest

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/ask")
async def ask_endpoint(request: AskRequest):
    """Handles the /ask endpoint by creating and running a LangGraph ReAct agent with tools.

    This function creates a LangGraph ReAct agent with MCP tools and executes it
    with the user's query. It connects to an MCP server, loads available tools,
    and runs the agent to generate a response.

    Args:
        request (AskRequest): The request object containing the user's query.

    Returns:
        JSONResponse: A JSON response containing either:
            - The agent's response content (status 200)
            - An error message (status 500)

    Raises:
        Exception: Any exception during agent execution is caught and returned
            as a 500 error response.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001", temperature=0, max_tokens=None, timeout=None, max_retries=2
    )

    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")

    try:
        async with streamablehttp_client(mcp_server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                langchain_tools = await load_mcp_tools(session)
                agent = create_react_agent(llm, langchain_tools)

                # Execute agent within the session context
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
