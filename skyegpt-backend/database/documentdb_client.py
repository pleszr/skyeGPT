"""
Abstraction layer for managing Document database. Acts as an interface to hide the underlying Mongo database.
"""
from .mongo_specific import mongo_client
from functools import wraps
from typing import Dict, Optional, List, Any
import uuid
from common import logger, constants
from common.exceptions import DocumentDBError
from agentic.conversation import Conversation
from datetime import datetime
from pymongo.errors import PyMongoError

CONVERSATION_DB_NAME = constants.DOCUMENT_DB_NAME
CONVERSATIONS_COLLECTION_NAME = constants.CONVERSATIONS_COLLECTION_NAME


def _handle_mongo_errors(func):
    """Decorator to catch and raise DocumentDBError on PyMongo exceptions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PyMongoError as e:
            logger.exception('Exception during Document DB operations')
            raise DocumentDBError(f"Database operation {func.__name__} failed") from e
    return wrapper


@_handle_mongo_errors
def get_database(database_name: str):
    return mongo_client.get_database(database_name)


@_handle_mongo_errors
def create_or_get_collection(database_name: str, collection_name: str):
    return mongo_client.create_or_get_collection(database_name, collection_name)


@_handle_mongo_errors
def upsert_conversation(conversation_id: uuid, conversation: Conversation) -> None:
    """Insert or update a conversation in the collection by ID.
    Args:
        conversation_id: uuid of the conversation, used to identify the record to be updated
        conversation: the found record will be updated to this conversation
    Raises:
        DocumentDBError: for transactional errors
    """
    logger.info(f'Upserting {conversation_id} to collection: {CONVERSATIONS_COLLECTION_NAME}')
    collection = create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)
    mongo_client.upsert_to_collection(collection, conversation_id, conversation.model_dump(by_alias=True))


@_handle_mongo_errors
def find_conversation_by_id(conversation_id: uuid) -> Optional[Conversation]:
    """Find a conversation document by its ID and return as a Conversation object.
    Returns:
        the found conversation OR None
    Raises:
        DocumentDBError: for transactional errors
    """
    logger.info(f'Searching for {conversation_id} in collection: {CONVERSATIONS_COLLECTION_NAME}')
    collection = create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)

    search_result = mongo_client.find_one_by_id(collection, conversation_id)
    if search_result is None:
        return None
    return Conversation.model_validate(search_result)


@_handle_mongo_errors
def find_conversations_by_created_since(feedback_since: datetime) -> List[Conversation]:
    """Find conversations with feedbacks created since the given datetime.
    Returns:
        List of conversations which have feedback since date. Returns empty list if nothing is found.
    Raises:
        DocumentDBError: for transactional errors
    """
    collection = create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)
    search_result: List[Dict] = mongo_client.find_many(
        collection,
        {
            'feedbacks': {
                '$elemMatch': {
                    'created_at': {
                        '$gte': feedback_since
                    }
                }
            }
        }
    )
    return _parse_raw_conversations(search_result)


def _parse_raw_conversations(raw_conversations: List[Dict[str, Any]]) -> List[Conversation]:
    """Helper method to parse a list of raw MongoDB documents into Conversation objects."""
    conversations = []
    for raw_conversation in raw_conversations:
        conversation = Conversation.model_validate(raw_conversation)
        conversations.append(conversation)
    return conversations


@_handle_mongo_errors
def update_conversation(_id: uuid, conversation: Conversation) -> None:
    """Replace an existing conversation document by its ID.
    Raises:
        DocumentDBError: for transactional errors
        ObjectNotFoundError: the conversation wasn't found in the database
    """
    logger.info(f'Updating {_id} in database: {CONVERSATION_DB_NAME}, collection: {CONVERSATIONS_COLLECTION_NAME}')
    collection = create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)
    mongo_client.replace_one_by_id(collection, _id, conversation.model_dump(by_alias=True))
