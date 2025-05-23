from typing import AsyncGenerator, List
from pydantic_ai import Agent
from pydantic_ai.messages import (PartDeltaEvent, TextPartDelta, PartStartEvent,
                                  FunctionToolCallEvent, FunctionToolResultEvent,
                                  TextPart, ToolCallPart, ModelRequest, ModelResponse)
from pydantic_ai.agent import AgentRun, CallToolsNode, ModelRequestNode
from .pydantic_ai_specific import agent_factory, decorators
from . import prompts
from common import utils, logger, stores
from .conversation import Conversation
import uuid


class DynamicLoadingTextService:
    def __init__(self, prompt_version: prompts.PromptDefinition):
        self.prompt_version = prompt_version
        self.agent: Agent = agent_factory.create_agent_from_prompt_version(self.prompt_version)

    async def generate_dynamic_loading_text(self, user_question: str) -> List[str]:
        """tbd """
        result = await self.agent.run(user_prompt=self._construct_user_prompt(user_question))
        print(result.output)
        return result.output

    def _construct_user_prompt(self, user_question: str) -> str:
        """
        Constructs the final user prompt by injecting the user's question
        into a predefined template.
        """
        prompt_template = self.prompt_version.prompt_template
        return utils.replace_placeholders(prompt_template, {"user_question": user_question})
