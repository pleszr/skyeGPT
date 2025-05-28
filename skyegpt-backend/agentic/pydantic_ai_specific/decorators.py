from pydantic_ai import UserError, AgentRunError, UsageLimitExceeded as PY_UsageLimitExceeded
from functools import wraps
from common.exceptions import ResponseGenerationError, UsageLimitExceededError
from common import logger


def handle_pydantic_stream_response_errors(func):
    """
    Decorator for async generator functions to handle specific Pydantic AI exceptions,
    log them, and map them to application-specific exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            async for item in func(*args, **kwargs):
                yield item
        except PY_UsageLimitExceeded as e:
            logger.warning(e.message)
            raise UsageLimitExceededError(e.message) from e
        except (AgentRunError, UserError) as e:
            logger.exception(e.message)
            raise ResponseGenerationError(e.message) from e

    return wrapper
