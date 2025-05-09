import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any


MONGO_USERNAME = os.getenv("MONGO_USERNAME", "skyegpt-admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "TODO")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo:27017")

CONNECTION_STRING = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/?authSource=admin"

_mongo_client = MongoClient(CONNECTION_STRING, uuidRepresentation='standard')


def get_database(database_name: str):
    return _mongo_client[database_name]


def create_or_get_collection(database_name: str, collection_name: str):
    database = get_database(database_name)
    return database[collection_name]


def add_document_to_collection(collection: Collection, document: Dict[str, Any]):
    collection.insert_one(document)



