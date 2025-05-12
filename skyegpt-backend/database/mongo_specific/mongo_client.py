import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any
import uuid


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


def add_to_collection(collection: Collection, document: Dict[str, Any]):
    collection.insert_one(document)


def upsert_to_collection(collection: Collection, _id: uuid, document: Dict[str, Any]):
    collection.replace_one({"_id": _id}, document, upsert=True)


def find_one_by_id(collection: Collection, _id: uuid):
    return collection.find_one({"_id": _id})


def replace_one_by_id(collection: Collection, _id: uuid, document: Dict[str, Any]):
    collection.replace_one({"_id": _id}, document, upsert=False)


def find_many(collection: Collection, query: dict):
    return collection.find(query)
