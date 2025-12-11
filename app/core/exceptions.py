"""Domain and application exception types.

Use RCode-like structure for error identification.
"""

from typing import Optional


class AppError(Exception):
    def __init__(self, message: str, rcode: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.rcode = rcode or "APP_000"


class AuthorizationError(AppError):
    def __init__(
        self, message: str = "Unauthorized", rcode: Optional[str] = "AUTH_001"
    ):
        super().__init__(message, rcode)


class ValidationError(AppError):
    def __init__(
        self, message: str = "Validation failed", rcode: Optional[str] = "VAL_001"
    ):
        super().__init__(message, rcode)
