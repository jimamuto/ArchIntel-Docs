"""
Security Middleware for ArchIntel Backend

This module provides comprehensive security middleware including:
- Rate limiting for authentication endpoints
- Secure error handling
- Security headers
- CSRF protection
- Session management

Author: ArchIntel Security Team
Requirements: Defense-in-depth authentication security
"""

import asyncio
import hashlib
import hmac
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

# Configure security logging
security_logger = logging.getLogger("archintel.security")
security_logger.setLevel(logging.INFO)

if not security_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)


class SecurityEventLogger:
    """Centralized security event logging"""
    
    @staticmethod
    def log_auth_attempt(ip: str, user_id: Optional[str], success: bool, endpoint: str, error: Optional[str] = None):
        """Log authentication attempts"""
        event_type = "AUTH_SUCCESS" if success else "AUTH_FAILURE"
        security_logger.info(
            f"{event_type} - IP: {ip}, User: {user_id or 'ANON'}, "
            f"Endpoint: {endpoint}, Error: {error or 'None'}"
        )
    
    @staticmethod
    def log_rate_limit_violation(ip: str, endpoint: str, attempts: int):
        """Log rate limiting violations"""
        security_logger.warning(
            f"RATE_LIMIT_VIOLATION - IP: {ip}, Endpoint: {endpoint}, Attempts: {attempts}"
        )
    
    @staticmethod
    def log_csrf_violation(ip: str, endpoint: str):
        """Log CSRF violations"""
        security_logger.warning(f"CSRF_VIOLATION - IP: {ip}, Endpoint: {endpoint}")
    
    @staticmethod
    def log_session_event(event_type: str, session_id: str, user_id: Optional[str], ip: str):
        """Log session events"""
        security_logger.info(
            f"SESSION_{event_type} - Session: {session_id}, User: {user_id or 'ANON'}, IP: {ip}"
        )


class RateLimiter:
    """Advanced rate limiting with progressive delays and IP-based throttling"""
    
    def __init__(self, window_size: int = 60, max_attempts: int = 5, block_duration: int = 300):
        """
        Initialize rate limiter
        
        Args:
            window_size: Time window in seconds
            max_attempts: Maximum attempts per window
            block_duration: Block duration in seconds after violation
        """
        self.window_size = window_size
        self.max_attempts = max_attempts
        self.block_duration = block_duration
        
        # In-memory storage (consider Redis for production)
        self.attempts: Dict[str, List[float]] = defaultdict(list)
        self.blocks: Dict[str, float] = {}
        
        # Progressive delay configuration
        self.progressive_delays = [0, 1, 2, 4, 8, 16]
    
    def is_rate_limited(self, identifier: str, endpoint: str) -> tuple[bool, Optional[int]]:
        """
        Check if request should be rate limited
        
        Returns:
            (is_limited, retry_after_seconds)
        """
        current_time = time.time()
        
        # Check if IP is currently blocked
        if identifier in self.blocks:
            if current_time < self.blocks[identifier]:
                retry_after = int(self.blocks[identifier] - current_time) + 1
                return True, retry_after
            else:
                del self.blocks[identifier]
        
        # Clean old attempts
        cutoff_time = current_time - self.window_size
        self.attempts[identifier] = [t for t in self.attempts[identifier] if t > cutoff_time]
        
        # Check attempt count
        attempt_count = len(self.attempts[identifier])
        
        if attempt_count >= self.max_attempts:
            # Block the IP
            self.blocks[identifier] = current_time + self.block_duration
            SecurityEventLogger.log_rate_limit_violation(identifier, endpoint, attempt_count)
            return True, self.block_duration
        
        return False, None
    
    def record_attempt(self, identifier: str, success: bool = False):
        """Record an authentication attempt"""
        if not success:
            self.attempts[identifier].append(time.time())
    
    def get_progressive_delay(self, identifier: str) -> int:
        """Get progressive delay for failed attempts"""
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        self.attempts[identifier] = [t for t in self.attempts[identifier] if t > cutoff_time]
        
        attempt_count = len(self.attempts[identifier])
        if attempt_count >= len(self.progressive_delays):
            return self.progressive_delays[-1]
        
        return self.progressive_delays[attempt_count]


class SessionManager:
    """Secure session management with timeout and validation"""
    
    def __init__(self, session_timeout: int = 1800, max_sessions_per_user: int = 5):
        """
        Initialize session manager
        
        Args:
            session_timeout: Session timeout in seconds (default 30 minutes)
            max_sessions_per_user: Maximum concurrent sessions per user
        """
        self.session_timeout = session_timeout
        self.max_sessions_per_user = max_sessions_per_user
        
        # In-memory session storage (consider Redis for production)
        self.sessions: Dict[str, Dict] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
    
    def create_session(self, user_id: str, ip: str, user_agent: str) -> str:
        """Create a new session"""
        session_id = self._generate_session_id()
        
        # Clean up old sessions for this user if limit exceeded
        if len(self.user_sessions[user_id]) >= self.max_sessions_per_user:
            self._cleanup_old_sessions(user_id)
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "ip": ip,
            "user_agent": user_agent,
            "active": True
        }
        
        self.sessions[session_id] = session_data
        self.user_sessions[user_id].add(session_id)
        
        SecurityEventLogger.log_session_event("CREATED", session_id, user_id, ip)
        return session_id
    
    def validate_session(self, session_id: str, ip: str, user_agent: str) -> Optional[Dict]:
        """Validate and update session"""
        if session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        
        # Check if session is active
        if not session_data.get("active", True):
            return None
        
        # Check timeout
        now = datetime.utcnow()
        if now - session_data["last_activity"] > timedelta(seconds=self.session_timeout):
            self.invalidate_session(session_id)
            return None
        
        # Check IP consistency (optional security feature)
        if session_data["ip"] != ip:
            # Log potential session hijacking
            SecurityEventLogger.log_session_event("HIJACK_ATTEMPT", session_id, session_data["user_id"], ip)
            return None
        
        # Update last activity
        session_data["last_activity"] = now
        
        return session_data
    
    def invalidate_session(self, session_id: str):
        """Invalidate a specific session"""
        if session_id in self.sessions:
            user_id = self.sessions[session_id]["user_id"]
            session_data = self.sessions.pop(session_id)
            
            if session_id in self.user_sessions[user_id]:
                self.user_sessions[user_id].remove(session_id)
            
            SecurityEventLogger.log_session_event("INVALIDATED", session_id, user_id, session_data["ip"])
    
    def invalidate_all_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user"""
        session_ids = list(self.user_sessions[user_id])
        for session_id in session_ids:
            self.invalidate_session(session_id)
        
        SecurityEventLogger.log_session_event("INVALIDATED_ALL", "ALL", user_id, "SYSTEM")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if now - session_data["last_activity"] > timedelta(seconds=self.session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return hashlib.sha256(
            f"{uuid.uuid4()}{time.time()}".encode()
        ).hexdigest()
    
    def _cleanup_old_sessions(self, user_id: str):
        """Clean up oldest sessions when limit is exceeded"""
        sessions = sorted(
            self.user_sessions[user_id],
            key=lambda sid: self.sessions[sid]["created_at"]
        )
        
        while len(self.user_sessions[user_id]) >= self.max_sessions_per_user:
            old_session_id = sessions.pop(0)
            self.invalidate_session(old_session_id)


class SecureErrorMiddleware(BaseHTTPMiddleware):
    """Middleware for secure error handling and response sanitization"""
    
    def __init__(self, app, enable_detailed_errors: bool = False):
        super().__init__(app)
        self.enable_detailed_errors = enable_detailed_errors
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Log the error details
            self._log_error(request, e)
            
            # Return sanitized error response
            return self._create_secure_error_response(e, request)
        except Exception as e:
            # Log unexpected errors
            self._log_error(request, e, is_internal=True)
            
            # Return generic error response
            return self._create_generic_error_response(request)
    
    def _log_error(self, request: Request, error: Exception, is_internal: bool = False):
        """Log error details for security analysis"""
        error_type = "INTERNAL_ERROR" if is_internal else "HTTP_ERROR"
        security_logger.error(
            f"{error_type} - Path: {request.url.path}, "
            f"Method: {request.method}, IP: {self._get_client_ip(request)}, "
            f"Error: {str(error)[:200]}"  # Truncate long error messages
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _create_secure_error_response(self, error: HTTPException, request: Request) -> Response:
        """Create secure error response without exposing sensitive information"""
        error_response = {
            "error": {
                "code": error.status_code,
                "message": self._get_safe_error_message(error.status_code),
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
        
        # Include error details only in development
        if self.enable_detailed_errors and os.getenv("ENVIRONMENT") == "development":
            error_response["error"]["details"] = str(error.detail)
        
        return JSONResponse(
            status_code=error.status_code,
            content=error_response,
            headers={"X-Content-Type-Options": "nosniff"}
        )
    
    def _create_generic_error_response(self, request: Request) -> Response:
        """Create generic error response for unexpected errors"""
        error_response = {
            "error": {
                "code": 500,
                "message": "An internal server error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
                "request_id": str(uuid.uuid4())
            }
        }
        
        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={"X-Content-Type-Options": "nosniff"}
        )
    
    def _get_safe_error_message(self, status_code: int) -> str:
        """Get safe error message based on status code"""
        error_messages = {
            400: "Bad request",
            401: "Authentication required",
            403: "Access forbidden",
            404: "Resource not found",
            429: "Too many requests",
            500: "Internal server error"
        }
        return error_messages.get(status_code, "An error occurred")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        # Remove server information
        response.headers.pop("server", None)
        
        # Add security headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class CSRFProtection:
    """CSRF token generation and validation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for a session"""
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{data}:{signature}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return False
            
            token_session_id, timestamp, signature = parts
            
            # Check session ID match
            if token_session_id != session_id:
                return False
            
            # Check timestamp (5 minute window)
            token_time = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - token_time) > 300:
                return False
            
            # Validate signature
            data = f"{token_session_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key,
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception:
            return False


# Global instances
rate_limiter = RateLimiter()
session_manager = SessionManager()
csrf_protection = CSRFProtection(os.getenv("SECRET_KEY", "archintel_secret_key"))