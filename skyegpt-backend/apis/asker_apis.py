import uuid
from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
from .schemas.requests import ConversationQueryRequest
from .schemas.responses import CreateConversationIdResponse, ConversationResponse
from dependencies import (AgentResponseStreamingService, get_agent_response_stream_service,
                          ConversationRetrieverService, get_conversation_retriever_service)
from common import logger, message_bundle
from common.decorators import handle_response_stream_errors, handle_unknown_errors


asker_apis_router = APIRouter(prefix="/ask", tags=["Asker Endpoints"])


@handle_unknown_errors
@handle_response_stream_errors
@asker_apis_router.post(
    "/response/stream",
    status_code=200,
    summary="Stream response for a query within a conversation",
    description="Streams the agents response back in SSE format",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Streaming response initiated successfully.",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "description": "A continuous SSE text stream."
                    },
                    "example": "event: message\ndata: {\"text\": \"Hello!\"}\n\n"
                }
            }
        },
        422: {"description": "Validation error in request body."},
        500: {"description": "Internal server error during processing or streaming."}
    },
)
async def stream_agent_response(
        request: ConversationQueryRequest,
        streaming_service: AgentResponseStreamingService = Depends(get_agent_response_stream_service)
) -> StreamingResponse:
    """
    Streams responses from the agents based on the provided query and conversation ID.
    """
    conversation_id = request.conversation_id
    question = request.query
    logger.info(f"Received request for /stream: conversation_id='{conversation_id}'")
    response_stream = streaming_service.stream_agent_response(question, conversation_id)
    return StreamingResponse(response_stream, media_type="text/event-stream")


@handle_unknown_errors
@asker_apis_router.post(
    "/conversation",
    summary="Create a new conversation thread",
    description="""Generates a new unique identifier (UUID) for starting a conversation. Used to track conversation 
    history to preserve context""",
    response_model=CreateConversationIdResponse,
    responses={
        200: {"description": "New conversation ID generated successfully."},
        500: {"description": "Internal server error during ID generation."}
    }
)
async def create_conversation() -> CreateConversationIdResponse:
    """
    Generates and returns a new UUID V4 as a conversation ID.
    """
    logger.info("Received request to create a new conversation")
    conversation_id = str(uuid.uuid4())  # CONVERT UUID to string, without this im getting internal error
    logger.info(f"Generated new conversation_id: {conversation_id}")
    return CreateConversationIdResponse(conversation_id=conversation_id)


@handle_unknown_errors
@asker_apis_router.get(
    "/conversation/{conversation_id}",
    summary="Get a conversation by its ID",
    description="Retrieves the details and messages of a specific conversation using its ID from the URL path.",
    response_model=ConversationResponse,
    responses={
        200: {"description": "Conversation retrieved successfully."},
        404: {"description": "Conversation not found."},
        500: {"description": message_bundle.INTERNAL_ERROR}
    }
)
async def get_conversation_by_id(
        conversation_id: uuid.UUID = Path(
            ...,
            description="The unique identifier (UUID) of the conversation to retrieve."
        ),
        conversation_retriever_service: ConversationRetrieverService = Depends(get_conversation_retriever_service)
) -> ConversationResponse:
    logger.info(f"Received request to get conversation with ID: {conversation_id}")
    conversation = await conversation_retriever_service.get_conversation_by_id(str(conversation_id))
    return ConversationResponse(conversation=conversation)
