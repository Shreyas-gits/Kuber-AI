"""Utility functions for configuring CORS in the FastAPI application."""

import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def configure_cors(app: FastAPI):
    """Configure CORS for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None

    Example:
        >>> from fastapi import FastAPI
        >>> from utils.CORS import configure_cors
        >>> app = FastAPI()
        >>> configure_cors(app)
    """
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS middleware configured for FastAPI application.")
