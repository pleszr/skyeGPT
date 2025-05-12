from .mongo_specific import mongo_client
from typing import Dict, Any, Optional, List
import uuid
from common import logger, constants
from agentic.conversation import Conversation
from datetime import datetime

CONVERSATION_DB_NAME = constants.DOCUMENT_DB_NAME
CONVERSATIONS_COLLECTION_NAME = constants.CONVERSATIONS_COLLECTION_NAME


def get_database(database_name: str):
    return mongo_client.get_database(database_name)


def create_or_get_collection(database_name: str, collection_name: str):
    return mongo_client.create_or_get_collection(database_name, collection_name)


def add_document_to_collection(database_name: str, collection_name: str, document: Dict[str, Any]):
    collection = mongo_client.create_or_get_collection(database_name, collection_name)
    mongo_client.add_to_collection(collection, document)


def upsert_conversation(_id: uuid, conversation: Conversation) -> None:
    logger.info(f'Upserting {_id} to database: {CONVERSATION_DB_NAME}, collection: {CONVERSATIONS_COLLECTION_NAME}')

    collection = mongo_client.create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)
    mongo_client.upsert_to_collection(collection, _id, conversation.model_dump(by_alias=True))


def find_conversation_by_id(conversation_id: uuid) -> Optional[Conversation]:
    logger.info(f'Searching for {conversation_id} in collection: {CONVERSATIONS_COLLECTION_NAME}')
    collection = mongo_client.create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)

    returned_dict = mongo_client.find_one_by_id(collection, conversation_id)
    if returned_dict is None:
        return None

    conversation = Conversation.model_validate(returned_dict)
    return conversation


def find_conversations_by_created_since(feedback_since: datetime) -> List[Conversation]:
    collection = mongo_client.create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)
    raw_conversations: List[Dict] = mongo_client.find_many(
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

    conversations = []
    for raw_conversation in raw_conversations:
        conversation = Conversation.model_validate(raw_conversation)
        conversations.append(conversation)
    return conversations


def update_conversation(_id: uuid, conversation: Conversation) -> None:
    logger.info(f'Updating {_id} in database: {CONVERSATION_DB_NAME}, collection: {CONVERSATIONS_COLLECTION_NAME}')

    collection = mongo_client.create_or_get_collection(CONVERSATION_DB_NAME, CONVERSATIONS_COLLECTION_NAME)
    mongo_client.replace_one_by_id(collection, _id, conversation.model_dump(by_alias=True))
