"""Logging configuration module for MCP server.

This module provides logging configuration and colored formatter functionality
for the Model Context Protocol server components.
"""

import logging.config
import os

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO").strip('"').upper()


class ColorFormatter(logging.Formatter):
    """Custom logging formatter that adds color to log levels and logger names.

    This formatter enhances log readability by applying ANSI color codes
    to different log levels and making logger names bold.
    """

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[41m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        """Format log record with colors and styling.

        Args:
            record: LogRecord instance to format.

        Returns:
            Formatted log string with color codes applied.
        """
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        original_format = self._style._fmt
        self._style._fmt = f"{color}{original_format}{reset}"
        try:
            return super().format(record)
        finally:
            self._style._fmt = original_format


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {"()": ColorFormatter, "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {"root": {"handlers": ["console"], "level": LOGGING_LEVEL, "propagate": False}},  # root logger
}


def setup_logging():
    """Set up logging configuration using the predefined colored logging config.

    Configures the logging system with colored output to stdout,
    making logs more readable during development and debugging.
    """
    logging.config.dictConfig(logging_config)
