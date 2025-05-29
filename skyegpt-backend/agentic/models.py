"""Defines an enum for models to reduce possible typos."""

from enum import Enum


class MODELS(str, Enum):
    """Defines the list of models that the agent accepts. Used by PromptDefinition."""

    GEMINI_2_0 = "gemini-2.0-flash"
    GEMINI_2_5 = "gemini-2.5-pro-preview-03-25"
    OPENAI_GPT_4_1 = "openai:gpt-4.1"
    OPENAI_GPT_4_1_MINI = "openai:gpt-4.1-mini"
    OPENAI_GPT_3_5 = "gpt-3.5-turbo"
