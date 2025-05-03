from common import utils
from agentic import PydanticAi
from typing import AsyncGenerator, Optional, Any


class AgentResponseStreamingService:
    """
    Provides services for streaming responses from an AI agent.

    This class encapsulates the logic for interacting with the underlying AI model
    (currently via PydanticAi) and formatting the response chunks into a streamable format,
    specifically Server-Sent Events (SSE).
    """
    async def stream_agent_response(self, question: str, conversation_id: str) -> AsyncGenerator[str, None]:
        """
        Streams AI responses for a given question and conversation ID, formatted as SSE.

        This asynchronous method takes a user question and a conversation context ID,
        queries the PydanticAi agent (presumably interacting with Gemini),
        and yields the resulting response chunks formatted as Server-Sent Events.

        Args:
            question: The user's question or prompt for the AI agent.
            conversation_id: The unique identifier for the ongoing conversation
                to maintain context.

        Yields:
            str: Response chunks formatted as Server-Sent Events
                 (e.g., "data: chunk_of_text\n\n").

        Raises:
            UsageLimitExceeded: Error raised when a Model's usage exceeds the specified limits.
            UserError: Error caused by a usage mistake by the application developer
            AgentRunError: when the underlying AI model fails to generate a response.
            Exception: for any other unexpected errors.
        """
        formatted_stream = utils.async_format_to_sse(PydanticAi.ask_gemini(question, conversation_id))
        async for item in formatted_stream:
            yield item


class AgentResponseService:
    """
    Provides services for responses from an AI agent.

    This class encapsulates the logic for interacting with the underlying AI model. Optionally returns context too.
    """
    async def agent_response(self, question: str, conversation_id: str, with_context: bool) -> dict[str, Any]:
        """
        Generate a full answer (and optional context) for a question.

        Args:
            question (str): The user's question.
            conversation_id (str): ID for context lookup.
            with_context (bool): If True, include prior context.

        Returns:
            dict[str, Any]:
                {
                    "generated_answer": str,
                    "curr_context": Any  # only if with_context and exists
                }

        Raises:
            UsageLimitExceeded: …
            AgentRunError: …
            Exception: …
        """
        response = await _aggregate_agent_response(question, conversation_id)

        if with_context:
            nested_context: Optional[Any] = _get_conversation_context(conversation_id)
            if nested_context:
                response["curr_context"] = nested_context

        return response


async def _aggregate_agent_response(question: str, conversation_id: str) -> dict[str, Any]:
    parts: list[str] = []
    async for chunk in PydanticAi.ask_gemini(question, conversation_id):
        parts.append(chunk)
    full_response = "".join(parts)
    return {"generated_answer": full_response}


def _get_conversation_context(conversation_id: str) -> dict[str, Any]:
    return PydanticAi.current_context_store.get(conversation_id)
