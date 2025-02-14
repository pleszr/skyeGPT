import markdown
from typing import Generator
import os
import json


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


def save_settings_to_file(
        my_dict: dict,
        json_name: str
):
    folder_path = "settings"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, json_name)

    with open(file_path, "w") as json_file:
        json.dump(my_dict, json_file, indent=4)


def load_settings_from_file(
        file_name: str
):
    folder_path = "settings"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "r") as f:
        loaded_dict = json.load(f)
    return loaded_dict
