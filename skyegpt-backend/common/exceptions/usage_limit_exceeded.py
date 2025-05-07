class UsageLimitExceededError(Exception):
    """Custom exception raised when a usage limit was exceeded"""
    def __init__(self, message: str = None):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{super().__str__()}"
