from pydantic_ai import Agent
from ..prompts import PromptDefinition

def create_agent_from_prompt_version(prompt_version: PromptDefinition) -> Agent:
    return Agent(
        model=prompt_version.model,
        instrument=True,
        instructions=prompt_version.instructions,
        model_settings={'temperature': prompt_version.temperature},
        tools=prompt_version.tools
    )