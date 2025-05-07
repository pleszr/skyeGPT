import chromadb
from chromadb.errors import NotFoundError
from datetime import datetime
from common.exceptions import ResponseGenerationError
import os
from common.exceptions import CollectionNotFoundError

CHROMA_HOST = os.getenv('CHROMA_HOST', 'chroma')
CHROMA_PORT = os.getenv('CHROMA_PORT', 8000)

chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def create_collection_if_needed(collection_name: str):
    chroma_client.get_or_create_collection(
        collection_name,
        metadata={
            "description": "ChromaDB for GPT purposes",
            "created": str(datetime.now())
        }
    )


def number_of_documents_in_collection(collection_name: str):
    try:
        collection = chroma_client.get_collection(collection_name)
        return collection.count()
    except NotFoundError:
        print(f"Collection with name {collection_name} not found. Returning 0 as number of documents")
        return 0


def get_collection_by_name(collection_name: str):
    try:
        return chroma_client.get_collection(name=collection_name)
    except NotFoundError as e:
        print(f"Error: Collection with name {collection_name} not found.")
        raise CollectionNotFoundError from e


def create_collection(collection_name: str):
    return chroma_client.create_collection(
        name=collection_name,
        metadata={
            "description": "ChromaDB for GPT purposes",
            "created": str(datetime.now())
        }
    )


def delete_collection(collection_name: str):
    try:
        chroma_client.delete_collection(name=collection_name)
    except ValueError:
        raise ResponseGenerationError(f"Collection with name {collection_name} was not found")


def add_to_collection(
        collection,
        documents,
        metadatas,
        ids
):
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )


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

