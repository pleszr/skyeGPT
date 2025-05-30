"""Wrapper to query the LLM service with a randomized conversation ID."""

from evaluator.skyegpt_client import query_skyegpt
import random


def query_llm(url: str, question: str) -> dict:
    """Query the SkyEGPT service with a random conversation ID."""
    conversation_id = str(random.randint(1, 99999999))
    return query_skyegpt(url, question, conversation_id)
