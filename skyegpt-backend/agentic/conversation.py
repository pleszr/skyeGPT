from pydantic_ai.messages import ModelResponse, ModelRequest
from typing import List
from common import constants, logger

from dataclasses import dataclass, field


@dataclass
class Conversation:
    """
    Represents one round of conversation with the agent model.
    Includes, instructions, user prompt, tool calls, tool results, generated response
    """
    content: List[ModelRequest | ModelResponse] = field(default_factory=list)

    def copy(self) -> 'Conversation':
        """
        Returns a copy of the conversation.
        """
        return Conversation(content=self.content.copy())

    def list(self) -> 'List':
        return list(self.content)

    def extend(self, conversation: 'Conversation') -> None:
        """
        Extends existing conversation with a new conversation. Keeps conversation length below MAX_CONVERSATION_LENGTH
        """
        self.content.extend(conversation.content)
        self._trim_conversation_history()

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
