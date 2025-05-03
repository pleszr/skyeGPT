# from pydantic_ai import Agent
# from typing import AsyncGenerator
# from pydantic_ai.messages import PartDeltaEvent, TextPartDelta, PartStartEvent
# from fastapi import HTTPException
# import logfire
# from agent_management.models import MODELS
# from agent_management import prompts
#
# logfire.configure()
#
#
# async def ask_gemini(user_prompt: str) -> AsyncGenerator[str, None]:
#
#     agent = Agent(
#         MODELS.GEMINI_2_0.value,
#         system_prompt=prompts.skyegpt_responder_system_prompt_v1.system_prompt,
#         instrument=True,
#         model_settings={'temperature': prompts.skyegpt_responder_system_prompt_v1.temperature}
#     )
#
#     logfire.info("--- Starting agent.iter for: {user_prompt} ---", user_prompt=user_prompt)
#     try:
#         async with agent.iter(user_prompt) as run:
#             async for node in run:
#                 # if Agent.is_user_prompt_node(node):
#                 #     # logfire.info('User prompt')
#                 if hasattr(node, 'stream') and hasattr(run, 'ctx'):
#                     try:
#                         async with node.stream(run.ctx) as event_stream:
#                             async for event in event_stream:
#                                 if isinstance(event, PartStartEvent):
#                                     logfire.info(event.part.content)
#                                     yield event.part.content
#                                 if isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
#                                     delta_text = event.delta.content_delta
#                                     if delta_text:
#                                         logfire.info(delta_text)
#                                         yield delta_text
#                     except Exception as stream_exc:
#                         logfire.error(f"Error streaming events in node {type(node).__name__}: {stream_exc}")
#     except Exception as e:
#         error_message = f"[Agent Run Error: {type(e).__name__} - {e}]"
#         logfire.error(error_message)
#         raise HTTPException(status_code=500, detail="Internal error when streaming response")
#     finally:
#         logfire.info("--- Finished agent.iter for: {user_prompt} ---", user_prompt=user_prompt)
