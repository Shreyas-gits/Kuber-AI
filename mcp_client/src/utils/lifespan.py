"""lifespan.py.

This module provides the FastAPI lifespan context manager for managing the FastMCP client.

Functions:
    lifespan(app: FastAPI): Async context manager for FastAPI app lifespan, handling FastMCP client setup and teardown.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for FastAPI app lifespan.

    Initializes the FastMCP client and attaches it to the app state at startup,
    and ensures proper cleanup at shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")
    try:
        logger.info(f"Initializing FastMCP client with URL: {mcp_server_url}")
        read, write, _ = await streamablehttp_client(mcp_server_url).__aenter__()
        session = ClientSession(read, write)
        await session.initialize()

        app.state.mcp_session = session
        yield
    except Exception as e:
        logger.error(f"Failed to initialize FastMCP client: {e}")
    finally:
        if hasattr(app.state, "mcp_session"):
            session = app.state.mcp_session
            logger.info("Cleaning up FastMCP client.")
            if hasattr(session, "aclose"):
                await session.aclose()
                logger.info("FastMCP client closed asynchronously.")
            elif hasattr(session, "close"):
                session.close()
                logger.info("FastMCP client closed synchronously.")
        else:
            logger.critical(
                f"FastMCP client was not initialized. The MCP server URL '{mcp_server_url}' "
                "may be incorrect. Shutting down application."
            )
            raise RuntimeError(
                "FastMCP client was not initialized. Please check the MCP_SERVER_URL environment variable."
            )
