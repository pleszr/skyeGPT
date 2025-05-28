from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Literal, List
import uuid
from common import constants


class SkyeVersionRequest(BaseModel):
    """
    Request model for specifying the Skye major version.
    """

    skye_major_version: str = Field(
        ...,
        pattern=r"^\d+\.\d+$",
        description="Skye major version in format X.Y (e.g., 9.16)",
        examples=["10.0", "9.16"],
        json_schema_extra={
            "error_messages": {"pattern": "Invalid version format. Must be in format 'X.Y' (e.g., '9.16', '10.3')"}
        },
    )


class ConversationQueryRequest(BaseModel):
    conversation_id: uuid.UUID = Field(
        ...,
        description="The unique identifier for the conversation thread.",
        examples=[uuid.uuid4()],
    )
    query: str = Field(
        ...,
        description="The user's question or query to be streamed.",
        examples=["Does Skye support SOAP API?"],
        max_length=4000,
    )


class ImportRequest(BaseModel):
    """
    Request model for specifying what to import to the lookup database.
    """

    class SkyedocConfig(BaseModel):
        enabled: bool
        skye_major_version: Optional[str] = Field(
            pattern=r"^\d+\.\d+$",
            description="Skye major version in format X.Y (e.g., 9.16)",
            examples=["10.0", "9.16"],
            json_schema_extra={
                "error_messages": {"pattern": "Invalid version format. Must be in format 'X.Y' (e.g., '9.16', '10.3')"}
            },
        )

        @model_validator(mode="after")
        def check_major_version_is_present_if_enabled(self):
            """Validator to ensure majorVersion exists if enabled is True."""
            if self.enabled and self.skye_major_version is None:
                raise ValueError("majorVersion must be provided when skyedoc import is enabled")
            return self

    class InnoveoPartnerHubConfig(BaseModel):
        """Configuration specific to Innoveo Partner Hub import."""

        enabled: bool

    class ImportsConfig(BaseModel):
        """Container for different import source configurations."""

        skyedoc: Optional["ImportRequest.SkyedocConfig"] = None
        innoveo_partner_hub: Optional["ImportRequest.InnoveoPartnerHubConfig"] = None

    markdown_split_headers: List[Literal["#", "##", "###"]]
    imports: ImportsConfig

    @classmethod
    @field_validator("split_headers")
    def check_split_headers_uniqueness(cls, value: List[Literal["#", "##", "###"]]):
        """Ensures that all values in split_headers are unique."""
        if len(set(value)) != len(value):
            raise ValueError("split_headers cannot contain duplicate values")
        return value


class CreateFeedbackRequest(BaseModel):
    vote: constants.VoteType = Field(
        ...,
        description="The nature of the feedback",
        examples=["positive", "negative", "not_specified"],
    )
    comment: Optional[str] = Field(
        description="Comment about the conversation",
        examples=["This was clearly false, the links are directing me to innoveo.skye.com/docs"],
        max_length=4000,
    )

    @model_validator(mode="after")
    def only_accepted_not_specified_if_there_is_a_comment(self):
        """Validator to ensure not specified is only allowed if there is a comment"""

        if not self.comment and self.vote == "not_specified":
            raise ValueError("Vote can only be 'not_specified' if there is a comment")
        return self
