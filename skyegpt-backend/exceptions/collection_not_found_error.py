class CollectionNotFoundError(Exception):
    """Custom exception raised when a Chroma collection is not found during deletion."""
    def __init__(self, message: str = None):
        super().__init__(message)

    def __str__(self):
        return f"{super().__str__()}"
