from typing import Any, Dict, Optional


class EnmaskError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(EnmaskError):
    def __init__(self, message: str = "Authentication failed", **kwargs: Any):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(EnmaskError):
    def __init__(self, message: str = "Insufficient permissions", **kwargs: Any):
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(EnmaskError):
    def __init__(self, resource: str = "Resource", **kwargs: Any):
        super().__init__(f"{resource} not found", status_code=404, **kwargs)


class ValidationError(EnmaskError):
    def __init__(self, message: str = "Validation error", **kwargs: Any):
        super().__init__(message, status_code=422, **kwargs)


class RateLimitError(EnmaskError):
    def __init__(self, message: str = "Rate limit exceeded", **kwargs: Any):
        super().__init__(message, status_code=429, **kwargs)


class ServerError(EnmaskError):
    def __init__(self, message: str = "Internal server error", **kwargs: Any):
        super().__init__(message, status_code=500, **kwargs)


class ConnectionError(EnmaskError):
    def __init__(self, message: str = "Connection failed", **kwargs: Any):
        super().__init__(message, status_code=None, **kwargs)
