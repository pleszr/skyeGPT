from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from apis.schemas.responses import CreateConversationIdResponse, ConversationResponse, ConversationListResponse
from apis.schemas.requests import CreateFeedbackRequest
from tests import test_constants, sample_objects
from apis.asker_apis import create_conversation, get_conversation_by_id, get_conversations_by_filter, create_feedback
from fastapi import HTTPException
from common import message_bundle


@pytest.mark.asyncio
@patch("apis.asker_apis.uuid.uuid4")
async def test_create_conversation_happy_path(mock_uuid4):
    mocked_generated_uuid = test_constants.sample_uuid
    mock_uuid4.return_value = mocked_generated_uuid

    response = await create_conversation()

    mock_uuid4.assert_called_once()

    assert isinstance(response, CreateConversationIdResponse), "Should be an instance of CreateConversationIdResponse"
    assert response.conversation_id == mocked_generated_uuid, "Response conversation_id does not match the mocked UUID"
    assert response.conversation_id == mocked_generated_uuid


@pytest.mark.asyncio
async def test_get_conversation_by_id_happy_path():
    # setup static data
    test_conv_id = sample_objects.sample_uuid

    # setup mocks
    expected_conversation = sample_objects.sample_conversation
    mock_retriever_service = MagicMock()
    mock_retriever_service.get_conversation_by_id = AsyncMock(return_value=expected_conversation)

    # act
    response = await get_conversation_by_id(
        conversation_id=test_conv_id, conversation_retriever_service=mock_retriever_service
    )

    # assert result
    assert isinstance(response, ConversationResponse), "Response should be an instance of ConversationResponse"
    assert response.conversation == sample_objects.sample_conversation

    # assert calls
    mock_retriever_service.get_conversation_by_id.assert_called_once_with(test_conv_id)


@pytest.mark.asyncio
async def test_get_conversation_by_id_not_found():
    not_existing_conv_id = sample_objects.sample_uuid

    mock_retriever_service = MagicMock()
    mock_retriever_service.get_conversation_by_id = AsyncMock(
        side_effect=HTTPException(status_code=404, detail=message_bundle.CONVERSATION_NOT_FOUND)
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_conversation_by_id(
            conversation_id=not_existing_conv_id, conversation_retriever_service=mock_retriever_service
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == message_bundle.CONVERSATION_NOT_FOUND
    mock_retriever_service.get_conversation_by_id.assert_called_once_with(not_existing_conv_id)


@pytest.mark.asyncio
async def test_get_conversations_by_filter_with_hours_happy_path():
    test_feedback_hours = 24
    expected_conversations_list = [sample_objects.sample_conversation, sample_objects.sample_conversation]

    mock_retriever_service = MagicMock()
    mock_retriever_service.find_conversations_by_feedback_created_since = MagicMock(
        return_value=expected_conversations_list
    )

    response = await get_conversations_by_filter(
        feedback_within_hours=test_feedback_hours, conversation_retriever_service=mock_retriever_service
    )

    mock_retriever_service.find_conversations_by_feedback_created_since.assert_called_once_with(test_feedback_hours)
    assert isinstance(response, ConversationListResponse), "Response should be an instance of ConversationListResponse"
    assert response.conversations == expected_conversations_list


@pytest.mark.asyncio
async def test_create_feedback_happy_path():
    test_conversation_id = sample_objects.sample_uuid
    test_feedback_request = CreateFeedbackRequest(vote="positive", comment="Great answer!")

    mock_feedback_service = MagicMock()
    mock_feedback_service.create_feedback = MagicMock()

    response = await create_feedback(
        request=test_feedback_request, conversation=test_conversation_id, feedback_service=mock_feedback_service
    )

    mock_feedback_service.create_feedback.assert_called_once_with(
        test_conversation_id, test_feedback_request.vote, test_feedback_request.comment
    )
    assert response.status_code == 201
