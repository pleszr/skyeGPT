class StoreManagementException(Exception):
    """Custom exception raised when an operation fails during store management."""
    def __init__(self, message: str = None):
        super().__init__(message)

    def __str__(self):
        return f"{super().__str__()}"
