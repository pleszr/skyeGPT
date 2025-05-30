"""Defines the Feedback model used to store user feedback on conversations."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import uuid
from common import constants


class Feedback(BaseModel):
    """Represents feedback given to a conversation."""

    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4(), alias="_id")
    vote: constants.VoteType = Field(default="not_specified")
    comment: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
