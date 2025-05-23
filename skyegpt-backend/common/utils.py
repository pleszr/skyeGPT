"""Utility helpers for SkyeGPT."""
from typing import Generator, AsyncGenerator
from datetime import datetime, timezone, timedelta
import os
import re
from markdownify import markdownify
from . import constants
from common import message_bundle
from common.constants import SseEventTypes


def convert_html_to_md(html_content: str) -> str:
    """Convert HTML text to Markdown using markdownify."""
    return markdownify(html_content, heading_style="ATX")


def format_str_to_sse(input_string: str, event_type: SseEventTypes) -> str:
    """Format a single string to SSE format.
    Example: "event:dynamic_loading_text\ndata: yield1\n\n"."""
    output_string = input_string.replace("\n", "\\n")
    return f"event: {event_type.value}\ndata: {output_string}\n\n"


def replace_placeholders(template: str, values: dict[str, str]) -> str:
    """Replace {{placeholder}} tokens in *template* using values from *values*.
    Missing keys are substituted with the message bundle: 'VALUE_NOT_FOUND'

    Args:
        template: a text that contains placeholders within {{}}
        values: a dict that contains placeholder_key (without the {{}}) and the value it should be replaced to
    """
    def replacer(match):
        key = match.group(1).strip()
        return values.get(key, message_bundle.VALUE_NOT_FOUND)
    return re.sub(r'{{(.*?)}}', replacer, template)


def folder_to_dict(path):
    """Recursively walk *path* and return a nested dict describing the folder tree.

    Useful for lightweight JSON serialisation of directory structures.
    """
    tree = {"name": os.path.basename(path), "type": "folder", "children": []}
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                tree["children"].append(folder_to_dict(full_path))
            else:
                tree["children"].append({"name": entry, "type": "file"})
    except PermissionError:
        pass
    return tree


def generate_local_folder_path_from_skye_version(skye_major_version: str) -> str:
    """Render the configured docs folder path for a given Skye major version."""
    return replace_placeholders(
        constants.SKYE_DOC_LOCAL_FOLDER_LOCATION_TEMPLATE,
        {"skye_major_version": skye_major_version}
    )


def calculate_utc_x_hours_ago(x_hours: int) -> datetime:
    """Return the UTC datetime representing *x_hours* ago from now."""
    now_utc = datetime.now(timezone.utc)
    return now_utc - timedelta(hours=x_hours)
