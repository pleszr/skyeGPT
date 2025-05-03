from langchain_text_splitters import MarkdownHeaderTextSplitter
from pathlib import Path
from typing import List
from retriever import db_client
import uuid
import os
import time
import multiprocessing as mp
from ..utils.process_wrapper import create_process, start_process, join_process
from ..utils import documentation_link_generator


def scan_and_import_markdowns_from_folder(
        collection_name: str,
        folder_path: str,
        markdown_split_headers: List[str]
) -> None :
    db_client.create_collection_if_needed(collection_name)

    batch_size = int(os.getenv("RAG_BATCH_SIZE"))
    queue = mp.Queue()

    producer_process = create_process(target=_chroma_import_producer, args=(
        folder_path,
        markdown_split_headers,
        batch_size,
        queue
    ))

    consumer_process = create_process(target=_chroma_import_consumer, args=(
        collection_name,
        queue
    ))

    start_time = time.time()
    start_process(producer_process)
    start_process(consumer_process)

    join_process(producer_process)
    queue.put(None)

    join_process(consumer_process)

    number_of_documents = db_client.number_of_documents_in_collection(collection_name)
    print(f"Elapsed seconds: {time.time()-start_time:.0f} Record count: {number_of_documents}")


def _chroma_import_producer(
        folder_path: str,
        markdown_split_headers: List[str],
        batch_size: int,
        queue
):
    folder = Path(folder_path)
    for file in folder.rglob("*.md"):
        with open(file, "r", encoding="utf-8") as opened_file:
            documentation_source = documentation_link_generator.select_doc_source_by_folder_path(file)

            file_content = opened_file.read()
            texts = _split_markdown_by_headers(
                file_content,
                markdown_split_headers
            )

            _add_text_to_queue(
                texts,
                Path(file.name).stem,
                documentation_source,
                batch_size,
                queue
            )


def _split_markdown_by_headers(
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
    documents = markdown_splitter.split_text(file_content)
    document_contents = [document.page_content for document in documents]
    return document_contents


def _add_text_to_queue(
        content_text_array: List[str],
        file_name: str,
        documentation_source: str,
        batch_size: int,
        queue
):
    documents = []
    metadatas = []
    ids = []

    for text in content_text_array:
        documentation_link = documentation_link_generator.link_generator(
            file_name,
            documentation_source
        )
        metadata = {
            "file_name": file_name,
            "documentation_link": documentation_link
        }

        ids.append(str(uuid.uuid4()))
        documents.append(text)
        metadatas.append(metadata)

        if len(ids) >= batch_size:
            queue.put({
                "documents": documents,
                "metadatas": metadatas,
                "ids": ids
                })
            documents = []
            metadatas = []
            ids = []

    if len(ids) > 0:
        queue.put({
            "documents": documents,
            "metadatas": metadatas,
            "ids": ids
        })


def _chroma_import_consumer(
        collection_name,
        queue
):
    collection = db_client.get_collection_by_name(collection_name)
    batch_number = 0
    while True:
        batch_number += 1
        batch = queue.get()
        if batch is None:
            break

        documents = batch["documents"]
        metadatas = batch["metadatas"]
        ids = batch["ids"]
        print(f"Saving batch: {batch_number} with {len(ids)} documents")
        db_client.add_to_collection(
            collection,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
