"""Main entry point for the mcp_server."""

import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
from common.logging_config import setup_logging  # noqa
from mcp_server.src.tools.tool_loader import register_kubernetes_tools  # noqa

# setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Kubernetes MCP Server", version="0.1.0", author="Shreyas")

# Register Kubernetes API tools
register_kubernetes_tools(mcp)

if __name__ == "__main__":
    logger.info("🚀 Starting MCP server🚀")

    # Run the MCP server
    mcp.run(transport="streamable-http")
