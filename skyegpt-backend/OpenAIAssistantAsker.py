from openai import OpenAI
import OpenAIAssistantSetup
from typing import Generator
from fastapi import HTTPException

client = OpenAI()


def ask_question(
        thread_id: str,
        question: str
):
    add_user_message_to_thread(
        thread_id,
        question
    )

    assistant_answer = run_assistant_on_thread(
        thread_id,
        OpenAIAssistantSetup.assistant_settings_store["assistant_id"]
    )

    for chunk in assistant_answer:
        if chunk is not None:
            yield chunk


def add_user_message_to_thread(
        thread_id: str,
        question: str
):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question,
    )


def run_assistant_on_thread(
        thread_id: str,
        assistant_id: str
) -> Generator[str, None, None]:

    stream = client.beta.threads.runs.create(thread_id=thread_id,
                                             assistant_id=assistant_id,
                                             stream=True)

    for chunk in stream:
        if chunk.event == "thread.message.delta":
            if hasattr(chunk.data.delta, 'content') and chunk.data.delta.content:
                token = chunk.data.delta.content[0].text.value
                if token is not None:
                    yield token

        elif chunk.event == "thread.run.failed":
            print(f"Error while running the thread. Chunk: {chunk}")
            raise HTTPException(status_code=500, detail="Error while running the thread")

        else:
            print(f"Event happened: {chunk.event}")
