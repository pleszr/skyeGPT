from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from apis.schemas.responses import AgentResponse
from apis. schemas.requests import ConversationQueryRequest
from tests import test_constants, sample_objects
from apis.evaluator_apis import generate_agent_response_with_context


@pytest.mark.asyncio
async def test_generate_agent_response_with_context_happy_path():
    test_conversation_id = sample_objects.sample_uuid
    test_query = "What is the meaning of life?"
    test_request = ConversationQueryRequest(conversation_id=test_conversation_id, query=test_query)

    expected_generated_answer = "42"
    expected_context = {"source": "hitchhiker's guide"}
    expected_response_dict = {
        "generated_answer": expected_generated_answer,
        "curr_context": expected_context
    }

    mock_agent_response_service = MagicMock()
    mock_agent_response_service.aggregated_agent_response = AsyncMock(return_value=expected_response_dict)

    response = await generate_agent_response_with_context(
        request=test_request,
        agent_response_service=mock_agent_response_service
    )

    mock_agent_response_service.aggregated_agent_response.assert_called_once_with(
        test_query,
        test_conversation_id,
        True
    )
    assert isinstance(response, AgentResponse), "Response should be an instance of AgentResponse"
    assert response.generated_answer == expected_generated_answer
    assert response.curr_context == expected_context