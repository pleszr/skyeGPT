from typing import Literal, TypeAlias
from enum import Enum
from pydantic import BaseModel, conlist

# API
MEDIA_TYPE_SSE = "text/event-stream"

# DATA_INGESTION
IPH_LOCAL_FOLDER_LOCATION = "content/innoveo-partner-hub"
SKYE_DOC_COLLECTION_NAME = "SkyeDoc"
IPH_DOC_COLLECTION_NAME = "SkyeDoc"
SKYE_DOC_LOCAL_FOLDER_LOCATION_TEMPLATE = "content/skyedoc/skye-{{skye_major_version}}"

# ASKER
MAX_CONVERSATION_LENGTH = 20

# RETRIEVER
VECTOR_NUMBER_OF_RESULTS = 10

# Document DB
DOCUMENT_DB_NAME = "skyegpt"
CONVERSATIONS_COLLECTION_NAME = "conversations"

# Type Alias
VoteType: TypeAlias = Literal["positive", "negative", "not_specified"]


class PromptUseCase(str, Enum):
    dynamic_loading_text = "dynamic_loading_text"
    response_generator = "response_generator"


class SseEventTypes(str, Enum):
    dynamic_loading_text = "dynamic_loading_text"
    streamed_response = "streamed_response"


class DynamicLoadingTextResponseModel(BaseModel):
    result: conlist(str, min_length=5, max_length=5)
