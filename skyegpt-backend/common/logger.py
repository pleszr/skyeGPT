"""Provides a centralized and consistent logging interface for the application.

The primary purpose of this abstraction is to simplify potential future
migrations to a different logging library which seems likely in case we move away from Pydantic AI.

Usage:
    logger.info("User logged in", user_id=123)
    logger.error("Failed to process request", request_id="xyz")
"""

import logfire
import os

environment = os.environ.get("ENVIRONMENT", "local")
logfire.configure(environment=environment)


def trace(message: str, **kwargs):
    """Logs a trace-level message."""
    logfire.trace(message, **kwargs)


def debug(message: str, **kwargs):
    """Logs a debug-level message."""
    logfire.debug(message, **kwargs)


def info(message: str, **kwargs):
    """Logs an info-level message."""
    logfire.info(message, **kwargs)


def warning(message: str, **kwargs):
    """Logs a warning-level message."""
    logfire.warning(message, **kwargs)


def error(message: str, **kwargs):
    """Logs an error-level message."""
    logfire.error(message, **kwargs)


def critical(message: str, **kwargs):
    """Logs a critical-level message."""
    logfire.fatal(message, **kwargs)


def exception(message: str, **kwargs):
    """Logs an exception with traceback."""
    logfire.exception(message, **kwargs)
