"""Main entry point for the mcp_server package."""

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Kubernetes MCP Server", version="0.1.0", author="Shreyas")

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
