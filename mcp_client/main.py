"""Main entry point for the mcp_client package."""

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastmcp import Client
from la import AgentConfig, GraphAgent
from langchain_google_genai import ChatGoogleGenerativeAI

from common.logging_config import setup_logging
from mcp_client.src.models.conversation_model import AskRequest

load_dotenv()
setup_logging()

# HTTP server
client = Client("http://127.0.0.1:8000/mcp/")

app = FastAPI()


@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    """Handle /ask endpoint: create and run a LangGraph agent with tools and return output."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, max_tokens=None, timeout=None, max_retries=2)
    async with client:
        tools = await client.list_tools()
        # Convert FastMCP tools to LangGraph-compatible tools if needed
        graph_tools = [
            {
                "name": tool.name,
                "func": (lambda tool=tool: (lambda **kwargs: client.call_tool(tool.name, kwargs)))(),
                "description": tool.description,
            }
            for tool in tools
        ]
        # Create the LangGraph agent
        agent_config = AgentConfig(tools=graph_tools, llm=llm, verbose=True)
        agent = GraphAgent(agent_config)
        try:
            output = await agent.run(request.query)  # Assuming async run
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
        return {"output": output}


if __name__ == "__main__":
    uvicorn.run("mcp_client.main:app", host="0.0.0.0", port=8080)
