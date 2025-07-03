"""Main entry point for the mcp_server package."""

from mcp.server.fastmcp import FastMCP

from src.tools.kubernetes_api_tool import register_kubernetes_tools
from src.utilities.configure_logging import setup_logging

# setup logging
setup_logging()

# Create an MCP server
mcp = FastMCP("Kubernetes MCP Server", version="0.1.0", author="Shreyas")

# Register Kubernetes API tools
register_kubernetes_tools(mcp)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
