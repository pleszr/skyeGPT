from fastapi import APIRouter, Depends, status
from .schemas.responses import AgentResponse, PlaygroundResponse
from .schemas.requests import ConversationQueryRequest
from dependencies import AgentResponseService, get_agent_response_service
from common.decorators import handle_aggregated_response_errors, handle_unknown_errors
from common import logger

evaluator_apis_router = APIRouter(prefix="/evaluate", tags=["Evaluator"])


@handle_unknown_errors
@handle_aggregated_response_errors
@evaluator_apis_router.post(
    "/response",
    summary="Returns response in one message including used context",
    description="""Used to evaluate the agent. Takes conversation id and query, uses the agents the generate an answer,
     and returns both the response and the used context in one message, without streaming""",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Answer generation successful, returning answer and context."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error in request body."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error during Pydantic AI processing."}
    }
)
async def evaluate_pydantic(
        request: ConversationQueryRequest,
        agent_response_service: AgentResponseService = Depends(get_agent_response_service)
) -> AgentResponse:
    """
    Processes query to generate agent answer.
    """
    conversation_id = request.conversation_id
    query = request.query
    logger.info(f"Received request aggregated agent response: conversation_id='{conversation_id}'")

    with_context = True
    response_dict = await agent_response_service.agent_response(query, conversation_id, with_context)
    generated_answer = response_dict.get("generated_answer")
    context = response_dict.get("curr_context")
    return AgentResponse(generated_answer=generated_answer, curr_context=context)


@evaluator_apis_router.post(
    "/playground",
    summary="Evaluate query using Playground model",
    description="""Receives a query and conversation ID, processes it using the Playground's Pydantic AI model, 
    and returns the raw generated response string.""",
    response_model=PlaygroundResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Playground evaluation successful, returning generated text."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error in request body."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error during Playground processing."}
    }
)
async def evaluate_playground(request: ConversationQueryRequest) -> PlaygroundResponse:
    """
    Used to test various features. Dev only.
    """
    response_text = request.query
    # conversation_id = request.conversation_id
    # query = request.query
    # logger.info(f"Received request for playground: conversation_id='{conversation_id}'")
    #
    #
    # generator = PydanticAi.stream_agent_response(query, str(conversation_id))
    # async for token in generator:
    #     response_text += token
    # logger.info(f"Successfully call to playground with conversation_id='{conversation_id}'")
    return PlaygroundResponse(response=response_text)
