from types import SimpleNamespace
from typing import List


def mock_assistant_chunk_generator(number_of_chunks: int, type_of_event: str):
    for x in range(number_of_chunks):
        chunk = SimpleNamespace(
            event=type_of_event,
            data=SimpleNamespace(
                delta=SimpleNamespace(content=[SimpleNamespace(text=SimpleNamespace(value=f"chunk_{x}"))])
            ),
        )
        yield chunk


def mock_token_generator(number_of_chunks: int):
    for x in range(number_of_chunks):
        yield f"token_{x}"


def mock_completions_chunk_generator(number_of_chunks: int):
    for x in range(number_of_chunks):
        chunk = SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=f"chunk_{x}"))])
        yield chunk


def convert_array_to_see(chunks: List[str]):
    formatted_list = []
    for chunk in chunks:
        formatted_chunk = f"data: {chunk}\n\n"
        formatted_list.append(formatted_chunk)
    return formatted_list


def _sort_tree(node: dict) -> dict:
    """Return a copy of *node* with its 'children' list recursively sorted.

    Folders come first (A-Z) and files second (A-Z).
    """
    if node.get("type") == "folder":
        # sort each child, then sort the list itself
        node = {**node, "children": [_sort_tree(c) for c in node["children"]]}
        node["children"].sort(key=lambda c: (c["type"] != "folder", c["name"]))
    return node
