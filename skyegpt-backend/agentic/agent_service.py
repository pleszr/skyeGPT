from typing import AsyncGenerator, List
from pydantic_ai import Agent
from pydantic_ai.messages import (PartDeltaEvent, TextPartDelta, PartStartEvent,
                                  FunctionToolCallEvent, FunctionToolResultEvent,
                                  TextPart, ToolCallPart, ModelResponse, ModelRequest)
from pydantic_ai.agent import AgentRun, CallToolsNode, ModelRequestNode
from .pydantic_ai_specific import agent_factory, decorators
from . import prompts
from common import utils, logger, stores
from .conversation import Conversation


class AgentService:
    def __init__(
            self,
            store_manager: stores.StoreManager,
            prompt_version: prompts.PromptDefinition
    ):
        self.store_manager = store_manager
        self.prompt_version = prompt_version

        self.agent = agent_factory.create_agent_from_prompt_version(self.prompt_version)

    async def stream_agent_response(self, user_question: str, conversation_id: str) -> AsyncGenerator[str, None]:
        """
    Streams the agent's response to a user question in real-time.

    This method serves as the public interface for streaming responses
    from the agent, abstracting away the underlying framework details.

    Args:
        user_question (str): The user’s question or input prompt.
        conversation_id (str): The unique identifier of the conversation.

    Yields:
        AsyncGenerator[str, None]: A stream of text chunks representing
        the agent's incremental response.

    Raises:
        UsageLimitExceededError: When a usage limit is exceeded
        ResponseGenerationError: Various errors during response generation
    """
        user_prompt = self._construct_user_prompt(user_question)
        existing_conversation = await self.store_manager.get_conversation_by_id(conversation_id)
        return self._stream_agent_response_pydantic(user_prompt, conversation_id, existing_conversation.content)

    @decorators.handle_pydantic_response_errors
    async def _stream_agent_response_pydantic(
            self,
            user_prompt: str,
            conversation_id: str,
            message_history: List[ModelRequest | ModelResponse]
    ) -> AsyncGenerator[str, None]:
        """
        Handles the Pydantic AI agent interaction to stream responses.

        This private method iterates through the agent's execution graph,
        delegating node handling to specific helper methods and managing
        the overall conversation flow.
        """
        async with self.agent.iter(user_prompt=user_prompt, message_history=message_history) as run:
            async for node in run:
                if Agent.is_model_request_node(node):
                    async for chunk in self._handle_model_request_node(node, run):
                        yield chunk
                elif Agent.is_call_tools_node(node):
                    await self._handle_call_tools_node(node, run, conversation_id)
            await self._add_conversation_to_store(run, conversation_id)
            logger.info(f'Answer generation for conversation_id {conversation_id} finished.')

    def _construct_user_prompt(self, user_question: str):
        """
        Constructs the final user prompt by injecting the user's question
        into a predefined template.
        """
        prompt_template = self.prompt_version.prompt_template
        return utils.replace_placeholders(prompt_template, {"user_question": user_question})

    async def _handle_model_request_node(self, node: ModelRequestNode, run: AgentRun):
        """
        Handles streaming events from a model request node. Processes events from the language model, yielding
        text content as it becomes available.

        Yields:
            AsyncGenerator[str, None]: Incremental text chunks from the language model.
        """
        async with node.stream(run.ctx) as request_stream:
            async for event in request_stream:
                if isinstance(event, PartStartEvent):
                    if isinstance(event.part, TextPart):
                        yield event.part.content
                    elif isinstance(event.part, ToolCallPart):
                        logger.info(f'Request to run tool: {event.part.tool_name}')
                elif isinstance(event, PartDeltaEvent):
                    if isinstance(event.delta, TextPartDelta):
                        yield event.delta.content_delta

    async def _handle_call_tools_node(self, node: CallToolsNode, run: AgentRun, conversation_id: str):
        """
        Handles events related to tool calls requested by the agent and appends context to the context store.
        """
        tool_args_json = {}
        logger.trace('is_call_tools_node')
        async with node.stream(run.ctx) as handle_stream:
            async for event in handle_stream:
                if isinstance(event, FunctionToolCallEvent):
                    tool_args_json = event.part.args_as_json_str()
                    logger.trace('FunctionToolCallEvent')
                elif isinstance(event, FunctionToolResultEvent):
                    logger.trace('FunctionToolResultEvent')
                    current_context = {
                        'tool_args': tool_args_json,
                        'tool_result': event.result.content
                    }
                    await self.store_manager.append_conversation_context(conversation_id, current_context)

    async def _add_conversation_to_store(self, run: AgentRun, conversation_id: str):
        """
        Adds new messages from the agent run to the conversation history store.
        """
        new_messages = Conversation(run.result.new_messages())
        await self.store_manager.extend_conversation_history(conversation_id, new_messages)
