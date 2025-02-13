import markdown
from typing import Generator


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
