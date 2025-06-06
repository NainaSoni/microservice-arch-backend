from enum import Enum
from typing import Optional, Any, Dict

class ErrorCode(Enum):
    # General errors (1000-1999)
    INTERNAL_ERROR = 1000
    VALIDATION_ERROR = 1001
    NOT_FOUND_ERROR = 1002
    DUPLICATE_DATA_ERROR = 1003
    DATABASE_ERROR = 1004
    NO_DATA_FOUND_ERROR = 1005
    CONNECTION_ERROR = 1006
    AUTHENTICATION_ERROR = 1007
    AUTHORIZATION_ERROR = 1008
    RATE_LIMIT_ERROR = 1009

    # Member service errors (2000-2999)
    MEMBER_NOT_FOUND = 2000
    MEMBER_ALREADY_EXISTS = 2001
    INVALID_MEMBER_DATA = 2002

    # Feedback service errors (3000-3999)
    FEEDBACK_NOT_FOUND = 3000
    FEEDBACK_ALREADY_EXISTS = 3001
    INVALID_FEEDBACK_DATA = 3002

class ServiceException(Exception):
    """Base exception for all service-related errors."""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(ServiceException):
    """Raised when input validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)

class NotFoundError(ServiceException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.NOT_FOUND_ERROR, details)

class InternalError(ServiceException):
    """Raised when an internal server error occurs."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.INTERNAL_ERROR, details)

class DuplicateDataError(ServiceException):
    """Raised when attempting to create a duplicate record."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.DUPLICATE_DATA_ERROR, details)

class DatabaseError(ServiceException):
    """Raised when a database operation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.DATABASE_ERROR, details)

class NoDataFoundError(ServiceException):
    """Raised when no data is found for a query."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.NO_DATA_FOUND_ERROR, details)

class ConnectionError(ServiceException):
    """Raised when a connection to an external service fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.CONNECTION_ERROR, details)

class AuthenticationError(ServiceException):
    """Raised when authentication fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.AUTHENTICATION_ERROR, details)

class AuthorizationError(ServiceException):
    """Raised when authorization fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.AUTHORIZATION_ERROR, details)

class RateLimitError(ServiceException):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.RATE_LIMIT_ERROR, details) 