"""
Secure Error Handling Service for ArchIntel Backend

This module provides comprehensive error handling with:
- Generic error responses to prevent information disclosure
- Error classification and sanitization
- Structured security logging
- Error response formatting
- Security monitoring and alerting

Author: ArchIntel Security Team
Requirements: Secure error handling without information disclosure
"""

import logging
import os
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Import security utilities
from services.security_middleware import SecurityEventLogger

# Configure error logging
error_logger = logging.getLogger("archintel.errors")
security_logger = logging.getLogger("archintel.security")

# Error severity levels
ERROR_SEVERITY = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH", 
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
    "INFO": "INFO"
}

# Error categories
ERROR_CATEGORIES = {
    "SECURITY": "SECURITY",
    "SYSTEM": "SYSTEM", 
    "USER": "USER",
    "NETWORK": "NETWORK",
    "VALIDATION": "VALIDATION",
    "AUTHENTICATION": "AUTHENTICATION",
    "AUTHORIZATION": "AUTHORIZATION"
}

# Error codes mapping
ERROR_CODES = {
    # Authentication errors
    "AUTH_INVALID_TOKEN": "AUTH_INVALID_TOKEN",
    "AUTH_MISSING_TOKEN": "AUTH_MISSING_TOKEN", 
    "AUTH_EXPIRED_TOKEN": "AUTH_EXPIRED_TOKEN",
    "AUTH_INSUFFICIENT_PERMISSIONS": "AUTH_INSUFFICIENT_PERMISSIONS",
    
    # Authorization errors
    "ACCESS_DENIED": "ACCESS_DENIED",
    "RESOURCE_NOT_FOUND": "RESOURCE_NOT_FOUND",
    
    # Input validation errors
    "INVALID_INPUT": "INVALID_INPUT",
    "MISSING_REQUIRED_FIELD": "MISSING_REQUIRED_FIELD",
    "INVALID_FORMAT": "INVALID_FORMAT",
    
    # System errors
    "DATABASE_ERROR": "DATABASE_ERROR",
    "EXTERNAL_SERVICE_ERROR": "EXTERNAL_SERVICE_ERROR",
    "RATE_LIMIT_EXCEEDED": "RATE_LIMIT_EXCEEDED",
    "SYSTEM_UNAVAILABLE": "SYSTEM_UNAVAILABLE",
    
    # Security errors
    "SECURITY_ERROR": "SECURITY_ERROR",
    "CSRF_VIOLATION": "CSRF_VIOLATION",
    "PATH_TRAVERSAL_ATTEMPT": "PATH_TRAVERSAL_ATTEMPT",
    "SQL_INJECTION_ATTEMPT": "SQL_INJECTION_ATTEMPT",
    "XSS_ATTEMPT": "XSS_ATTEMPT",
    
    # Git/Repository errors
    "REPO_CLONE_FAILED": "REPO_CLONE_FAILED",
    "INVALID_REPOSITORY_URL": "INVALID_REPOSITORY_URL",
    "REPO_ACCESS_DENIED": "REPO_ACCESS_DENIED",
    
    # LLM/API errors
    "LLM_SERVICE_ERROR": "LLM_SERVICE_ERROR",
    "API_KEY_INVALID": "API_KEY_INVALID",
    "API_RATE_LIMITED": "API_RATE_LIMITED"
}

# User-friendly error messages (generic)
USER_ERROR_MESSAGES = {
    "AUTH_INVALID_TOKEN": "Authentication failed. Please log in again.",
    "AUTH_MISSING_TOKEN": "Authentication required. Please provide valid credentials.",
    "AUTH_EXPIRED_TOKEN": "Your session has expired. Please log in again.",
    "AUTH_INSUFFICIENT_PERMISSIONS": "You don't have permission to access this resource.",
    
    "ACCESS_DENIED": "Access to this resource is denied.",
    "RESOURCE_NOT_FOUND": "The requested resource was not found.",
    
    "INVALID_INPUT": "Invalid input provided. Please check your request.",
    "MISSING_REQUIRED_FIELD": "Required information is missing from your request.",
    "INVALID_FORMAT": "Input format is invalid. Please check the required format.",
    
    "DATABASE_ERROR": "A database error occurred. Please try again later.",
    "EXTERNAL_SERVICE_ERROR": "External service is temporarily unavailable.",
    "RATE_LIMIT_EXCEEDED": "Too many requests. Please wait before trying again.",
    "SYSTEM_UNAVAILABLE": "The service is temporarily unavailable. Please try again later.",
    
    "CSRF_VIOLATION": "Request validation failed. Please try again.",
    "PATH_TRAVERSAL_ATTEMPT": "Request validation failed. Please try again.",
    "SQL_INJECTION_ATTEMPT": "Request validation failed. Please try again.",
    "XSS_ATTEMPT": "Request validation failed. Please try again.",
    
    "REPO_CLONE_FAILED": "Failed to access repository. Please check the URL and permissions.",
    "INVALID_REPOSITORY_URL": "Repository URL format is invalid.",
    "REPO_ACCESS_DENIED": "Repository access is denied. Please check your credentials.",
    
    "LLM_SERVICE_ERROR": "AI service is currently unavailable. Please try again later.",
    "API_KEY_INVALID": "API service configuration error. Please contact support.",
    "API_RATE_LIMITED": "AI service is rate limited. Please try again later."
}

# Development environment check
DEBUG_MODE = os.getenv("ENVIRONMENT", "production").lower() == "development"


class SecurityError(Exception):
    """Base class for security-related errors"""
    def __init__(self, message: str, error_code: str, severity: str = "HIGH"):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        super().__init__(message)


class ErrorHandler:
    """Centralized error handling with security logging"""
    
    def __init__(self):
        self.error_count = 0
        self.security_events = []
        
    def handle_error(
        self, 
        error: Exception, 
        request: Optional[Request] = None,
        context: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and return secure error response
        
        Args:
            error: The exception to handle
            request: FastAPI request object
            context: Additional context about where the error occurred
            user_id: User ID if available
            
        Returns:
            Secure error response dictionary
        """
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Get request information
        client_ip = self._get_client_ip(request) if request else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown") if request else "unknown"
        request_path = request.url.path if request else "unknown"
        request_method = request.method if request else "unknown"
        
        # Classify the error
        error_info = self._classify_error(error, context)
        
        # Log the error for debugging (detailed logs)
        self._log_detailed_error(
            error_id, error, error_info, client_ip, user_id, 
            request_path, request_method, context
        )
        
        # Log security events
        if error_info["category"] == ERROR_CATEGORIES["SECURITY"]:
            SecurityEventLogger.log_auth_attempt(
                client_ip, user_id, False, request_path, 
                f"Security error: {error_info['message']}"
            )
        
        # Return secure error response
        return self._create_error_response(
            error_id, error_info, timestamp, request_path
        )
    
    def handle_http_exception(
        self, 
        exc: HTTPException, 
        request: Optional[Request] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle HTTP exceptions with security logging"""
        return self.handle_error(exc, request, "HTTP_ENDPOINT", user_id)
    
    def create_error_response(
        self, 
        error_id: str, 
        error_info: Dict[str, Any], 
        timestamp: str, 
        request_path: str
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "error": {
                "code": error_info["code"],
                "message": error_info["user_message"],
                "timestamp": timestamp,
                "request_id": error_id,
                "path": request_path
            }
        }
    
    def _classify_error(
        self, 
        error: Exception, 
        context: Optional[str]
    ) -> Dict[str, Any]:
        """Classify error and determine appropriate response"""
        
        # Determine error category and severity
        if isinstance(error, SecurityError):
            category = ERROR_CATEGORIES["SECURITY"]
            severity = error.severity
            error_code = error.error_code
            message = str(error.message)
            
        elif isinstance(error, HTTPException):
            category = ERROR_CATEGORIES["SYSTEM"]
            severity = self._get_http_error_severity(error.status_code)
            error_code = self._get_http_error_code(error.status_code)
            message = str(error.detail)
            
        elif isinstance(error, (ValueError, TypeError)):
            category = ERROR_CATEGORIES["VALIDATION"]
            severity = "MEDIUM"
            error_code = ERROR_CODES["INVALID_INPUT"]
            message = str(error)
            
        elif "database" in str(error).lower() or "sql" in str(error).lower():
            category = ERROR_CATEGORIES["SYSTEM"]
            severity = "HIGH"
            error_code = ERROR_CODES["DATABASE_ERROR"]
            message = "Database operation failed"
            
        elif "git" in str(error).lower() or "repository" in str(error).lower():
            category = ERROR_CATEGORIES["SYSTEM"]
            severity = "MEDIUM"
            error_code = ERROR_CODES["REPO_CLONE_FAILED"]
            message = "Repository operation failed"
            
        elif any(keyword in str(error).lower() for keyword in ["timeout", "connection", "network"]):
            category = ERROR_CATEGORIES["NETWORK"]
            severity = "MEDIUM"
            error_code = ERROR_CODES["EXTERNAL_SERVICE_ERROR"]
            message = "External service timeout"
            
        else:
            category = ERROR_CATEGORIES["SYSTEM"]
            severity = "MEDIUM"
            error_code = "INTERNAL_ERROR"
            message = "An internal error occurred"
        
        # Get user-friendly message
        user_message = USER_ERROR_MESSAGES.get(error_code, "An error occurred")
        
        return {
            "category": category,
            "severity": severity,
            "code": error_code,
            "message": message,
            "user_message": user_message,
            "context": context or "unknown"
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_http_error_severity(self, status_code: int) -> str:
        """Determine severity based on HTTP status code"""
        if status_code >= 500:
            return "HIGH"
        elif status_code >= 400:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_http_error_code(self, status_code: int) -> str:
        """Get error code based on HTTP status code"""
        if status_code == 400:
            return ERROR_CODES["INVALID_INPUT"]
        elif status_code == 401:
            return ERROR_CODES["AUTH_INVALID_TOKEN"]
        elif status_code == 403:
            return ERROR_CODES["AUTH_INSUFFICIENT_PERMISSIONS"]
        elif status_code == 404:
            return ERROR_CODES["RESOURCE_NOT_FOUND"]
        elif status_code == 429:
            return ERROR_CODES["RATE_LIMIT_EXCEEDED"]
        elif status_code >= 500:
            return ERROR_CODES["SYSTEM_UNAVAILABLE"]
        else:
            return "HTTP_ERROR"
    
    def _log_detailed_error(
        self, 
        error_id: str,
        error: Exception, 
        error_info: Dict[str, Any],
        client_ip: str,
        user_id: Optional[str],
        request_path: str,
        request_method: str,
        context: Optional[str]
    ):
        """Log detailed error information for debugging"""
        
        # Log to error logger
        error_logger.error(
            f"ERROR_ID: {error_id} | "
            f"Category: {error_info['category']} | "
            f"Severity: {error_info['severity']} | "
            f"Code: {error_info['code']} | "
            f"Message: {error_info['message']} | "
            f"IP: {client_ip} | "
            f"User: {user_id or 'ANON'} | "
            f"Path: {request_path} | "
            f"Method: {request_method} | "
            f"Context: {context or 'unknown'}"
        )
        
        # Log stack trace in development mode
        if DEBUG_MODE:
            error_logger.error(f"Stack trace for {error_id}:")
            error_logger.error(traceback.format_exc())
        
        # Log to security logger for security-related errors
        if error_info["category"] == ERROR_CATEGORIES["SECURITY"]:
            security_logger.warning(
                f"SECURITY_ERROR - ID: {error_id}, "
                f"Category: {error_info['category']}, "
                f"Severity: {error_info['severity']}, "
                f"Code: {error_info['code']}, "
                f"IP: {client_ip}, "
                f"User: {user_id or 'ANON'}, "
                f"Path: {request_path}"
            )
    
    def _create_error_response(
        self, 
        error_id: str, 
        error_info: Dict[str, Any], 
        timestamp: str, 
        request_path: str
    ) -> Dict[str, Any]:
        """Create secure error response"""
        return {
            "error": {
                "code": error_info["code"],
                "message": error_info["user_message"],
                "timestamp": timestamp,
                "request_id": error_id,
                "path": request_path
            }
        }
    
    def sanitize_error_message(self, message: str) -> str:
        """Sanitize error messages to remove sensitive information"""
        # Remove potential sensitive information
        sensitive_patterns = [
            r"password.*=.*['\"][^'\"]*['\"]",  # Passwords
            r"token.*=.*['\"][^'\"]*['\"]",     # Tokens
            r"key.*=.*['\"][^'\"]*['\"]",       # Keys
            r"secret.*=.*['\"][^'\"]*['\"]",    # Secrets
            r"database.*=.*['\"][^'\"]*['\"]",  # Database connections
        ]
        
        sanitized = message
        for pattern in sensitive_patterns:
            sanitized = sanitized.replace(pattern, "***REDACTED***")
        
        # Remove stack traces
        if "Traceback" in sanitized:
            sanitized = sanitized.split("Traceback")[0]
        
        # Limit message length
        if len(sanitized) > 200:
            sanitized = sanitized[:200] + "..."
        
        return sanitized
    
    def log_security_event(
        self, 
        event_type: str, 
        ip: str, 
        user_id: Optional[str], 
        details: str
    ):
        """Log security events for monitoring"""
        security_logger.warning(
            f"SECURITY_EVENT - Type: {event_type}, "
            f"IP: {ip}, User: {user_id or 'ANON'}, "
            f"Details: {details}"
        )


# Global error handler instance
error_handler = ErrorHandler()


def create_error_response(
    error_code: str, 
    message: Optional[str] = None, 
    status_code: int = 500,
    request: Optional[Request] = None
) -> JSONResponse:
    """
    Create a standardized error response
    
    Args:
        error_code: Standardized error code
        message: Optional custom message (will be sanitized)
        status_code: HTTP status code
        request: FastAPI request object for context
        
    Returns:
        JSONResponse with error details
    """
    if message:
        message = error_handler.sanitize_error_message(message)
    else:
        message = USER_ERROR_MESSAGES.get(error_code, "An error occurred")
    
    timestamp = datetime.utcnow().isoformat()
    error_id = str(uuid.uuid4())
    
    response_content = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": timestamp,
            "request_id": error_id,
            "path": request.url.path if request else "unknown"
        }
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_content,
        headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        }
    )


def handle_security_error(
    error_type: str, 
    details: str, 
    request: Optional[Request] = None,
    user_id: Optional[str] = None
) -> JSONResponse:
    """
    Handle security-related errors with logging
    
    Args:
        error_type: Type of security error
        details: Error details for logging
        request: FastAPI request object
        user_id: User ID if available
        
    Returns:
        JSONResponse with generic security error
    """
    client_ip = error_handler._get_client_ip(request) if request else "unknown"
    
    # Log security event
    error_handler.log_security_event(error_type, client_ip, user_id, details)
    
    # Return generic error response
    return create_error_response(
        ERROR_CODES.get(error_type, "SECURITY_ERROR"),
        "Request validation failed. Please try again.",
        400,
        request
    )