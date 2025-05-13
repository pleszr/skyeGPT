from common.exceptions import VectorDBError, CollectionNotFoundError
from common import logger
from chromadb.errors import ChromaError
from functools import wraps
from .chroma_specific import chroma_client
from typing import List, Mapping, Union


def convert_chroma_error_to_vectordb_error(func):
    """Decorator to catch ChromaDB's specific ChromaError and re-raise it as a domain-specific VectorDBError.
    Raises:
        VectorDBError: Wrapping the original ChromaError.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChromaError as e:
            raise VectorDBError(e.message()) from e
    return wrapper


@convert_chroma_error_to_vectordb_error
def create_collection_if_needed(collection_name: str) -> None:
    """Creates a collection if needed.

    Raises:
        VectorDBError for database related errors
    """
    chroma_client.create_collection_if_needed(collection_name)


@convert_chroma_error_to_vectordb_error
def number_of_documents_in_collection(collection_name: str) -> int:
    """Counts the number of documents in a collection.

    Raises:
        VectorDBError: for database related errors
        CollectionNotFoundError: if collection is not found
    """
    try:
        return chroma_client.number_of_documents_in_collection(collection_name)
    except ValueError as e:
        _handle_value_error(collection_name, e)


@convert_chroma_error_to_vectordb_error
def create_collection(collection_name: str) -> None:
    """Creates a new collection in VectorDB

    Raises:
        VectorDBError: for database related errors
    """
    return chroma_client.create_collection(collection_name)


@convert_chroma_error_to_vectordb_error
def delete_collection(collection_name: str) -> None:
    """Deletes collection identified by name.

    Raises:
        VectorDBError: for database related errors
        CollectionNotFoundError: if collection is not found
    """
    try:
        chroma_client.delete_collection(collection_name)
    except ValueError as e:
        _handle_value_error(collection_name, e)


@convert_chroma_error_to_vectordb_error
def add_to_collection(
        collection_name: str,
        documents: List[str],
        metadatas: List[Mapping[str, Union[str, int, float, bool]]],
        ids: List[str]
) -> None:
    """Adds a document to the collection identified by name.

    Args:
        collection_name: name of the collection
        ids: The ids of the embeddings you wish to add
        metadatas: The metadata to associate with the embeddings. When querying, you can filter on this metadata.
        documents: The documents to associate with the embeddings.
    Raises:
        VectorDBError: for database related errors
        CollectionNotFoundError: if collection is not found
    """
    try:
        collection = chroma_client.get_collection_by_name(collection_name)
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
    except ValueError as e:
        _handle_value_error(collection_name, e)


def _handle_value_error(collection_name: str, e: ValueError):
    """Chroma returns ValueError when a collection is not found. This helper method catches it
    and raises SkyeGPT-specific CollectionNotFoundError"""
    error_message = f'Collection {collection_name} not found'
    logger.error(error_message)
    raise CollectionNotFoundError(error_message) from e
