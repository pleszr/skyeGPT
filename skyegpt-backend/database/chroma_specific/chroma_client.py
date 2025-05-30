"""HTTP-based ChromaDB client wrappers for managing collections and queries."""

import chromadb
from functools import wraps
from typing import Optional
from chromadb.errors import NotFoundError
from chromadb import Collection, QueryResult
from datetime import datetime
from common.exceptions import ResponseGenerationError, CollectionNotFoundError
import os

CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = os.getenv("CHROMA_PORT", 8000)

_chroma_client: Optional[chromadb.HttpClient] = None


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
    """Get or create a ChromaDB collection by name."""
    return _chroma_client.get_or_create_collection(
        collection_name, metadata={"description": "ChromaDB for GPT purposes", "created": str(datetime.now())}
    )


@ensure_client
def number_of_documents_in_collection(collection_name: str):
    """Return the number of documents in the specified collection."""
    try:
        collection = _chroma_client.get_collection(collection_name)
        return collection.count()
    except NotFoundError:
        print(f"Collection with name {collection_name} not found. Returning 0 as number of documents")
        return 0


@ensure_client
def get_collection_by_name(collection_name: str):
    """Retrieve a collection by name, or raise CollectionNotFoundError if not found."""
    try:
        return _chroma_client.get_collection(name=collection_name)
    except NotFoundError as e:
        print(f"Error: Collection with name {collection_name} not found.")
        raise CollectionNotFoundError from e


@ensure_client
def create_collection(collection_name: str):
    """Create a new collection with the given name."""
    return _chroma_client.create_collection(
        name=collection_name, metadata={"description": "ChromaDB for GPT purposes", "created": str(datetime.now())}
    )


@ensure_client
def delete_collection(collection_name: str):
    """Delete the collection with the specified name."""
    try:
        _chroma_client.delete_collection(name=collection_name)
    except ValueError as e:
        raise ResponseGenerationError(f"Collection with name {collection_name} was not found") from e


@ensure_client
def find_k_nearest_neighbour(collection: Collection, query: str, k: int) -> QueryResult:
    """Find the k nearest neighbours in the collection for the given query."""
    results = collection.query(query_texts=[query], n_results=k)
    return results


@ensure_client
def add_to_collection(collection, documents, metadatas, ids):
    """Add documents with metadata and ids to the specified collection."""
    collection.add(documents=documents, metadatas=metadatas, ids=ids)


@ensure_client
def verify_if_collection_exists(collection_name: str) -> bool:
    """Check if a collection with the given name exists."""
    if get_collection_by_name(collection_name):
        return True
    else:
        return False
