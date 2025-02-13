import chromadb
import uuid
from datetime import datetime
from typing import Mapping, List
from chromadb.errors import InvalidCollectionException
from DocumentationLinkGenerator import documentation_link_generator
import ImportFromS3


import Markdown2VectorDB

chroma_client = chromadb.PersistentClient()
chroma_settings_store = {}


def setup_chroma(
        collection_name: str,
        should_import: bool,
        folder_path: str,
        documentation_source,
        number_of_chroma_results: int,
        markdown_split_headers: List[str],
        gpt_model: str,
        gpt_temperature: float,
        gpt_developer_prompt: str,
        documentation_selector: dict[str, bool],
        s3_bucket: str,
        s3_folder_prefix: str,
        s3_local_folder: str
):
    save_settings_to_settings_store(
        number_of_chroma_results,
        gpt_model,
        gpt_temperature,
        gpt_developer_prompt
        )

    create_collection_if_needed(collection_name)

    if documentation_selector.get("s3") is True:
        ImportFromS3.download_files_from_s3_bucket(
            s3_bucket,
            s3_folder_prefix,
            s3_local_folder
        )

    if should_import:
        print("Import is enabled. Starting to import...")
        Markdown2VectorDB.scan_and_import_markdowns_from_folder(
            collection_name,
            folder_path,
            markdown_split_headers,
            documentation_source
        )
    else:
        print("Import is disabled. Proceeding...")
    number_of_documents = number_of_documents_in_collection(collection_name)
    print(f"Collection {collection_name} is ready to use. There are {number_of_documents} loaded to the collection.")
    return number_of_documents


def save_settings_to_settings_store(
        number_of_chroma_results: int,
        gpt_model: str,
        gpt_temperature: float,
        gpt_developer_prompt: str
):
    chroma_settings_store["number_of_chroma_results"] = number_of_chroma_results
    chroma_settings_store["gpt_model"] = gpt_model
    chroma_settings_store["gpt_temperature"] = gpt_temperature
    chroma_settings_store["gpt_developer_prompt"] = gpt_developer_prompt


def create_collection_if_needed(
        collection_name: str
):
    chroma_client.get_or_create_collection(collection_name,
                                           metadata={
                                               "description": "ChromaDB for GPT purposes",
                                               "created": str(datetime.now())
                                           })


def create_document_from_split_texts(
    collection_name: str,
    content_text_array: List[str],
    file_name: str,
    documentation_source: str
):

    for text in content_text_array:
        documentation_link = documentation_link_generator(
            file_name,
            documentation_source
        )
        add_document_to_collection(
            collection_name,
            text,
            {
                "file_name": file_name,
                "documentation_link": documentation_link
            }
        )
    number_of_documents = number_of_documents_in_collection(collection_name)
    print(f"Number of Documents: {number_of_documents}")


def number_of_documents_in_collection(collection_name: str):
    try:
        collection = chroma_client.get_collection(collection_name)
        return collection.count()
    except chromadb.errors.InvalidCollectionException:
        print(f"Collection with name {collection_name} not found. Returning 0 as number of documents")
        return 0


def get_collection_by_name(collection_name: str):
    try:
        return chroma_client.get_collection(name=collection_name)
    except chromadb.errors.InvalidCollectionException:
        print(f"Error: Collection with name {collection_name} not found.")
        return None


def add_document_to_collection(
        collection_name: str,
        document: str,
        metadata: Mapping[str, str]
):
    collection = get_collection_by_name(collection_name)
    document_uuid = uuid.uuid4()
    collection.add(
        documents=document,
        ids=str(document_uuid),
        metadatas=metadata
    )
    return document_uuid


def create_collection(collection_name: str):
    return chroma_client.create_collection(
        name=collection_name,
        metadata={
            "description": "ChromaDB for GPT purposes",
            "created": str(datetime.now())
        }
    )


def delete_collection(collection_name: str):
    chroma_client.delete_collection(name=collection_name)


def verify_if_collection_exists(
        collection_name: str
) -> bool:
    if get_collection_by_name(collection_name):
        return True
    else:
        return False


def set_chroma_client(
        client
):
    global chroma_client
    chroma_client = client

