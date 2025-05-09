from .mongo_specific import mongo_client
from typing import Dict, Any


def get_database(database_name: str):
    return mongo_client.get_database(database_name)


def create_or_get_collection(database_name: str, collection_name: str):
    return mongo_client.create_or_get_collection(database_name, collection_name)


def add_document_to_collection(database_name: str, collection_name: str, document: Dict[str, Any]):
    collection = mongo_client.create_or_get_collection(database_name, collection_name)
    collection.insert_one(document)
