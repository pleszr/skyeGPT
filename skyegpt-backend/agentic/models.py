from enum import Enum


class MODELS(str, Enum):
    GEMINI_2_0 = "gemini-2.0-flash"
    GEMINI_2_5 = "gemini-2.5-pro-preview-03-25"
    OPENAI_GPT_4_1 = "openai:gpt-4.1"
    OPENAI_GPT_4_1_MINI = "openai:gpt-4.1-mini"
