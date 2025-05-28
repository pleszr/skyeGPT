import asyncio
import uuid

from common import logger, constants
from typing import Dict, List, Any
from common.decorators import handle_store_errors
from agentic.conversation import Conversation
from database import documentdb_client

MAX_CONVERSATION_LENGTH = constants.MAX_CONVERSATION_LENGTH


class StoreManager:
    """
    Manages shared in-memory stores for conversation history and context.

    This class provides thread/task-safe access to dictionaries storing
    conversation data using asyncio locks. It is designed to be instantiated
    once at the module level, creating a singleton instance that can be
    injected as a dependency into services requiring access to this shared state.
    """

    _instance = None

    def __new__(cls):
        """
        Ensures only one instance of StoreManager exists.

        Returns:
            The singleton instance of StoreManager.
        """
        if cls._instance is None:
            cls._instance = super(StoreManager, cls).__new__(cls)
            cls._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initializes the StoreManager instance. This will only run once
        for the singleton instance.
        """
        if self._initialized:
            return
        self._conversation_context_store: Dict[str, List[Dict[str, Any]]] = {}
        self._conversation_context_store_lock = asyncio.Lock()

        self._initialized = True

    @handle_store_errors
    async def get_conversation_by_id(self, conversation_id: uuid) -> Conversation:
        """
        Retrieves the conversation by conversation_id from document database
        OR creates a new, empty one with conversation_id.

        Args:
            conversation_id: The unique identifier for the conversation.

        Returns:
            A Conversation containing the messages for the conversation, or an empty Conversation
            if the conversation ID is not found.

        Raises StoreManagementException for invalid inputs or internal errors
        """
        logger.info(f"Retrieving conversation with id {conversation_id}")
        self._handle_empty_key(conversation_id)

        found_conversation = documentdb_client.find_conversation_by_id(conversation_id)
        return found_conversation or Conversation(conversation_id=conversation_id)

    @handle_store_errors
    async def extend_conversation_history(self, original_conversation_id: uuid, new_conversation: Conversation):
        """
        Extends new messages to a conversation's history and trims it if necessary.

        Args:
            original_conversation_id: The unique identifier for the conversation.
            new_conversation: A Conversation object containing the new messages to be added.

        Raises StoreManagementException for invalid inputs or internal errors
        """
        logger.info(f"Extending conversation history with conversation id: {original_conversation_id}")

        conversation = await self.get_conversation_by_id(original_conversation_id)
        conversation.extend(new_conversation)
        documentdb_client.upsert_conversation(conversation.conversation_id, conversation)

    @handle_store_errors
    async def get_conversation_context(self, conversation_id) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation context for a specific conversation ID.

        Args:
            conversation_id: The unique identifier for the conversation.

        Returns:
            A list containing the context entries for the conversation, or an
            empty list if the conversation ID is not found.

        Raises StoreManagementException for invalid inputs or internal errors
        """
        logger.info(f"Getting conversation context with id {conversation_id}")
        self._handle_empty_key(conversation_id)
        async with self._conversation_context_store_lock:
            return list(self._conversation_context_store.get(conversation_id, []))

    @handle_store_errors
    async def append_conversation_context(self, conversation_id: uuid, context: Dict[str, Any]):
        """
        Appends a new context dictionary to the context list for a conversation. Thread safe.
        Args:
            conversation_id: The unique identifier for the conversation.
            context: The new context dictionary to add to the list.

        Raises StoreManagementException for invalid inputs or internal errors
        """
        logger.info(f"Appending conversation context with id {conversation_id}")
        self._handle_empty_key(conversation_id)
        async with self._conversation_context_store_lock:
            self._conversation_context_store.setdefault(conversation_id, []).append(context)

    def _handle_empty_key(self, key: str):
        """
        Checks of the key is empty.

        Raises ValueError for invalid inputs or internal errors
        """
        if not key:
            raise ValueError("Key can not be empty")
