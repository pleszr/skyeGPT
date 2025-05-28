import pytest
from unittest.mock import patch
from agentic.dynamic_loading_text_service import DynamicLoadingTextService
from pydantic_ai.models.test import TestModel
from pydantic_ai.messages import UserPromptPart, SystemPromptPart
from pydantic_ai import capture_run_messages
from tests import sample_objects


@pytest.fixture
def setup_test_environment(monkeypatch):
    """Setup environment variables and global state for agent tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "mock_openai_key")
    monkeypatch.setattr("pydantic_ai.models.ALLOW_MODEL_REQUESTS", False)
    yield


@pytest.fixture
def loading_text_service_instance():
    """Create a loading text service with mocked dependencies."""
    sample_prompt_def = sample_objects.sample_loading_text_prompt
    return DynamicLoadingTextService(sample_prompt_def)


@pytest.mark.asyncio
@patch("agentic.agent_service.utils.replace_placeholders")
async def test_generate_dynamic_loading_text_happy_path(
    mock_replace,
    setup_test_environment,
    loading_text_service_instance,
):
    """Test successful generation of dynamic loading text."""
    # setup static data
    test_question = "What is machine learning?"
    sample_prompt_def = sample_objects.sample_loading_text_prompt

    # setup mocks
    mock_replace.return_value = test_question

    # act
    with capture_run_messages() as messages:
        with loading_text_service_instance.agent.override(model=TestModel()):
            result = await loading_text_service_instance.generate_dynamic_loading_text(test_question)
    print(f"messages: {messages}")
    print(f"result: {result}")

    # assert
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)

    # assert system prompt
    system_prompt_part = messages[0].parts[0]
    assert isinstance(system_prompt_part, SystemPromptPart)
    assert system_prompt_part.content == sample_prompt_def.system_prompt

    # assert user prompt
    user_prompt_part = messages[0].parts[1]
    assert isinstance(user_prompt_part, UserPromptPart)
    assert user_prompt_part.content == test_question
