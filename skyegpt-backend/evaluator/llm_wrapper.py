from evaluator.skyegpt_client import query_skyegpt
import random


def query_llm(url: str, question: str) -> dict:
    conversation_id = str(random.randint(1, 99999999))
    return query_skyegpt(url, question, conversation_id)
