from agentic.feedback import Feedback
from agentic.conversation import Conversation
from datetime import datetime
import uuid
from agentic.prompts import PromptDefinition
from agentic.models import MODELS
from typing import List, Dict
from common import constants


sample_uuid = uuid.UUID("db5008a7-432f-4b4e-985d-bdb07cdcc65e")

sample_conversation_feedback = Feedback(
    id=uuid.UUID("9ea036ea-d491-4987-ab89-d253cce78832"),
    vote="positive",
    comment="This was clearly false, the links are directing me to innoveo.skye.com/docs",
    created_at=datetime.fromisoformat("2025-05-12T18:15:19.104000"),
)

sample_instruction = "Sample you are agent - instruction"

sample_conversation_content = [
    {
        "parts": [
            {
                "content": """
                    \n    You are an agent whose job is to answer questions based the documentation of the
                    Innoveo Skye or related documents. \n    Use your tools to check the documentation.
                    User's question: Does Skye support SOAP API?\n    """,
                "timestamp": "2025-05-12T18:11:14.135000",
                "part_kind": "user-prompt",
            }
        ],
        "instructions": sample_instruction,
        "kind": "request",
        "usage": {
            "requests": 1,
            "request_tokens": 491,
            "response_tokens": 23,
            "total_tokens": 514,
            "details": {
                "accepted_prediction_tokens": 0,
                "audio_tokens": 0,
                "reasoning_tokens": 0,
                "rejected_prediction_tokens": 0,
                "cached_tokens": 0,
            },
        },
    },
    {
        "parts": [
            {
                "tool_name": "search_in_skye_documentation",
                "args": '{"query":"Does Skye support SOAP API?"}',
                "tool_call_id": "call_7GrxOBQ7b0eKgFVf9Hp45tn9",
                "part_kind": "tool-call",
            }
        ],
        "model_name": "gpt-4.1",
        "timestamp": "2025-05-12T18:11:15",
        "kind": "response",
    },
    {
        "parts": [
            {
                "tool_name": "search_in_skye_documentation",
                "content": "# sample tool return #1",
                "tool_call_id": "call_bTRXVb3m6ixxpGiaLv4Q6Ae9",
                "timestamp": "2025-05-19T17:47:12.591000",
                "part_kind": "tool-return",
            }
        ],
        "instructions": sample_instruction,
        "kind": "request",
    },
]

sample_conversation = Conversation(
    conversation_id=sample_uuid, feedbacks=[sample_conversation_feedback], contents=sample_conversation_content
)

mock_raw_chunks = ["chunkA", "chunkB", "chunkC"]
mock_sse_loading_text_chunks = ["Searching in Skye doc1", "Searching in Skye doc2"]
mock_sse_response_chunks = ["data: chunk1\n\n", "data: chunk2\n\n"]


async def sse_response_stream(*args, **kwargs):
    for chunk in mock_sse_response_chunks:
        yield chunk


async def raw_response_stream(*args, **kwargs):
    for chunk in mock_raw_chunks:
        yield chunk


expected_stream_outcome = [
    'event: dynamic_loading_text\ndata: ["Searching in Skye doc1", "Searching in Skye doc2"]\n\n',
    "event: streamed_response\ndata: chunkA\n\n",
    "event: streamed_response\ndata: chunkB\n\n",
    "event: streamed_response\ndata: chunkC\n\n",
]

sample_skye_document_search_result = {
    "document": "#Sample_search_result",
    "metadata": {
        "file_name": "595329025",
        "documentation_link": "https://innoveo.atlassian.net/wiki/spaces/IPH/pages/595329025",
    },
}


def mock_search_in_skye_documentation(query: str) -> List[Dict]:
    """Search in Skye documentation. It is a semantic vector database.

    Args:
        query: the question to find the relevant information of

    """
    return [sample_skye_document_search_result]


sample_agent_service_prompt = PromptDefinition(
    name="skyegpt-responder-agent",
    use_case=constants.PromptUseCase.response_generator,
    model=MODELS.OPENAI_GPT_4_1.value,
    version="v1",
    temperature=0.0,
    instructions="Given the information the tools you have access to and not prior knowledge, answer the query. "
    "Aim to give a link of the relevant documentation.",
    prompt_template="Question:",
    tools=[mock_search_in_skye_documentation],
)

sample_loading_text_prompt = PromptDefinition(
    name="skyegpt-dynamic_loading_text_generator_agent",
    use_case=constants.PromptUseCase.dynamic_loading_text,
    model=MODELS.OPENAI_GPT_3_5,
    version="v1",
    temperature=0.0,
    output_type=List[str],
    system_prompt="""Suggest 5 next-step prompts as a JSON array for the following question""",
)
