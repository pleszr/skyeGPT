from unittest.mock import patch, MagicMock, AsyncMock, ANY
from services.asker_services import (AgentResponseStreamingService, AggregatedAgentResponseService,
                                     ConversationRetrieverService, FeedbackManagerService)
import pytest
from tests import sample_objects
from fastapi import HTTPException, status


@pytest.mark.asyncio
@patch('services.asker_services.store_manager')
@patch(
    'services.asker_services.utils.format_str_to_sse',
    side_effect=lambda s, e: f"event: {e.value}\ndata: {s}\n\n"
)
@patch('services.asker_services.AgentService')
@patch('services.asker_services.DynamicLoadingTextService')
async def test_agent_response_streaming_service_stream_agent_response_happy_path(
        mock_dynamic_loading_text_class,
        mock_agent_service_class,
        mock_format_str_to_sse,
        mock_store_manager
):
    # setup static data
    service = AgentResponseStreamingService ()
    user_question = "What is Skye?"
    expected_loading_texts = ["Searching in Skye doc1", "Searching in Skye doc2"]
    test_conversation_id = sample_objects.sample_uuid

    # setup DynamicLoadingText mocks mocks
    mock_loading_text_instance = MagicMock()
    mock_dynamic_loading_text_class.return_value = mock_loading_text_instance
    mock_loading_text_instance.generate_dynamic_loading_text = AsyncMock(return_value=expected_loading_texts)

    # setup AgentService mocks
    mock_agent_service_instance = MagicMock()
    mock_agent_service_class.return_value = mock_agent_service_instance
    mock_agent_service_instance.stream_agent_response = AsyncMock(side_effect=sample_objects.raw_response_stream)

    # act
    result_chunks = []
    async for chunk in service.stream_agent_response(user_question, test_conversation_id):
        result_chunks.append(chunk)

    # assert result
    assert sample_objects.expected_stream_outcome == result_chunks

    # assert agent_service calls
    mock_agent_service_class.assert_called_once_with(mock_store_manager, ANY)
    mock_agent_service_instance.stream_agent_response.assert_called_once_with(user_question, test_conversation_id)
    assert mock_format_str_to_sse.called

    # assert dynamic loading text calls
    mock_dynamic_loading_text_class.assert_called_once_with(ANY)
    mock_loading_text_instance.generate_dynamic_loading_text.assert_called_once_with(user_question)


@pytest.mark.asyncio
@patch('services.asker_services.store_manager')
@patch('services.asker_services.AgentService')
async def test_aggregated_agent_response_with_context_happy_path(
        mock_agent_service_class,
        mock_store_manager
):
    # setup static data
    service = AggregatedAgentResponseService()
    user_question = "What's the meaning of life?"
    test_conversation_id = sample_objects.sample_uuid
    test_with_context = True

    # setup mocks
    agent_service_instance = MagicMock()
    agent_service_instance.stream_agent_response = AsyncMock(side_effect=sample_objects.raw_response_stream)
    mock_agent_service_class.return_value = agent_service_instance

    expected_context = [{"turn": 1, "text": "hello"}]
    mock_store_manager.get_conversation_context = AsyncMock(return_value=expected_context)

    #act
    result = await service.aggregated_agent_response(
        question=user_question,
        conversation_id=test_conversation_id,
        with_context=test_with_context
    )

    #assert results
    assert result["generated_answer"] == "".join(sample_objects.mock_raw_chunks)
    assert result["curr_context"] == expected_context

    #assert calls
    mock_agent_service_class.assert_called_once_with(mock_store_manager,ANY)
    agent_service_instance.stream_agent_response.assert_called_once_with(user_question, test_conversation_id)
    mock_store_manager.get_conversation_context.assert_called_once_with(test_conversation_id)


@pytest.mark.asyncio
@patch('services.asker_services.documentdb_client')
async def test_get_conversation_by_id_happy_path(mock_documentdb_client):
    # setup static data
    service = ConversationRetrieverService()
    test_conversation_id = sample_objects.sample_uuid
    expected_conversation = sample_objects.sample_conversation

    # setup mocks
    mock_documentdb_client.find_conversation_by_id.return_value = expected_conversation

    # act
    result = await service.get_conversation_by_id(test_conversation_id)

    # assert result
    assert result == expected_conversation

    # assert calls
    mock_documentdb_client.find_conversation_by_id.assert_called_once_with(test_conversation_id)


@pytest.mark.asyncio
@patch('services.asker_services.documentdb_client')
@patch('services.asker_services.message_bundle')
async def test_get_conversation_by_id_not_found_raises_http_exception(
        mock_message_bundle,
        mock_documentdb_client
):
    # setup static data
    service = ConversationRetrieverService()
    test_conversation_id = sample_objects.sample_uuid

    # setup mocks
    mock_documentdb_client.find_conversation_by_id.return_value = None
    mock_message_bundle.CONVERSATION_NOT_FOUND = "Conversation not found"

    # act
    with pytest.raises(HTTPException) as exc_info:
        await service.get_conversation_by_id(test_conversation_id)

    # verify result
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == mock_message_bundle.CONVERSATION_NOT_FOUND

    # assert calls
    mock_documentdb_client.find_conversation_by_id.assert_called_once_with(test_conversation_id)


@pytest.mark.asyncio
@patch('services.asker_services.utils.calculate_utc_x_hours_ago')
@patch('services.asker_services.documentdb_client')
async def test_find_conversations_by_feedback_created_since_happy_path(
        mock_documentdb_client,
        mock_calculate_utc
):
    # setup static data
    service = ConversationRetrieverService()
    feedback_hours = 5

    # setup mocks
    mock_time = MagicMock()
    mock_calculate_utc.return_value = mock_time

    expected_list = [sample_objects.sample_conversation, sample_objects.sample_conversation]
    mock_documentdb_client.find_conversations_by_created_since.return_value = expected_list

    # act
    result = service.find_conversations_by_feedback_created_since(feedback_hours)

    # assert
    assert result == expected_list

    # assert calls
    mock_documentdb_client.find_conversations_by_created_since.assert_called_once_with(mock_time)


@pytest.mark.asyncio
@patch('services.asker_services.utils.calculate_utc_x_hours_ago')
@patch('services.asker_services.documentdb_client')
async def test_find_conversations_by_feedback_created_since_returns_empty_list(
        mock_documentdb_client,
        mock_calculate_utc
):
    # setup static data
    service = ConversationRetrieverService()
    feedback_hours = 1

    # setup mocks
    mock_time = MagicMock()
    mock_calculate_utc.return_value = mock_time
    mock_documentdb_client.find_conversations_by_created_since.return_value = []

    # act
    result = service.find_conversations_by_feedback_created_since(feedback_hours)

    # assert result
    assert result == []

    # assert calls
    mock_documentdb_client.find_conversations_by_created_since.assert_called_once_with(mock_time)


@patch('services.asker_services._find_conversation')
@patch('services.asker_services.documentdb_client')
def test_create_feedback_happy_path(
        mock_documentdb_client,
        mock_find_conversation
):
    # setup static data
    service = FeedbackManagerService()
    conversation_id = sample_objects.sample_uuid
    vote = 'positive'
    comment = "Great answer"

    # setup mocks
    conversation = sample_objects.sample_conversation
    initial_len = len(conversation.feedbacks)
    mock_find_conversation.return_value = conversation

    # act
    service.create_feedback(conversation_id=conversation_id, vote=vote, comment=comment)

    # assert result
    assert len(conversation.feedbacks) == initial_len + 1
    new_feedback = conversation.feedbacks[-1]
    assert new_feedback.vote == vote
    assert new_feedback.comment == comment

    # assert calls
    mock_documentdb_client.update_conversation.assert_called_once_with(conversation_id, conversation)