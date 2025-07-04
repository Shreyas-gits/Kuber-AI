"""Main entry point for the mcp_server."""

import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
from src.tools.tool_loader import register_kubernetes_tools  # noqa E402
from src.utils.logging_config import setup_logging  # noqa E402

# setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Kubernetes MCP Server", version="0.1.0", author="Shreyas")

# Register Kubernetes API tools
register_kubernetes_tools(mcp)

if __name__ == "__main__":
    logger.info("🚀 Starting MCP server🚀")

    # http_mcp_app = mcp.streamable_http_app()
    # # Run the MCP server
    # uvicorn.run(http_mcp_app, host="0.0.0.0", port=8080)

    mcp.run()
