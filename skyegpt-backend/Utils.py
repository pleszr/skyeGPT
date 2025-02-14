import markdown
from typing import Generator
import os
import json
import RagSetup
import OpenAIAssistantSetup


def convert_md_to_html(
        answer_md: str,
        extension: str
):
    return markdown.markdown(answer_md, extensions=[extension])


def format_to_sse(
        chunks: Generator[str, None, None]
) -> Generator[str, None, None]:
    for chunk in chunks:
        chunk = chunk.replace("\n", "\\n")
        yield f"data: {chunk}\n\n"


def save_settings_stores():
    save_settings_to_file(
        RagSetup.rag_settings_store,
        "chroma_settings_store.json"
    )
    save_settings_to_file(
        OpenAIAssistantSetup.assistant_settings_store,
        "assistant_settings_store.json"
    )


def load_settings_stores():
    try:
        RagSetup.rag_settings_store = load_settings_from_file("chroma_settings_store.json")
        print("Chroma settings loaded")
    except FileNotFoundError:
        print("chroma_settings_store.json is not present. Chroma settings not loaded")

    try:
        OpenAIAssistantSetup.assistant_settings_store = load_settings_from_file("assistant_settings_store.json")
        print("Assistant settings loaded")
    except FileNotFoundError:
        print("assistant_settings_store.json is not present. OpenAI Assistant settings not loaded")


def save_settings_to_file(
        my_dict: dict,
        json_name: str
):
    folder_path = "settings"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, json_name)

    with open(file_path, "w") as json_file:
        json.dump(my_dict, json_file, indent=4)
    print(f"{json_name} was saved successfully")


def load_settings_from_file(
        file_name: str
):
    folder_path = "settings"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "r") as f:
        loaded_dict = json.load(f)
    return loaded_dict
