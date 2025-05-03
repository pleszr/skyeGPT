from pydantic_ai import Agent
from typing import AsyncGenerator
from pydantic_ai.messages import (PartDeltaEvent, TextPartDelta, PartStartEvent, ToolCallPartDelta,
                                  FinalResultEvent, FunctionToolCallEvent, FunctionToolResultEvent,
                                  TextPart, ToolCallPart)
from fastapi import HTTPException
import logfire
import random
from retriever import db_client
from common.utils import replace_placeholders
import agentic.prompts as prompts
import json

logfire.instrument_pydantic_ai()
conversation_store = {}
current_context_store = {}

prompt_version = prompts.responder_openai_v4_openai_template

agent = Agent(
    model=prompt_version.model,
    instrument=True,
    instructions=prompt_version.instructions,
    model_settings={'temperature': prompt_version.temperature}
)


async def ask_gemini(user_prompt: str, conversation_id: str) -> AsyncGenerator[str, None]:
    prompt_template = prompt_version.prompt_template
    actual_prompt = replace_placeholders(prompt_template, {"user_prompt": user_prompt})

    message_history = conversation_store.get(conversation_id, [])

    try:
        async with agent.iter(actual_prompt, message_history=message_history) as run:
            async for node in run:
                if Agent.is_user_prompt_node(node):
                    logfire.info('user prompt node')
                elif Agent.is_model_request_node(node):
                    logfire.info('model request node')
                    async with node.stream(run.ctx) as request_stream:
                        async for event in request_stream:
                            if isinstance(event, PartStartEvent):
                                if isinstance(event.part, TextPart):
                                    yield event.part.content
                                elif isinstance(event.part, ToolCallPart):
                                    # Log tool call info if desired, but don't yield content
                                    logfire.info(f'Tool call started: {event.part.tool_name}')
                            elif isinstance(event, PartDeltaEvent):
                                if isinstance(event.delta, TextPartDelta):
                                    # logfire.info('TextPartDelta')
                                    yield event.delta.content_delta
                                elif isinstance(event.delta, ToolCallPartDelta):
                                    logfire.info('ToolCallPartDelta')
                            elif isinstance(event, FinalResultEvent):
                                logfire.info('FinalResultEvent')
                elif Agent.is_call_tools_node(node):
                    tool_args_store: dict[str, str] = {}
                    logfire.info('is_call_tools_node')
                    async with node.stream(run.ctx) as handle_stream:
                        async for event in handle_stream:
                            if isinstance(event, FunctionToolCallEvent):
                                tool_call_id = event.part.tool_call_id
                                tool_args_json = event.part.args_as_json_str()
                                tool_args_store[tool_call_id] = tool_args_json
                                logfire.info('FunctionToolCallEvent')
                            elif isinstance(event, FunctionToolResultEvent):
                                logfire.info('FunctionToolResultEvent')
                                tool_call_id = event.tool_call_id
                                stored_args_json = tool_args_store.get(tool_call_id, {})

                                global current_context_store
                                current_context_store[conversation_id] = {
                                    'tool_args': stored_args_json,
                                    'tool_result': event.result.content
                                }
                elif Agent.is_end_node(node):
                    logfire.info('is_end_node')
            new_messages = run.result.new_messages()
            conversation_store.setdefault(conversation_id, []).extend(new_messages)
            max_conversation_length = 20
            curr_conversation_length = len(conversation_store[conversation_id])

            if curr_conversation_length > max_conversation_length:
                extra_conv_counter = curr_conversation_length-max_conversation_length
                conversation_store[conversation_id] = conversation_store[conversation_id][extra_conv_counter:]
            logfire.info(f'cica length: {len(conversation_store[conversation_id])}')
            print(f'cica: {conversation_store[conversation_id]}')
    except Exception as e:
        logfire.error("Agent Run Error: {error_type} - {error_details}", error_type=type(e).__name__, error_details=e)
        raise HTTPException(status_code=500, detail="Internal error when streaming response")


# @agent.tool_plain
def roll_die_multiple_times_and_sum_result(number_of_rolls: int) -> str:
    """Roll a die X times and sums up the result."""
    die_sum = 0
    for i in range(1, number_of_rolls):
        die_sum += random.randint(1, 6)
    return str(die_sum)


@agent.tool_plain
def search_in_skye_documentation(query: str) -> str:
    """Search in Skye documentation. It is a semantic vector database.

  Args:
      query: the question to find the relevant information of
  """
    number_of_results = 10
    collection_name = "SkyeDoc"
    collection = db_client.get_collection_by_name(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=number_of_results
    )
    return json.dumps(results)
