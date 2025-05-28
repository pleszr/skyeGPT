from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Dict
from common import constants, logger, message_bundle
import uuid
from .feedback import Feedback
from pydantic_ai.messages import ModelRequest, ModelResponse, Usage


class Conversation(BaseModel):
    """
    Represents one round of conversation with the agent model.
    Includes, instructions, user prompt, tool calls, tool results, generated response
    """

    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="_id")
    feedbacks: List[Feedback] = Field(default_factory=list)
    contents: List[ModelRequest | ModelResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    def create_copy(self) -> "Conversation":
        """
        Returns a copy of the conversation.
        """
        return self.model_copy(update={"conversation_id": uuid.uuid4()})

    def get_content_as_list(self) -> "List":
        return list(self.contents)

    def extend(self, conversation: "Conversation") -> None:
        """
        Extends existing conversation with a new conversation. Keeps conversation length below MAX_CONVERSATION_LENGTH
        """
        self.contents.extend(conversation.contents)
        self._enforce_max_history_size()
        self.last_modified = datetime.now(timezone.utc)

    def _enforce_max_history_size(self: "Conversation"):
        """
        Trims the conversation history to MAX_CONVERSATION_LENGTH.
        It removes the oldest messages using FIFO (First-In, First-Out) logic.

        Args:
           self: the Conversation to be trimmed
        """
        max_conversation_length = constants.MAX_CONVERSATION_LENGTH
        curr_conversation_length = len(self.contents)
        if curr_conversation_length > max_conversation_length:
            logger.info(
                f"Current conversation length is {curr_conversation_length}, "
                f"max conversation length is {max_conversation_length}. Trimming extra conversations"
            )
            self.contents = self.contents[-max_conversation_length:]

    def add_feedback(self, feedback: Feedback) -> None:
        self.feedbacks.append(feedback)

    def archive_tool_output(self) -> None:
        """Archives the tool output content and removes usages.
        Purpose is to keep the conversation's size manageable."""
        logger.info(f"Archiving tool output of {self.conversation_id}")
        for content in self.contents:
            part = content.parts[0]
            if hasattr(part, "tool_name") and hasattr(part, "content"):
                part.content = message_bundle.CONTENT_ARCHIVED_MESSAGE
