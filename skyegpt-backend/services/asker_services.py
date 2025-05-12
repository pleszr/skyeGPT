from common import utils, logger, constants, message_bundle
from agentic import agent_service, prompts
from agentic.feedback import Feedback
from typing import AsyncGenerator, Optional, Any
from common.stores import StoreManager
from agentic.conversation import Conversation
from fastapi import HTTPException, status
import uuid
from database import documentdb_client


store_manager = StoreManager()


class AgentResponseStreamingService:
    """
    Provides services for streaming responses from an AI agent.

    This class encapsulates the logic for interacting with the underlying AI model
    (currently via PydanticAi) and formatting the response chunks into a streamable format,
    specifically Server-Sent Events (SSE).
    """
    async def stream_agent_response(self, question: str, conversation_id: uuid) -> AsyncGenerator[str, None]:
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
    async def agent_response(self, question: str, conversation_id: uuid, with_context: bool) -> dict[str, Any]:
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
        response = await self._aggregate_agent_response(question, conversation_id)

        if with_context:
            nested_context: Optional[Any] = await self._get_conversation_context(conversation_id)
            if nested_context:
                response["curr_context"] = nested_context
        return response

    async def _aggregate_agent_response(self, question: str, conversation_id: uuid) -> dict[str, Any]:
        agent_service_model = agent_service.AgentService(
            store_manager,
            prompts.responder_openai_v4_openai_template
        )
        parts: list[str] = []
        async for chunk in await agent_service_model.stream_agent_response(question, conversation_id):
            parts.append(chunk)
        full_response = "".join(parts)
        return {"generated_answer": full_response}

    async def _get_conversation_context(self, conversation_id: uuid) -> list[dict[str, Any]]:
        return await store_manager.get_conversation_context(conversation_id)


class ConversationRetrieverService:
    async def get_conversation_by_id(self, conversation_id: uuid) -> Conversation:
        conversation = await store_manager.get_conversation_by_id(conversation_id)
        if not conversation.content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conversation

    def find_conversations_by_feedback_created_since(self, feedback_within_hours: int):
        logger.info(f"Searching for conversations in last {feedback_within_hours} hours")
        utc_x_hours_ago = utils.calculate_utc_x_hours_ago(feedback_within_hours)
        return documentdb_client.find_conversations_by_created_since(utc_x_hours_ago)


class FeedbackManagerService:
    """Provides service to manage feedback. Save, store, retrieve & search"""
    def create_feedback(self, conversation_id: uuid, vote: constants.VoteType, comment: str) -> None:
        feedback = Feedback(vote=vote, comment=comment)
        conversation = self._find_conversation(conversation_id)
        conversation.add_feedback(feedback)
        documentdb_client.update_conversation(conversation.conversation_id, conversation)
        logger.info(f"Added feedback {feedback.id} ({vote}) to conversation {conversation.conversation_id}")

    def _find_conversation(self, conversation_id: uuid) -> Conversation:
        conversation = documentdb_client.find_conversation_by_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message_bundle.CONVERSATION_NOT_FOUND)
        return conversation
