import os
os.environ["OPENAI_API_KEY"] = "dummy-key"
from ChromaAsker import (send_question_to_gpt,
                         add_relevant_documents_to_message_history,
                         find_relevant_documents_for_question,
                         is_message_history_too_big,
                         ask_gpt_powered_by_chroma)
from unittest.mock import patch, MagicMock
import TestUtils
import ChromaSetup
import ChromaAsker
import copy


@patch("ChromaAsker.client.chat.completions.create")
@patch.dict(ChromaSetup.chroma_settings_store, {}, clear=True)
def test_send_question_to_gpt(mock_create):
    temperature = 0.1
    gpt_model = "test_gpt_model"
    ChromaSetup.chroma_settings_store["gpt_temperature"] = temperature
    ChromaSetup.chroma_settings_store["gpt_model"] = gpt_model
    message_history = [
            {"role": "user", "content": "msg_1"},
            {"role": "assistant", "content": "msg_2"}
        ]

    mock_create.return_value = TestUtils.mock_completions_chunk_generator(4)

    assistant_answer = send_question_to_gpt(message_history)

    token_id = 0
    for token in assistant_answer:
        assert token == f"chunk_{token_id}"
        token_id += 1

    mock_create.assert_called_once_with(
        temperature=temperature,
        model=gpt_model,
        messages=message_history,
        stream=True
    )


@patch.dict(ChromaSetup.chroma_settings_store, {}, clear=True)
def test_add_relevant_documents_to_message_history():
    ChromaSetup.chroma_settings_store["number_of_chroma_results"] = 3
    message_history = [
        {"role": "user", "content": "msg_1"},
        {"role": "assistant", "content": "msg_2"}
    ]
    copy_of_original_message_history = copy.deepcopy(message_history)

    relevant_documents = {
        "documents": [
            [
                "Document 1",
                "Document 2",
                "Document 3"
            ]
        ],
        "metadatas": [
            [
                {"documentation_link": "dummy_link1"},
                {"documentation_link": "dummy_link2"},
                {"documentation_link": "dummy_link3"}
            ]
        ]
    }

    actual_message_history = add_relevant_documents_to_message_history(
        relevant_documents,
        message_history
    )

    expected_message_history = [
        {"role": "user", "content": "msg_1"},
        {"role": "assistant", "content": "msg_2"},
        {"role": "developer", "content": "Relevant manual: Document 1. Documentation link: dummy_link1"},
        {"role": "developer", "content": "Relevant manual: Document 2. Documentation link: dummy_link2"},
        {"role": "developer", "content": "Relevant manual: Document 3. Documentation link: dummy_link3"},
    ]

    assert actual_message_history == expected_message_history

    assert message_history == copy_of_original_message_history


@patch("ChromaSetup.get_collection_by_name")
def test_find_relevant_documents_for_question(mock_get_collection_by_name):
    collection_name = "test_collection_name"
    query = "dummy query"
    number_of_results = 3

    mock_collection = MagicMock()
    mock_get_collection_by_name.return_value = mock_collection

    expected_relevant_documents = {
        "documents": [
            [
                "Document 1",
                "Document 2",
                "Document 3"
            ]
        ],
        "metadatas": [
            [
                {"documentation_link": "dummy_link1"},
                {"documentation_link": "dummy_link2"},
                {"documentation_link": "dummy_link3"}
            ]
        ]
    }

    mock_collection.query.return_value = expected_relevant_documents

    actual_relevant_documents = find_relevant_documents_for_question(
        collection_name,
        query,
        number_of_results
    )
    mock_collection.query.assert_called_once_with(query_texts=[query],
                                                  n_results=number_of_results)
    assert expected_relevant_documents == actual_relevant_documents


def test_is_message_history_too_big_yes():
    message_history = [
        {"role": "user", "content": "msg_1"},
        {"role": "assistant", "content": "msg_2"},
        {"role": "developer", "content": "Relevant manual: Document 1. Documentation link: dummy_link1"},
        {"role": "developer", "content": "Relevant manual: Document 2. Documentation link: dummy_link2"},
        {"role": "developer", "content": "Relevant manual: Document 3. Documentation link: dummy_link3"},
    ]

    max_prompt_size = 5
    assert is_message_history_too_big(message_history,
                                         max_prompt_size)


def test_is_message_history_too_big_no():
    message_history = [
        {"role": "user", "content": "msg_1"},
        {"role": "assistant", "content": "msg_2"},
    ]

    max_prompt_size = 5
    assert not is_message_history_too_big(message_history,
                                             max_prompt_size)


@patch.dict(ChromaAsker.conversation_store, {}, clear=True)  # Ensures isolated test state
@patch.dict(ChromaSetup.chroma_settings_store, {"gpt_developer_prompt": "Default Prompt"}, clear=True)
def test_load_conversation_from_store_or_generate_default_found():
    conversation_id = "existing_conversation"
    expected_conversation = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi, how can I help?"}
    ]

    ChromaAsker.conversation_store[conversation_id] = expected_conversation

    actual_conversation = ChromaAsker.load_conversation_from_store_or_generate_default(conversation_id)

    assert actual_conversation == expected_conversation


@patch.dict(ChromaAsker.conversation_store, {}, clear=True)  # Ensures isolated test state
@patch.dict(ChromaSetup.chroma_settings_store, {"gpt_developer_prompt": "Default Prompt"}, clear=True)
def test_load_conversation_from_store_or_generate_default_not_found():
    conversation_id = "missing_conversation"
    expected_default_conversation = [
        {"role": "developer", "content": "Default Prompt"}
    ]

    actual_conversation = ChromaAsker.load_conversation_from_store_or_generate_default(conversation_id)

    assert actual_conversation == expected_default_conversation


@patch("ChromaAsker.add_relevant_documents_to_message_history")
@patch("ChromaAsker.load_conversation_from_store_or_generate_default")
@patch("ChromaAsker.send_question_to_gpt")
@patch("ChromaAsker.find_relevant_documents_for_question")
@patch("ChromaAsker.is_message_history_is_too_big")
@patch.dict("ChromaAsker.conversation_store", {}, clear=True)
@patch.dict("ChromaSetup.chroma_settings_store", {
    "gpt_developer_prompt": "Default Prompt",
    "number_of_chroma_results": 3
}, clear=True)
def test_ask_gpt_powered_by_chroma_happy_path(
        mock_is_too_big,
        mock_find_documents,
        mock_send_question,
        mock_load_or_gen_def_conv,
        mock_add_to_message_history
):
    conversation_id = "test_conversation"
    question = "test question"

    initial_history = [{"role": "developer", "content": "Default Prompt"}]
    mock_load_or_gen_def_conv.return_value = initial_history

    mock_is_too_big.return_value = False

    mock_find_documents.return_value = {
        "documents": [["Doc1", "Doc2", "Doc3"]],
        "metadatas": [[
            {"documentation_link": "link1"},
            {"documentation_link": "link2"},
            {"documentation_link": "link3"}
        ]]
    }

    updated_history = [
        {"role": "developer", "content": "Default Prompt"},
        {"role": "developer", "content": "Relevant manual: Doc1. Documentation link: link1"},
        {"role": "developer", "content": "Relevant manual: Doc2. Documentation link: link2"},
        {"role": "developer", "content": "Relevant manual: Doc3. Documentation link: link3"}
    ]
    mock_add_to_message_history.return_value = updated_history

    mock_send_question.return_value = ["response", "_", "tokens"]

    response_generator = ask_gpt_powered_by_chroma(question,
                                                   conversation_id)
    assistant_response = list(response_generator)
    assert assistant_response == ["response", "_", "tokens"]

    expected_final_conversation = [
        {"role": "developer", "content": "Default Prompt"},
        {"role": "developer", "content": "Relevant manual: Doc1. Documentation link: link1"},
        {"role": "developer", "content": "Relevant manual: Doc2. Documentation link: link2"},
        {"role": "developer", "content": "Relevant manual: Doc3. Documentation link: link3"},
        {"role": "user", "content": "test question"},
        {"role": "assistant", "content": "response_tokens"}
    ]
    assert ChromaAsker.conversation_store[conversation_id] == expected_final_conversation

    mock_is_too_big.assert_called_once_with(initial_history,
                                            20)

    mock_find_documents.assert_called_once_with("SkyeDoc",
                                                question,
                                                3)
    expected_pre_gpt_msg_history = expected_final_conversation[:-1]
    mock_send_question.assert_called_once_with(expected_pre_gpt_msg_history)
