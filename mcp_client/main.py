"""Main entry point for the mcp_client package."""

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from common.logging_config import setup_logging
from mcp_client.src.routers.conversation_router import router as conversation_router
from mcp_client.src.utils.lifespan import lifespan

load_dotenv()
setup_logging()

app = FastAPI(lifespan=lifespan)

app.include_router(conversation_router, tags=["conversation"])

if __name__ == "__main__":
    uvicorn.run("mcp_client.main:app", host="0.0.0.0", port=8080)
