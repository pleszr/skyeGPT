from functools import wraps
from fastapi import status, HTTPException
import asyncio
from fastapi.responses import StreamingResponse
from common import logger, message_bundle, constants
from common.exceptions import StoreManagementException, ResponseGenerationError, UsageLimitExceededError
import json
from typing import AsyncGenerator


def handle_response_stream_errors(func):
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
        except Exception:
            logger.exception("Uncaught Exception")
            return _generate_sse_stream_from_error_message(message_bundle.INTERNAL_ERROR)
    return wrapper


def _generate_sse_stream_from_error_message(
        response_error_message: str = message_bundle.INTERNAL_ERROR
) -> StreamingResponse:
    return StreamingResponse(
        _stream_error(response_error_message),
        media_type=constants.MEDIA_TYPE_SSE,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={
            "Cache-Control": "no-cache",
            "Connection":    "keep-alive",
        }
    )


async def _stream_error(
        error_message: str
) -> AsyncGenerator[str, None]:
    error_data = {"detail": error_message}
    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


def handle_aggregated_response_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UsageLimitExceededError as e:
            logger.exception(e.message)
            raise HTTPException(status_code=429, detail=message_bundle.USAGE_LIMIT_EXCEEDED_ERROR)
        except ResponseGenerationError as e:
            logger.exception(e.message)
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR)
        except Exception:
            logger.exception("Uncaught Exception")
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR)
    return wrapper


def handle_unknown_errors(func):
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


def handle_store_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.exception('Exception during Store Management')
            raise StoreManagementException from e
    return wrapper
