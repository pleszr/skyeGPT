import os
from functools import wraps
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any, List, Optional
import uuid
from common.exceptions import ObjectNotFoundError

MONGO_USERNAME = os.getenv("MONGO_USERNAME", "skyegpt-admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "TODO")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo:27017")

CONNECTION_STRING = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/?authSource=admin"

_mongo_client: Optional[MongoClient] = None


def _init_client():
    """Create the real client only once."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(CONNECTION_STRING, uuidRepresentation='standard')
    return _mongo_client


def ensure_client(func):
    """Lazy setup for client. Mainly to avoid side effect connections during testing."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        _init_client()
        return func(*args, **kwargs)
    return wrapper


@ensure_client
def get_database(database_name: str):
    """
    Retrieves a database instance from the MongoDB client.
    
    Returns:
        Database: A PyMongo Database object.
    Raises:
        an instance PyMongoError for operational errors
    """
    return _mongo_client[database_name]


@ensure_client
def create_or_get_collection(database_name: str, collection_name: str) -> Collection:
    """
    Retrieves a collection from the specified database. Creates the collection if it does not exist.

    Returns:
        Collection: A PyMongo Collection object.
    Raises:
        an instance PyMongoError for operational errors
    """
    database = get_database(database_name)
    return database[collection_name]


@ensure_client
def add_to_collection(collection: Collection, document: Dict[str, Any]) -> None:
    """
    Inserts a single document into the specified collection.

    Args:
        collection (Collection): The MongoDB collection.
        document (Dict[str, Any]): The document to insert.
        
    Raises:
        an instance PyMongoError for operational errors
    """
    collection.insert_one(document)


@ensure_client
def upsert_to_collection(collection: Collection, _id: uuid, document: Dict[str, Any]) -> None:
    """
    Replaces a document in the collection if it exists, otherwise inserts it.

    Args:
        collection (Collection): The MongoDB collection.
        _id (uuid): The unique identifier of the document.
        document (Dict[str, Any]): The document to upsert.
    Raises:
        an instance PyMongoError for operational errors
    """
    collection.replace_one({"_id": _id}, document, upsert=True)


@ensure_client
def find_one_by_id(collection: Collection, _id: uuid):
    """
    Finds a single document in the collection by its _id field.

    Args:
        collection (Collection): The MongoDB collection.
        _id (uuid): The unique identifier of the document.

    Returns:
        dict or None: The document if found, else None.
    Raises:
        an instance PyMongoError for operational errors
    """
    return collection.find_one({"_id": _id})


@ensure_client
def replace_one_by_id(collection: Collection, _id: uuid, document: Dict[str, Any]):
    """
    Replaces an existing document in the collection by its _id. Raises an error if not found.

    Args:
        collection (Collection): The MongoDB collection.
        _id (uuid): The unique identifier of the document.
        document (Dict[str, Any]): The document to replace with.

    Raises:
        ObjectNotFoundError: If no document with the given _id exists.
        an instance PyMongoError for operational errors
    """
    update_result = collection.replace_one({"_id": _id}, document, upsert=False)
    if update_result.matched_count == 0:
        raise ObjectNotFoundError(f"Object with _id: {_id} was not found in collection: {collection.name}")


@ensure_client
def find_many(collection: Collection, query: dict) -> List[Dict]:
    """
    Finds multiple documents in the collection that match the query.

    Args:
        collection (Collection): The MongoDB collection.
        query (dict): The query criteria.

    Returns:
        List of returned objects
    """
    return list(collection.find(query))
