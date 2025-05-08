from common import utils, logger
from agentic import agent_service, prompts
from typing import AsyncGenerator, Optional, Any
from common.stores import StoreManager
from agentic.conversation import Conversation
from fastapi import HTTPException, status


store_manager = StoreManager()


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
        logger.info(f"Asker service stream_agent_response started")
        agent_service_model = agent_service.AgentService(
            store_manager,
            prompts.responder_openai_v4_openai_template
        )

        agent_response_stream = await agent_service_model.stream_agent_response(question, conversation_id)
        formatted_stream = utils.async_format_to_sse(agent_response_stream)

        async for item in formatted_stream:
            yield item
        logger.info(f"Asker service stream_agent_response finished")


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
            nested_context: Optional[Any] = await _get_conversation_context(conversation_id)
            if nested_context:
                response["curr_context"] = nested_context

        return response


class ConversationRetrieverService:
    async def get_conversation_by_id(self, conversation_id: str) -> Conversation:
        conversation = await store_manager.get_conversation_by_id(conversation_id)
        if not conversation.content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conversation


class FeedbackManagerService:
    """Provides service to manage feedback. Save, store, retrieve & search"""
    def create_feedback(self):
        logger.info('this is where feedback management will be')


async def _aggregate_agent_response(question: str, conversation_id: str) -> dict[str, Any]:
    agent_service_model = agent_service.AgentService(
        store_manager,
        prompts.responder_openai_v4_openai_template
    )
    parts: list[str] = []
    async for chunk in await agent_service_model.stream_agent_response(question, conversation_id):
        parts.append(chunk)
    full_response = "".join(parts)
    return {"generated_answer": full_response}


async def _get_conversation_context(conversation_id: str) -> list[dict[str, Any]]:
    return await store_manager.get_conversation_context(conversation_id)
