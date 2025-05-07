import logfire
import os

"""
    Provides a centralized and consistent logging interface for the application.
    The primary purpose of this abstraction is to simplify potential future
    migrations to a different logging library which seems likely in case we move away from Pydantic AI.

    Usage:
        logger.info("User logged in", user_id=123)
        logger.error("Failed to process request", request_id="xyz")
"""

environment = os.environ.get('ENVIRONMENT', 'local')
logfire.configure(environment=environment)

def trace(message: str, **kwargs):
    logfire.trace(message, **kwargs)


def debug(message: str, **kwargs):
    logfire.debug(message, **kwargs)


def info(message: str, **kwargs):
    logfire.info(message, **kwargs)


def warning(message: str, **kwargs):
    logfire.warning(message, **kwargs)


def error(message: str, **kwargs):
    logfire.error(message, **kwargs)


def critical(message: str, **kwargs):
    logfire.fatal(message, **kwargs)


def exception(message: str, **kwargs):
    logfire.exception(message, **kwargs)
