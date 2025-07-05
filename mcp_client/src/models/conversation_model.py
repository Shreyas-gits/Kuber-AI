"""Models for conversation handling in mcp_client."""

from pydantic import BaseModel


class AskRequest(BaseModel):
    """Request model for /ask endpoint containing the user query."""

    query: str
