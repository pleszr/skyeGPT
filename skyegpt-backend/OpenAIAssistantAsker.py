from openai import OpenAI
import OpenAIAssistantSetup
import time
import Utils
from OpenAIAssistantSetup import assistant_settings_store


client = OpenAI()


def ask_question(
        thread_id: str,
        question: str
):
    add_user_message_to_thread(
        thread_id,
        question
    )

    run_assistant_on_thread(
        thread_id,
        OpenAIAssistantSetup.assistant_settings_store["assistant_id"]
    )

    return wait_and_extract_assistant_response(
        thread_id,
        assistant_settings_store["number_of_retries_for_assistant_answer"]
    )


def add_user_message_to_thread(
        thread_id: str,
        question: str
):
    client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=question,
    )


def run_assistant_on_thread(
        thread_id: str,
        assistant_id: str
):
    client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )


def wait_and_extract_assistant_response(
        thread_id: str,
        max_retries: int
):
    answer_md = ""
    for attempt in range(max_retries):
        thread_messages = client.beta.threads.messages.list(thread_id)
        role = thread_messages.data[0].role
        content = thread_messages.data[0].content
        if role == "assistant" and content:
            answer_md = thread_messages.data[0].content[0].text.value
            break
        else:
            print(f"No assistant response in {thread_id}, retrying in 1 sec")
            time.sleep(1)
    answer_html = Utils.convert_md_to_html(
        answer_md,
        "extra"
    )
    return answer_html
