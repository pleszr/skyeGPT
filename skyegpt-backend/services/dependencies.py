from services.setup_services import IngestionService, DatabaseService
from services.asker_services import (
    AgentResponseStreamingService,
    AggregatedAgentResponseService,
    ConversationRetrieverService,
    FeedbackManagerService,
)


def get_ingestion_service() -> IngestionService:
    """
    Dependency provider for IngestionService.
    FastAPI will call this function when a route depends on IngestionService.
    """
    return IngestionService()


def get_database_service() -> DatabaseService:
    """
    Dependency provider for DatabaseService.
    FastAPI will call this function when a route depends on DatabaseService.
    """
    return DatabaseService()


def get_agent_response_stream_service() -> AgentResponseStreamingService:
    """
    Dependency provider for Agent Response Streaming Service.
    FastAPI will call this function when a route depends on DatabaseService.
    """
    return AgentResponseStreamingService()


def get_agent_response_service() -> AggregatedAgentResponseService:
    """
    Dependency provider for Agent Response Service.
    FastAPI will call this function when a route depends on DatabaseService.
    """
    return AggregatedAgentResponseService()


def get_conversation_retriever_service() -> ConversationRetrieverService:
    """
    Dependency provider for ConversationRetrieverService.
    FastAPI will call this function when a route depends on DatabaseService.
    """
    return ConversationRetrieverService()


def get_feedback_manager_service() -> FeedbackManagerService:
    """
    Dependency provider for FeedbackManagerService.
    FastAPI will call this function when a route depends on DatabaseService.
    """
    return FeedbackManagerService()
