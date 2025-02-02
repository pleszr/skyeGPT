from langchain_text_splitters import MarkdownHeaderTextSplitter
from pathlib import Path
from typing import List
import ChromaSetup


def scan_and_import_markdowns_from_folder(
        collection_name: str,
        folder_path: str,
        markdown_split_headers: List[str],
        documentation_source: str
):
    folder = Path(folder_path)
    for file in folder.rglob("*.md"):
        print(f"Found markdown file: {file}")

        with open(file, "r", encoding="utf-8") as opened_file:
            file_content = opened_file.read()

        import_file_to_document(
            collection_name,
            markdown_split_headers,
            Path(file.name).stem,
            file_content,
            documentation_source
        )


def import_file_to_document(
        collection_name: str,
        markdown_split_headers: List[str],
        file_name: str,
        file_content: str,
        documentation_source
):

    markdown_header_splits_array = split_markdown_to_header_texts(
        file_content,
        markdown_split_headers
    )

    ChromaSetup.create_document_from_split_texts(
        collection_name,
        markdown_header_splits_array,
        file_name,
        documentation_source
    )


def split_markdown_to_header_texts(
        file_content: str,
        markdown_split_headers: List[str]
):

    split_levels_list = []
    if "#" in markdown_split_headers:
        split_levels_list.append(("#", "Header 1"))
    if "##" in markdown_split_headers:
        split_levels_list.append(("##", "Header 2"))
    if "###" in markdown_split_headers:
        split_levels_list.append(("###", "Header 3"))

    markdown_splitter = MarkdownHeaderTextSplitter(split_levels_list, strip_headers=False)
    documents_array = markdown_splitter.split_text(file_content)
    string_array = [document.page_content for document in documents_array]
    return string_array



