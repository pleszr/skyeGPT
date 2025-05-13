import chromadb
from functools import wraps
from typing import Optional
from chromadb.errors import NotFoundError
from chromadb import Collection
from datetime import datetime
from common.exceptions import ResponseGenerationError
import os
from common.exceptions import CollectionNotFoundError

CHROMA_HOST = os.getenv('CHROMA_HOST', 'chroma')
CHROMA_PORT = os.getenv('CHROMA_PORT', 8000)

_chroma_client: Optional[chromadb.HttpClient]


def _init_client():
    """Create the real client only once."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _chroma_client


def ensure_client(func):
    """Lazy setup for client. Mainly to avoid side effect connections during testing."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        _init_client()
        return func(*args, **kwargs)
    return wrapper


@ensure_client
def create_collection_if_needed(collection_name: str) -> Collection:
    return _chroma_client.get_or_create_collection(
        collection_name,
        metadata={
            "description": "ChromaDB for GPT purposes",
            "created": str(datetime.now())
        }
    )


@ensure_client
def number_of_documents_in_collection(collection_name: str):
    try:
        collection = _chroma_client.get_collection(collection_name)
        return collection.count()
    except NotFoundError:
        print(f"Collection with name {collection_name} not found. Returning 0 as number of documents")
        return 0


@ensure_client
def get_collection_by_name(collection_name: str):
    try:
        return _chroma_client.get_collection(name=collection_name)
    except NotFoundError as e:
        print(f"Error: Collection with name {collection_name} not found.")
        raise CollectionNotFoundError from e


@ensure_client
def create_collection(collection_name: str):
    return _chroma_client.create_collection(
        name=collection_name,
        metadata={
            "description": "ChromaDB for GPT purposes",
            "created": str(datetime.now())
        }
    )


@ensure_client
def delete_collection(collection_name: str):
    try:
        _chroma_client.delete_collection(name=collection_name)
    except ValueError:
        raise ResponseGenerationError(f"Collection with name {collection_name} was not found")


@ensure_client
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


@ensure_client
def verify_if_collection_exists(
        collection_name: str
) -> bool:
    if get_collection_by_name(collection_name):
        return True
    else:
        return False


@ensure_client
def set_chroma_client(
        client
):
    global _chroma_client
    _chroma_client = client
