from typing import Generator, AsyncGenerator
from datetime import datetime, timezone, timedelta
import os
import re
from markdownify import markdownify as md
from . import constants


def convert_html_to_md(
        html_content: str
) -> str:
    return md(html_content, heading_style="ATX")


def format_to_sse(
        chunks: Generator[str, None, None]
) -> Generator[str, None, None]:
    for chunk in chunks:
        chunk = chunk.replace("\n", "\\n")
        yield f"data: {chunk}\n\n"


async def async_format_to_sse(
        chunks: AsyncGenerator[str, None]
) -> AsyncGenerator[str, None]:
    async for chunk in chunks:
        chunk = chunk.replace("\n", "\\n")
        yield f"data: {chunk}\n\n"


def replace_placeholders(template: str, values: dict[str, str]) -> str:
    def replacer(match):
        key = match.group(1).strip()
        return values.get(key, 'VALUE NOT FOUND')
    return re.sub(r'{{(.*?)}}', replacer, template)


def folder_to_dict(path):
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
    return replace_placeholders(
        constants.SKYE_DOC_LOCAL_FOLDER_LOCATION_TEMPLATE,
        {"skye_major_version": skye_major_version}
    )


def calculate_utc_x_hours_ago(x_hours: int) -> datetime:
    now_utc = datetime.now(timezone.utc)
    return now_utc - timedelta(hours=x_hours)
