"""
Custom Exception Classes for ArchIntel Backend

This module defines custom exception classes for different error scenarios
with proper categorization and security handling.

Author: ArchIntel Security Team
Requirements: Structured exception handling for security
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException
from services.error_handler import ERROR_SEVERITY, ERROR_CATEGORIES, ERROR_CODES


class SecurityError(Exception):
    """Base security-related exception"""
    def __init__(
        self, 
        message: str, 
        error_code: str = ERROR_CODES["SECURITY_ERROR"], 
        severity: str = ERROR_SEVERITY["HIGH"]
    ):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        super().__init__(message)


class AuthenticationError(SecurityError):
    """Authentication-related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code=ERROR_CODES["AUTH_INVALID_TOKEN"],
            severity=ERROR_SEVERITY["HIGH"]
        )


class AuthorizationError(SecurityError):
    """Authorization-related errors"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code=ERROR_CODES["AUTH_INSUFFICIENT_PERMISSIONS"],
            severity=ERROR_SEVERITY["HIGH"]
        )


class CSRFError(SecurityError):
    """CSRF protection violations"""
    def __init__(self, message: str = "CSRF token validation failed"):
        super().__init__(
            message=message,
            error_code=ERROR_CODES["CSRF_VIOLATION"],
            severity=ERROR_SEVERITY["MEDIUM"]
        )


class PathTraversalError(SecurityError):
    """Path traversal attempt detection"""
    def __init__(self, message: str = "Invalid file path detected"):
        super().__init__(
            message=message,
            error_code=ERROR_CODES["PATH_TRAVERSAL_ATTEMPT"],
            severity=ERROR_SEVERITY["HIGH"]
        )


class InputValidationError(Exception):
    """Input validation errors"""
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        error_code: str = ERROR_CODES["INVALID_INPUT"]
    ):
        self.message = message
        self.field = field
        self.error_code = error_code
        super().__init__(message)


class RepositoryError(Exception):
    """Repository-related errors"""
    def __init__(
        self, 
        message: str, 
        repo_url: Optional[str] = None,
        error_code: str = ERROR_CODES["REPO_CLONE_FAILED"]
    ):
        self.message = message
        self.repo_url = repo_url
        self.error_code = error_code
        super().__init__(message)


class DatabaseError(Exception):
    """Database operation errors"""
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        error_code: str = ERROR_CODES["DATABASE_ERROR"]
    ):
        self.message = message
        self.operation = operation
        self.error_code = error_code
        super().__init__(message)


class ServiceUnavailableError(Exception):
    """External service unavailability"""
    def __init__(
        self, 
        message: str, 
        service: Optional[str] = None,
        error_code: str = ERROR_CODES["EXTERNAL_SERVICE_ERROR"]
    ):
        self.message = message
        self.service = service
        self.error_code = error_code
        super().__init__(message)


class RateLimitError(Exception):
    """Rate limiting violations"""
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        error_code: str = ERROR_CODES["RATE_LIMIT_EXCEEDED"]
    ):
        self.message = message
        self.retry_after = retry_after
        self.error_code = error_code
        super().__init__(message)


class ConfigurationError(Exception):
    """Configuration-related errors"""
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        error_code: str = "CONFIGURATION_ERROR"
    ):
        self.message = message
        self.config_key = config_key
        self.error_code = error_code
        super().__init__(message)


class SecurityValidationError(Exception):
    """Security validation failures"""
    def __init__(
        self, 
        message: str, 
        validation_type: Optional[str] = None,
        error_code: str = ERROR_CODES["SECURITY_ERROR"]
    ):
        self.message = message
        self.validation_type = validation_type
        self.error_code = error_code
        super().__init__(message)


# HTTP Exception Mapping
def create_http_exception(
    status_code: int,
    detail: str,
    headers: Optional[Dict[str, str]] = None
) -> HTTPException:
    """Create standardized HTTP exceptions"""
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


# Specific HTTP Exception Factories
def unauthorized_exception() -> HTTPException:
    """Create unauthorized (401) exception"""
    return create_http_exception(
        status_code=401,
        detail="Authentication required"
    )


def forbidden_exception() -> HTTPException:
    """Create forbidden (403) exception"""
    return create_http_exception(
        status_code=403,
        detail="Access denied"
    )


def not_found_exception(resource: str = "Resource") -> HTTPException:
    """Create not found (404) exception"""
    return create_http_exception(
        status_code=404,
        detail=f"{resource} not found"
    )


def conflict_exception(message: str = "Resource conflict") -> HTTPException:
    """Create conflict (409) exception"""
    return create_http_exception(
        status_code=409,
        detail=message
    )


def too_many_requests_exception(retry_after: int = 60) -> HTTPException:
    """Create too many requests (429) exception"""
    return create_http_exception(
        status_code=429,
        detail="Too many requests. Please try again later.",
        headers={"Retry-After": str(retry_after)}
    )


def internal_server_error() -> HTTPException:
    """Create internal server error (500) exception"""
    return create_http_exception(
        status_code=500,
        detail="Internal server error"
    )


def service_unavailable() -> HTTPException:
    """Create service unavailable (503) exception"""
    return create_http_exception(
        status_code=503,
        detail="Service temporarily unavailable"
    )


# Exception Context Manager
class ExceptionHandler:
    """Context manager for handling exceptions with proper logging"""
    
    def __init__(self, context: str, user_id: Optional[str] = None):
        self.context = context
        self.user_id = user_id
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True
        
        # Import error handler here to avoid circular imports
        from services.error_handler import error_handler
        
        # Handle the exception
        if exc_type.__name__ in ["SecurityError", "AuthenticationError", "AuthorizationError"]:
            # Re-raise security exceptions for proper handling
            return False
        else:
            # Log and handle other exceptions
            error_handler.handle_error(
                exc_val, 
                context=self.context,
                user_id=self.user_id
            )
            return True