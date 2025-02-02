import chromadb
import ChromaSetup
from openai import OpenAI
from typing import List, Dict

import Utils

client = OpenAI()
chroma_client = chromadb.PersistentClient()
conversation_store = {}


def ask_gpt_powered_by_chroma(
        question: str,
        conversation_id: str
):

    message_history = load_conversation_from_store_or_generate_default(
        conversation_id
    )

    message_history_is_too_big = verify_if_message_history_is_too_big(
        message_history,
        20
    )
    if message_history_is_too_big:
        return "Message history limit reached. Reload the page"

    relevant_documents = find_relevant_documents_for_question(
        "SkyeDoc",
        question,
        ChromaSetup.chroma_settings_store["number_of_chroma_results"]
    )
    message_history = add_relevant_documents_to_message_history(
        relevant_documents,
        message_history
    )

    message_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    assistant_answer = send_question_to_gpt(
        message_history
    )

    message_history.append(
        {
            "role": "assistant",
            "content": assistant_answer
        }
    )

    conversation_store[conversation_id] = message_history
    return Utils.convert_md_to_html(
        assistant_answer,
        "extra")


def load_conversation_from_store_or_generate_default(
        conversation_id: str
):
    default_message = [
            {
                "role": "developer",
                "content": ChromaSetup.chroma_settings_store["gpt_developer_prompt"]
            }
        ]

    return conversation_store.get(
        conversation_id,
        default_message)


def verify_if_message_history_is_too_big(
        message_history: List[Dict[str, str]],
        max_prompt_size: int
) -> bool:
    message_history_size = len(message_history)
    if message_history_size >= max_prompt_size:
        return True
    else:
        return False


def find_relevant_documents_for_question(
        collection_name: str,
        query: str,
        number_of_results: int
) -> dict:
    collection = ChromaSetup.get_collection_by_name(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=number_of_results
    )
    return results


def add_relevant_documents_to_message_history(
        relevant_documents: dict,
        message_history: List[Dict[str, str]]
):
    updated_message_history = message_history[:]

    for document_index in range(0, ChromaSetup.chroma_settings_store["number_of_chroma_results"]):
        relevant_document = relevant_documents["documents"][0][document_index]
        relevant_link = relevant_documents["metadatas"][0][document_index]["documentation_link"]

        updated_message_history.append(
            {
                "role": "developer",
                "content": str(f"This the first manual: {relevant_document} Metadata: {relevant_link}")
            }
        )
    return updated_message_history


def send_question_to_gpt(
        message_history: List[Dict[str, str]]
) -> str:
    completion = client.chat.completions.create(
        temperature=ChromaSetup.chroma_settings_store["gpt_temperature"],
        model=ChromaSetup.chroma_settings_store["gpt_model"],
        messages=message_history
    )
    return completion.choices[0].message.content
