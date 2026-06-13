from typing import Any, Dict, Optional


class EnmaskException(Exception):
    """Base exception for Enmask platform."""
    pass


class DatabaseConnectionError(EnmaskException):
    """Raised when a database connection fails."""
    pass


class RuleValidationError(EnmaskException):
    """Raised when a masking rule is invalid."""
    pass


class JobExecutionError(EnmaskException):
    """Raised when a masking job fails during execution."""
    pass


class ResourceNotFoundError(EnmaskException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        self.message = f"{resource_type} with ID {resource_id} not found."
        super().__init__(self.message)


class AuthenticationError(EnmaskException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(EnmaskException):
    """Raised when a user lacks permission for an action."""
    pass


class ValidationError(EnmaskException):
    """Raised when input data fails validation."""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        self.details = details or {}
        super().__init__(message)


class RateLimitExceeded(EnmaskException):
    """Raised when rate limit is exceeded."""
    def __init__(self, limit: str, window: str):
        self.message = f"Rate limit exceeded: {limit} per {window}."
        super().__init__(self.message)


class MaskingError(EnmaskException):
    """Raised when a masking operation fails."""
    def __init__(self, table: str, column: str, reason: str):
        self.message = f"Masking failed on {table}.{column}: {reason}"
        super().__init__(self.message)


class PluginError(EnmaskException):
    """Raised when a plugin operation fails."""
    def __init__(self, plugin_name: str, reason: str):
        self.message = f"Plugin '{plugin_name}' error: {reason}"
        super().__init__(self.message)


class ComplianceViolationError(EnmaskException):
    """Raised when an action violates a compliance framework requirement."""
    def __init__(self, framework: str, rule: str, details: Optional[str] = None):
        self.framework = framework
        self.rule = rule
        self.message = f"Compliance violation [{framework}] {rule}"
        if details:
            self.message += f": {details}"
        super().__init__(self.message)


class VaultError(EnmaskException):
    """Raised when vault encryption/decryption or storage fails."""
    pass


class ConfigurationError(EnmaskException):
    """Raised when application configuration is invalid."""
    pass
