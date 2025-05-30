"""Defines prompt configurations for SkyeGPT agents and dynamic loading text generation."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from .models import MODELS
from typing import Callable, List, Optional, Any
from . import tools
from common.constants import PromptUseCase


class PromptDefinition(BaseModel):
    """Defines a prompt configuration for an agent.

    Stores all prompt-related configuration in one place. Prompt defs are version-controlled and part of the codebase.

    Args:
        name: Identifier for the prompt definition. Used for human readability.
        use_case: Defines where the agent will be used. See PromptUseCase enum.
        version: Version tag of the prompt definition.
        model: Underlying model to be used.
        created_at: Timestamp when the prompt was created.
        temperature: Temperature setting for the agent.
        output_type: Structured output type, if any.
        instructions: Agent instructions (system-level).
        system_prompt: System-level prompt to prepend.
        prompt_template: Optional template to format user question.
        tools: External tools the agent may invoke.
    """

    name: str
    use_case: PromptUseCase
    version: str
    model: MODELS
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    temperature: float
    output_type: Optional[Any] = Field(default=str)
    instructions: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)
    prompt_template: Optional[str] = Field(default=None)
    tools: List[Callable] = Field(default=None)


responder_openai_v1 = PromptDefinition(
    name="skyegpt-responder-agent",
    use_case=PromptUseCase.response_generator,
    model=MODELS.OPENAI_GPT_4_1.value,
    version="v1",
    temperature=0.0,
    instructions="Given the information the tools you have access to and not prior knowledge, answer the query. "
    "Aim to give a link of the relevant documentation.",
    prompt_template="Question:",
    tools=[],
)

responder_openai_v2 = PromptDefinition(
    name="skyegpt-responder-agent",
    use_case=PromptUseCase.response_generator,
    model=MODELS.OPENAI_GPT_4_1.value,
    version="v2",
    temperature=0.0,
    instructions="You are a support person helping to resolve questions related to Innoveo Skye. "
    "Do NOT rely on your existing knowledge, ALWAYS use the tools and answer the questions ONLY based on "
    "the outcome of the tools. Aim to give a link of the relevant documentation",
    prompt_template="User question:",
    tools=[],
)

responder_openai_v3 = PromptDefinition(
    name="skyegpt-responder-agent",
    use_case=PromptUseCase.response_generator,
    version="v3",
    model=MODELS.OPENAI_GPT_4_1.value,
    temperature=0.0,
    instructions="You are a support person helping to resolve questions related to Innoveo Skye."
    "CRITICAL: for ALL questions about Innoveo Skye you MUST use your tools to gather knowledge. "
    "Do NOT answer from memory. Your ONLY source of information is the output of your tools"
    "Be direct and short."
    "Aim to give a link of the relevant documentation where the user finds more detailed instructions",
    prompt_template="User is asking about Innoveo Skye or one of its features. "
    "CRITICAL: use your tools to gather context. You must NOT answer it from your memory."
    "The question: {{user_prompt}}",
    tools=[],
)

responder_openai_v4_openai_template = PromptDefinition(
    # https://cookbook.openai.com/examples/gpt4-1_prompting_guide
    name="skyegpt-responder-agent",
    use_case=PromptUseCase.response_generator,
    model=MODELS.OPENAI_GPT_4_1,
    version="v4",
    temperature=0.0,
    instructions="""You are an agent - please keep going until the user’s query is completely resolved,
before ending your turn and yielding back to the user. Only terminate your turn when you are sure
that the problem is solved."
You should ALWAYS use your tools to answer. Your job is to respond based on the files documentation
you have access to via tools. do NOT guess or make up an answer.

# Workflow

## High-Level Problem Solving Strategy

1. Analyze the question the user asked. Carefully read the option and think through what is the intent
behind the user's question. Check the message history for more context.
2. Once you have a good understanding about the user's question and it's intent, review your tools
and decide which tools to use and with what parameters.
3. Use your tools.
4. Evaluate if your the results that you got from your tools provide enough clarity for you to
answer the question.
5. Use your tools again if the results were not satisfactory.
6. If none of your tools gave any response that is relevant to the user's question, admit that you did
not find relevant documents. Do NOT guess or make up an answer.
7. Answer the question. Be brief and aim to give a link to the documentation where the user can
followup for more details.
""",
    prompt_template="""
You are an agent whose job is to answer questions based the documentation of the Innoveo Skye or related documents.
Use your tools to check the documentation. User's question: {{user_question}}
""",
    tools=[tools.search_in_skye_documentation],
)

loading_text_generator_v1 = PromptDefinition(
    name="skyegpt-dynamic_loading_text_generator_agent",
    use_case=PromptUseCase.dynamic_loading_text,
    model=MODELS.OPENAI_GPT_3_5,
    version="v1",
    temperature=0.0,
    output_type=List[str],
    system_prompt="""
Suggest 5 next-step prompts as a JSON array. They will be used as texts in the loading animation.
Your job is NOT to answer the question but to respond with 5 steps that you would take.
You are part of support so there is no point reaching out to them.
Take a funny, but professional tone. Aim to inform but slightly entertain.
Available tools: search in Innoveo Skye's documentation, search or Innoveo Partner Hub confluence.

Example:
[
    "Searching Innoveo Skye documentation how to add a multibrick...",
    "Filtering out non relevant results. User meant multibrick not brickmulti...",
    "Looking for examples on multibrick operations on Innoveo Partner Hub confluence...",
    "Verifying output quality, cross checking possible hallucinations...",
    "Maybe I should stand up from the computer and ask Roland Lukacs personally"
    ]
""",
    prompt_template="""Suggest 5 next-step prompts as a JSON array for the following question '{{user_question}}'.
Send the 5 prompts back in one a JSON array. Generating less then 5 response is fatal failure""",
)
