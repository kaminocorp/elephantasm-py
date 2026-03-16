"""Custom exception hierarchy for Elephantasm SDK."""


class ElephantasmError(Exception):
    """Base exception for all Elephantasm errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(ElephantasmError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class NotFoundError(ElephantasmError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitError(ElephantasmError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ValidationError(ElephantasmError):
    """Raised when request validation fails (422)."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class ServerError(ElephantasmError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str = "Server error"):
        super().__init__(message, status_code=500)
