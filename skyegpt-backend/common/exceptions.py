"""Custom exceptions used throughout the SkyeGPT backend."""


class SkyeGptException(Exception):
    """Base class for all custom exceptions in SkyeGPT."""

    def __init__(self, message: str = None):
        """Initialize the exception with an optional message."""
        super().__init__(message)
        self.message = message

    def __str__(self):
        """Return the string representation of the exception."""
        return super().__str__()


class CollectionNotFoundError(SkyeGptException):
    """Custom exception raised when a Chroma collection is not found during deletion."""


class DocumentDBError(SkyeGptException):
    """Custom exception raised when there is a Document DB related error."""


class ResponseGenerationError(SkyeGptException):
    """Custom exception raised when there is an error generating response to the user's question."""


class StoreManagementException(SkyeGptException):
    """Custom exception raised when an operation fails during store management."""


class UsageLimitExceededError(SkyeGptException):
    """Custom exception raised when a usage limit was exceeded."""


class VectorDBError(SkyeGptException):
    """Custom exception raised for Vector DB related operations."""


class ObjectNotFoundError(SkyeGptException):
    """Custom exception when an object is not found in a database and returning None is not an option."""
