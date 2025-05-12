from datetime import datetime, timezone
from pydantic_ai.messages import ModelResponse, ModelRequest
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from common import constants, logger
import uuid
from .feedback import Feedback


class Conversation(BaseModel):
    """
    Represents one round of conversation with the agent model.
    Includes, instructions, user prompt, tool calls, tool results, generated response
    """
    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="_id")
    feedbacks: List[Feedback] = Field(default_factory=list)
    content: List[ModelRequest | ModelResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    def create_copy(self) -> 'Conversation':
        """
        Returns a copy of the conversation.
        """
        return self.model_copy(update={
            "conversation_id": uuid.uuid4()})

    def get_content_as_list(self) -> 'List':
        return list(self.content)

    def extend(self, conversation: 'Conversation') -> None:
        """
        Extends existing conversation with a new conversation. Keeps conversation length below MAX_CONVERSATION_LENGTH
        """
        self.content.extend(conversation.content)
        self._trim_conversation_history()
        self.last_modified = datetime.now(timezone.utc)

    def add_feedback(self, feedback: Feedback) -> None:
        self.feedbacks.append(feedback)

    def _trim_conversation_history(self: 'Conversation'):
        """
        Trims the conversation history to MAX_CONVERSATION_LENGTH.
        It removes the oldest messages using FIFO (First-In, First-Out) logic.

        Args:
           self: the Conversation to be trimmed
        """
        max_conversation_length = constants.MAX_CONVERSATION_LENGTH
        curr_conversation_length = len(self.content)
        if curr_conversation_length > max_conversation_length:
            logger.info(f'Current conversation length is {curr_conversation_length}, '
                        f'max conversation length is {max_conversation_length}. Trimming extra conversations')
            self.content = self.content[-max_conversation_length:]
