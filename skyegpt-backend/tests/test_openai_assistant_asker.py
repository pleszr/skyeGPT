# a module that has openai client fails when being imported if env variable not set
import os
os.environ["OPENAI_API_KEY"] = "dummy-key"
import pytest
from fastapi import HTTPException
import TestUtils
from unittest.mock import patch
from OpenAIAssistantAsker import run_assistant_on_thread, add_user_message_to_thread, ask_question
import OpenAIAssistantSetup


@patch("OpenAIAssistantAsker.client.beta.threads.runs.create")
def test_run_assistant_on_thread_success(mock_runs_create):
    thread_id = "test_thread_id"
    assistant_id = "test_assistant_id"

    mock_runs_create.return_value = TestUtils.mock_assistant_chunk_generator(
        3,
        "thread.message.delta"
    )

    assistant_answer = run_assistant_on_thread(
        thread_id,
        assistant_id
    )

    token_id = 0
    for token in assistant_answer:
        assert token == f"chunk_{token_id}"
        token_id += 1

    mock_runs_create.assert_called_once_with(
        thread_id=thread_id,
        assistant_id=assistant_id,
        stream=True
    )


@patch("OpenAIAssistantAsker.client.beta.threads.runs.create")
def test_run_assistant_on_thread_fail(mock_runs_create):
    thread_id = "test_thread_id"
    assistant_id = "test_assistant_id"

    mock_runs_create.return_value = TestUtils.mock_assistant_chunk_generator(
        4,
        "thread.run.failed"
    )

    with pytest.raises(HTTPException) as exception_info:
        assistant_answer = run_assistant_on_thread(thread_id,
                                                   assistant_id)
        for token in assistant_answer:
            pytest.fail()

    assert exception_info.value.status_code == 500

    mock_runs_create.assert_called_once_with(
        thread_id=thread_id,
        assistant_id=assistant_id,
        stream=True
    )


@patch("OpenAIAssistantAsker.client.beta.threads.messages.create")
def test_add_user_message_to_thread(mock_messages_create):
    thread_id = "test_thread_id"
    question = "dummy question"

    add_user_message_to_thread(thread_id,
                               question)

    mock_messages_create.assert_called_once_with(
        thread_id=thread_id,
        role="user",
        content=question
    )


@patch("OpenAIAssistantAsker.run_assistant_on_thread")
@patch("OpenAIAssistantAsker.add_user_message_to_thread")
def test_ask_question(mock_add_user_message_to_thread,
                      mock_run_assistant_on_thread):
    thread_id = "test_thread_id"
    question = "dummy question"
    test_assistant_id = "test_assistant_id"

    OpenAIAssistantSetup.assistant_settings_store = {"assistant_id": test_assistant_id}

    mock_run_assistant_on_thread.return_value = TestUtils.mock_token_generator(3)

    token_id = 0
    for token in ask_question(thread_id, question):
        assert token == f"token_{token_id}"
        token_id += 1

    mock_add_user_message_to_thread.assert_called_once_with(
        thread_id,
        question)
    mock_run_assistant_on_thread.assert_called_once_with(
        thread_id,
        test_assistant_id)
