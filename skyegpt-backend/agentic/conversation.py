"""Data model for managing conversations with the agent, including message history and feedback."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from common import constants, logger, message_bundle
import uuid
from .feedback import Feedback
from pydantic_ai.messages import ModelRequest, ModelResponse


class Conversation(BaseModel):
    """Represents a conversation with the agent.

    Includes instructions, user prompt, tool calls, tool results, and responses.
    """

    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="_id")
    feedbacks: List[Feedback] = Field(default_factory=list)
    contents: List[ModelRequest | ModelResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    def create_copy(self) -> "Conversation":
        """Returns a copy of the conversation with a new UUID."""
        return self.model_copy(update={"conversation_id": uuid.uuid4()})

    def get_content_as_list(self) -> "List":
        """Returns the list of message contents."""
        return list(self.contents)

    def extend(self, conversation: "Conversation") -> None:
        """Extends the conversation with new content from another conversation.

        Ensures total history stays within MAX_CONVERSATION_LENGTH.
        """
        self.contents.extend(conversation.contents)
        self._enforce_max_history_size()
        self.last_modified = datetime.now(timezone.utc)

    def _enforce_max_history_size(self: "Conversation"):
        """Trims the conversation history to the configured maximum length.

        Removes oldest messages in FIFO order.
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
        """Adds a feedback entry to the conversation."""
        self.feedbacks.append(feedback)

    def archive_tool_output(self) -> None:
        """Archives the tool output content and removes usages.

        This keeps the stored conversation size manageable.
        """
        logger.info(f"Archiving tool output of {self.conversation_id}")
        for content in self.contents:
            part = content.parts[0]
            if hasattr(part, "tool_name") and hasattr(part, "content"):
                part.content = message_bundle.CONTENT_ARCHIVED_MESSAGE
