"""Shared exception-handling decorators used across FastAPI services."""

from functools import wraps
from fastapi import status, HTTPException
from fastapi.responses import StreamingResponse
from common import logger, message_bundle, constants
from common.exceptions import StoreManagementException, ResponseGenerationError, UsageLimitExceededError
import json
from asyncio import Queue
from typing import AsyncGenerator


def handle_response_stream_errors(func):
    """Handles known errors and wraps the result in a StreamingResponse with SSE-compatible error messages."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UsageLimitExceededError as e:
            logger.exception(e.message)
            return _generate_sse_stream_from_error_message(message_bundle.USAGE_LIMIT_EXCEEDED_ERROR)
        except ResponseGenerationError as e:
            logger.exception(e.message)
            return _generate_sse_stream_from_error_message(message_bundle.INTERNAL_ERROR)
        except Exception:  # noqa: E722
            logger.exception("Uncaught Exception")
            return _generate_sse_stream_from_error_message(message_bundle.INTERNAL_ERROR)

    return wrapper


def _generate_sse_stream_from_error_message(
    response_error_message: str = message_bundle.INTERNAL_ERROR,
) -> StreamingResponse:
    """Creates a StreamingResponse with an error SSE payload."""
    return StreamingResponse(
        _stream_error(response_error_message),
        media_type=constants.MEDIA_TYPE_SSE,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


async def _stream_error(error_message: str) -> AsyncGenerator[str, None]:
    """Yields a single SSE-formatted error message."""
    error_data = {"detail": error_message}
    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


def handle_aggregated_response_errors(func):
    """Raises HTTPExceptions for known agent response errors with appropriate status codes."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UsageLimitExceededError as e:
            logger.exception(e.message)
            raise HTTPException(status_code=429, detail=message_bundle.USAGE_LIMIT_EXCEEDED_ERROR) from e
        except ResponseGenerationError as e:
            logger.exception(e.message)
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR) from e
        except Exception as e:
            logger.exception("Uncaught Exception")
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR) from e

    return wrapper


def handle_unknown_errors(func):
    """Re-raises known HTTPExceptions or wraps unknown exceptions in a generic 500 response."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.exception("Uncaught Exception")
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR) from e

    return wrapper


def handle_asyncio_producer_task_errors(queue_arg: int = -1, swallow: bool = False):
    """Catches and optionally rethrows exceptions in async tasks, while signaling failure via a queue."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            queue: Queue = args[queue_arg]
            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.exception(f"{func.__name__} failed")
                await queue.put(None)
                if not swallow:
                    raise

        return wrapper

    return decorator


def handle_store_errors(func):
    """Converts common data access errors into StoreManagementException."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.exception("Exception during Store Management")
            raise StoreManagementException from e

    return wrapper
