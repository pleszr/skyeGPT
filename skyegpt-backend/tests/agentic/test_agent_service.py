import pytest
from unittest.mock import patch, AsyncMock, ANY
from dirty_equals import IsStr
from pydantic_ai.models.test import TestModel
from pydantic_ai.messages import UserPromptPart, ToolCallPart, ToolReturnPart, TextPart
from pydantic_ai import capture_run_messages
from agentic.agent_service import AgentService
from tests import sample_objects
from common import message_bundle


@pytest.fixture
def setup_test_environment(monkeypatch):
    """Setup environment variables and global state for agent tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "mock_openai_key")
    monkeypatch.setattr('pydantic_ai.models.ALLOW_MODEL_REQUESTS', False)
    yield


@pytest.fixture
def agent_service_instance():
    """Create an agent service with mocked dependencies."""
    sample_prompt_def = sample_objects.sample_agent_service_prompt
    mock_store_manager = AsyncMock()
    return AgentService(mock_store_manager, sample_prompt_def)


@pytest.mark.asyncio
@patch('agentic.agent_service.utils.replace_placeholders')
async def test_stream_agent_response_full_logic_happy_path(
        mock_replace,
        setup_test_environment,
        agent_service_instance
):

    # setup static data
    test_conversation_id = sample_objects.sample_uuid
    test_question = "Does Skye support SOAP?"
    sample_prompt_def = sample_objects.sample_agent_service_prompt

    # setup mocks
    mock_replace.return_value = test_question

    # act
    full_response = []
    with capture_run_messages() as messages:
        with agent_service_instance.agent.override(model=TestModel()):
            async for _ in await agent_service_instance.stream_agent_response(test_question, test_conversation_id):
                pass

    # assert results
    assert len(messages) == 4

    user_prompt_part = messages[0].parts[0]
    assert isinstance(user_prompt_part, UserPromptPart)
    assert user_prompt_part.content == test_question
    assert messages[0].instructions == sample_prompt_def.instructions

    tool_part_call = messages[1].parts[0]
    assert isinstance(tool_part_call, ToolCallPart)
    assert tool_part_call.tool_name == sample_prompt_def.tools[0].__name__
    tool_call_id = tool_part_call.tool_call_id

    tool_return_part = messages[2].parts[0]
    assert isinstance(tool_return_part, ToolReturnPart)
    assert tool_return_part.tool_name == sample_prompt_def.tools[0].__name__
    assert tool_return_part.content == message_bundle.CONTENT_ARCHIVED_MESSAGE
    assert tool_return_part.tool_call_id == tool_call_id

    text_part = messages[3].parts[0]
    assert isinstance(text_part, TextPart)
    assert messages[3].kind == "response"
    assert text_part.content == IsStr()

    # assert calls
    mock_replace.assert_called_once_with(ANY, {"user_question": test_question})

    store = agent_service_instance.store_manager
    store.get_conversation_by_id.assert_called_once_with(test_conversation_id)
    store.extend_conversation_history.assert_called_once_with(test_conversation_id, ANY)

