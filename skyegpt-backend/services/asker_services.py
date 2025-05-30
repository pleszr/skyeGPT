"""Services for streaming and aggregating AI agent responses."""

from common import utils, logger, constants, message_bundle
from agentic import prompts
from agentic.agent_service import AgentService
from agentic.feedback import Feedback
from typing import AsyncGenerator, Optional, Any, List
from common.stores import StoreManager
from common.decorators import handle_asyncio_producer_task_errors
from agentic.conversation import Conversation
from fastapi import HTTPException, status
import uuid
from database import documentdb_client
from agentic.dynamic_loading_text_service import DynamicLoadingTextService
from common.constants import SseEventTypes
import json
import asyncio


store_manager = StoreManager()


class AgentResponseStreamingService:
    """Provides services for streaming responses from an AI agent.

    This class encapsulates the logic for interacting with the underlying AI model
    (currently via PydanticAi) and formatting the response chunks into a streamable format,
    specifically Server-Sent Events (SSE).
    """

    async def stream_agent_response(self, user_question: str, conversation_id: uuid) -> AsyncGenerator[str, None]:
        """Streams AI responses as SSE events.

        Args:
            user_question (str): The user's question.
            conversation_id (uuid.UUID): Unique conversation ID.

        Yields:
            str: SSE-formatted response chunks.

        Raises:
            UsageLimitExceededError: When usage limits are reached.
            ResponseGenerationError: On generation errors.
        """
        queue = asyncio.Queue()
        _loading_text_task = asyncio.create_task(self._produce_loading_texts(user_question, queue))
        _response_task = asyncio.create_task(self._produce_response(user_question, conversation_id, queue))

        done_streams = 0
        while done_streams < 2:
            item = await queue.get()
            if item is None:
                done_streams += 1
            else:
                yield item
        logger.info("Asker service stream_agent_response finished")

    @staticmethod
    @handle_asyncio_producer_task_errors(-1, False)
    async def _produce_loading_texts(user_question: str, queue: asyncio.Queue):
        r"""Generates dynamic loading texts and puts them into the queue as SSE events.

        Args:
            user_question (str): The user's question.
            queue (asyncio.Queue): Queue to put SSE-formatted loading texts.
        """
        logger.info("Asker service dynamic text generation started")
        dynamic_loading_text_service = DynamicLoadingTextService(prompts.loading_text_generator_v1)
        dynamic_text_list = await dynamic_loading_text_service.generate_dynamic_loading_text(user_question)
        formatted_list = utils.format_str_to_sse(
            json.dumps(dynamic_text_list), constants.SseEventTypes.dynamic_loading_text
        )
        await queue.put(formatted_list)
        await queue.put(None)

    @staticmethod
    @handle_asyncio_producer_task_errors(-1, False)
    async def _produce_response(user_question: str, conversation_id: uuid, queue: asyncio.Queue):
        """Produces streamed AI response chunks and puts them into the queue as SSE events.

        Args:
            user_question (str): The user's question.
            conversation_id (uuid.UUID): Unique conversation ID.
            queue (asyncio.Queue): Queue to put SSE-formatted response chunks.
        """
        logger.info("Asker service stream_agent_response started")
        agent_service_model = AgentService(store_manager, prompts.responder_openai_v4_openai_template)
        agent_response_stream = await agent_service_model.stream_agent_response(user_question, conversation_id)
        async for chunk in agent_response_stream:
            sse_formatted_text = utils.format_str_to_sse(chunk, SseEventTypes.streamed_response)
            await queue.put(sse_formatted_text)
        await queue.put(None)


class AggregatedAgentResponseService:
    """Provides services to get the full, aggregated response from the underlying AI model.

    Optionally returns context too which is used for evaluation.
    """

    async def aggregated_agent_response(
        self, question: str, conversation_id: uuid, with_context: bool
    ) -> dict[str, Any]:
        """Generate a full answer (and optional context) for a question.

        Args:
            question (str): The user's question.
            conversation_id (uuid.UUID): ID for context lookup.
            with_context (bool): If True, include prior context (like tool run metadata).

        Returns:
            dict[str, Any]: {
                "generated_answer": str,
                "curr_context": Any  # only if with_context and exists
            }

        Raises:
            UsageLimitExceededError: When usage limits are reached.
            ResponseGenerationError: On generation errors.
        """
        response = await self._aggregate_agent_response(question, conversation_id)

        if with_context:
            nested_context: Optional[Any] = await self._get_conversation_context(conversation_id)
            if nested_context:
                response["curr_context"] = nested_context
        return response

    # noinspection PyMethodMayBeStatic
    async def _aggregate_agent_response(self, question: str, conversation_id: uuid) -> dict[str, Any]:
        """Helper method to convert the streamed agent response to an aggregated string.

        Args:
            question (str): The user's question.
            conversation_id (uuid.UUID): Unique conversation ID.

        Returns:
            dict[str, Any]: Aggregated response dictionary.
        """
        agent_service_model = AgentService(store_manager, prompts.responder_openai_v4_openai_template)
        parts: list[str] = []
        async for chunk in await agent_service_model.stream_agent_response(question, conversation_id):
            parts.append(chunk)
        full_response = "".join(parts)
        return {"generated_answer": full_response}

    # noinspection PyMethodMayBeStatic
    async def _get_conversation_context(self, conversation_id: uuid) -> list[dict[str, Any]]:
        """Retrieves conversation context from the store manager.

        Args:
            conversation_id (uuid.UUID): Unique conversation ID.

        Returns:
            list[dict[str, Any]]: List of context dictionaries.
        """
        return await store_manager.get_conversation_context(conversation_id)


class ConversationRetrieverService:
    """Provides services for retrieving conversations."""

    # noinspection PyMethodMayBeStatic
    async def get_conversation_by_id(self, conversation_id: uuid) -> Conversation:
        """Retrieves a conversation based on conversation_id.

        Returns:
            Conversation: Conversation object.

        Raises:
            HTTPException: Status 404 if no conversation with conversation_id.
        """
        return _find_conversation(conversation_id)

    # noinspection PyMethodMayBeStatic
    def find_conversations_by_feedback_created_since(self, feedback_within_hours: int) -> List[Conversation]:
        """Retrieves conversations which have feedback in last X hours.

        Returns:
            list[Conversation]: List of Conversation or empty list.
        """
        logger.info(f"Searching for conversations in last {feedback_within_hours} hours")
        utc_x_hours_ago = utils.calculate_utc_x_hours_ago(feedback_within_hours)
        return documentdb_client.find_conversations_by_created_since(utc_x_hours_ago)


class FeedbackManagerService:
    """Provides services to manage feedback."""

    # noinspection PyMethodMayBeStatic
    def create_feedback(self, conversation_id: uuid, vote: constants.VoteType, comment: str) -> None:
        """Creates Feedback object and attaches it to related conversation.

        Args:
            conversation_id (uuid.UUID): Unique conversation ID.
            vote (constants.VoteType): Vote type.
            comment (str): Feedback comment.
        """
        feedback = Feedback(vote=vote, comment=comment)
        conversation = _find_conversation(conversation_id)
        conversation.add_feedback(feedback)
        documentdb_client.update_conversation(conversation.conversation_id, conversation)
        logger.info(f"Added feedback {feedback.id} ({vote}) to conversation {conversation.conversation_id}")


def _find_conversation(conversation_id: uuid) -> Conversation:
    """Helper method to retrieve conversation from document db.

    Args:
        conversation_id (uuid.UUID): Unique conversation ID.

    Returns:
        Conversation: Conversation object.

    Raises:
        HTTPException: Status 404 if conversation is not found.
    """
    conversation = documentdb_client.find_conversation_by_id(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message_bundle.CONVERSATION_NOT_FOUND)
    return conversation
