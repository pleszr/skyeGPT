from pydantic_ai import Agent
from ..prompts import PromptDefinition


def create_agent_from_prompt_version(prompt_version: PromptDefinition) -> Agent:
    """Creates a Pydantic agent from a PromptDefinition. If an optional field is none, it is not passed to the agent"""
    agent_kwargs = {
        "model": prompt_version.model,
        "instrument": True,
        "instructions": prompt_version.instructions,
        "model_settings": {'temperature': prompt_version.temperature},
        "output_type": prompt_version.output_type,
    }

    optional_fields = {
        "system_prompt": prompt_version.system_prompt,
        "instructions": prompt_version.instructions,
        "output_type": prompt_version.output_type,
        "tools": prompt_version.tools,
    }

    for key, value in optional_fields.items():
        if value is not None:
            agent_kwargs[key] = value

    return Agent(**agent_kwargs)
