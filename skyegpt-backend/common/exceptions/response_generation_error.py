class ResponseGenerationError(Exception):
    """Custom exception raised when there is an error generating response to the user's question"""
    def __init__(self, message: str = None):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{super().__str__()}"
