from functools import wraps
from fastapi import status, HTTPException
import asyncio
from fastapi.responses import StreamingResponse
from common import logger, message_bundle, constants
from pydantic_ai import UserError, AgentRunError, UsageLimitExceeded
import json
from typing import AsyncGenerator


def catch_stream_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            raise
        except UsageLimitExceeded as e:
            logger.exception(e.message)
            return _generate_sse_stream_from_error_message(message_bundle.USAGE_LIMIT_EXCEEDED_ERROR)
        except (AgentRunError, UserError) as e:
            logger.exception(e.message)
            return _generate_sse_stream_from_error_message()
        except Exception:
            logger.exception("Uncaught Exception")
            return _generate_sse_stream_from_error_message()
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


def catch_response_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UsageLimitExceeded as e:
            logger.exception(e.message)
            raise HTTPException(status_code=429, detail=message_bundle.USAGE_LIMIT_EXCEEDED_ERROR)
        except (AgentRunError, UserError) as e:
            logger.exception(e.message)
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR)
        except Exception:
            logger.exception("Uncaught Exception")
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR)
    return wrapper


def catch_unknown_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as http_exc:
            raise http_exc
        except Exception:
            logger.exception("Uncaught Exception")
            raise HTTPException(status_code=500, detail=message_bundle.INTERNAL_ERROR)
    return wrapper
