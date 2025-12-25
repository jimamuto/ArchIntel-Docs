"""
Input Validation Middleware for ArchIntel Backend

This middleware provides comprehensive input validation for all API endpoints
including rate limiting, request size limits, and security validation.
"""

import logging
import time
from typing import Dict, List, Optional, Set
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.security_config import SecurityConfig, SecurityConstants
from schemas.security import ValidationError, SecurityValidationConfig


# Configure logging
middleware_logger = logging.getLogger("archintel.middleware")
middleware_logger.setLevel(logging.INFO)

if not middleware_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - MIDDLEWARE - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    middleware_logger.addHandler(handler)


class RateLimiter:
    """Rate limiting implementation for API endpoints"""
    
    def __init__(self, window_size: int = 60, max_attempts: int = 100, block_duration: int = 300):
        """
        Initialize rate limiter
        
        Args:
            window_size: Time window in seconds
            max_attempts: Maximum attempts per window
            block_duration: Block duration in seconds after limit exceeded
        """
        self.window_size = window_size
        self.max_attempts = max_attempts
        self.block_duration = block_duration
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocks: Dict[str, float] = {}
    
    def is_rate_limited(self, client_ip: str, endpoint: str) -> tuple[bool, int]:
        """
        Check if client is rate limited
        
        Returns:
            (is_limited, retry_after_seconds)
        """
        key = f"{client_ip}:{endpoint}"
        now = time.time()
        
        # Check if currently blocked
        if key in self.blocks:
            if now < self.blocks[key]:
                retry_after = int(self.blocks[key] - now)
                return True, retry_after
            else:
                del self.blocks[key]
        
        # Clean old requests
        cutoff = now - self.window_size
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # Check limit
        if len(self.requests[key]) >= self.max_attempts:
            self.blocks[key] = now + self.block_duration
            retry_after = self.block_duration
            return True, retry_after
        
        return False, 0
    
    def record_attempt(self, client_ip: str, endpoint: str, success: bool = True):
        """Record a request attempt"""
        key = f"{client_ip}:{endpoint}"
        now = time.time()
        
        # Clean old requests periodically
        if len(self.requests[key]) % 10 == 0:
            cutoff = now - self.window_size
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        self.requests[key].append(now)
        
        middleware_logger.info(
            f"Request recorded: {client_ip} -> {endpoint} (success: {success})"
        )


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive input validation"""
    
    def __init__(
        self, 
        app: ASGIApp,
        config: Optional[SecurityValidationConfig] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        super().__init__(app)
        self.config = config or SecurityValidationConfig()
        self.rate_limiter = rate_limiter or RateLimiter()
        
        # Endpoints that require stricter validation
        self.strict_endpoints = {
            '/projects',
            '/projects/{id}/ingest/code',
            '/docs/{project_id}/file/doc',
            '/docs/{project_id}/search'
        }
        
        # Endpoints that are read-only and less strict
        self.read_only_endpoints = {
            '/docs/{project_id}/file/code',
            '/projects/{id}/file/code'
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process incoming request with validation"""
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        
        # Skip validation for auth endpoints to prevent issues with 2FA flow
        if endpoint.startswith('/auth'):
            response = await call_next(request)
            return response
        
        # 1. Rate limiting check
        await self._check_rate_limit(client_ip, endpoint, request)
        
        # 2. Request size validation
        await self._validate_request_size(request)
        
        # 3. Content-Type validation
        self._validate_content_type(request)
        
        # 4. Path parameter validation
        self._validate_path_parameters(request)
        
        # 5. Query parameter validation
        await self._validate_query_parameters(request)
        
        # 6. Request body validation
        if request.method in ['POST', 'PUT', 'PATCH']:
            await self._validate_request_body(request)
        
        # 7. Security headers validation
        self._validate_security_headers(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers to response
        self._add_security_headers(response)
        
        # Log successful request
        middleware_logger.info(
            f"Request processed: {client_ip} -> {endpoint} [{request.method}] -> {response.status_code}"
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.client.host if request.client else 'unknown'

        return client_ip
    
    async def _check_rate_limit(self, client_ip: str, endpoint: str, request: Request):
        """Check rate limiting for the request"""
        # Skip rate limiting for certain endpoints
        if endpoint in ['/health', '/metrics', '/docs']:
            return
        
        # Check if endpoint requires stricter rate limiting
        if endpoint in self.strict_endpoints:
            # Use stricter limits for write operations
            is_limited, retry_after = self.rate_limiter.is_rate_limited(
                client_ip, f"{endpoint}_strict"
            )
        else:
            is_limited, retry_after = self.rate_limiter.is_rate_limited(client_ip, endpoint)
        
        if is_limited:
            middleware_logger.warning(
                f"Rate limit exceeded: {client_ip} -> {endpoint} (retry after {retry_after}s)"
            )
            
            error_response = ValidationError(
                error="RATE_LIMIT_EXCEEDED",
                message=SecurityConstants.RATE_LIMIT_ERROR,
                timestamp=datetime.utcnow().isoformat()
            )
            
            response = JSONResponse(
                status_code=429,
                content=error_response.dict(),
                headers={"Retry-After": str(retry_after)}
            )
            
            # Record failed attempt
            if endpoint in self.strict_endpoints:
                self.rate_limiter.record_attempt(client_ip, f"{endpoint}_strict", success=False)
            else:
                self.rate_limiter.record_attempt(client_ip, endpoint, success=False)
            
            raise HTTPException(response=response)
    
    async def _validate_request_size(self, request: Request):
        """Validate request size limits"""
        content_length = request.headers.get('Content-Length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.config.max_input_length:
                    middleware_logger.warning(
                        f"Request too large: {size} bytes > {self.config.max_input_length} bytes"
                    )
                    
                    error_response = ValidationError(
                        error="REQUEST_TOO_LARGE",
                        message=f"Request size too large. Maximum allowed: {self.config.max_input_length} bytes",
                        timestamp=datetime.utcnow().isoformat()
                    )
                    
                    raise HTTPException(status_code=413, detail=error_response.dict())
            except ValueError:
                # Invalid Content-Length header
                middleware_logger.warning("Invalid Content-Length header")
                raise HTTPException(status_code=400, detail="Invalid request headers")
    
    def _validate_content_type(self, request: Request):
        """Validate Content-Type for POST/PUT/PATCH requests"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '').lower()
            
            # Allow common content types
            allowed_types = [
                'application/json',
                'application/x-www-form-urlencoded',
                'multipart/form-data',
                'text/plain'
            ]
            
            if not any(allowed in content_type for allowed in allowed_types):
                middleware_logger.warning(f"Invalid Content-Type: {content_type}")
                
                error_response = ValidationError(
                    error="INVALID_CONTENT_TYPE",
                    message="Unsupported content type",
                    timestamp=datetime.utcnow().isoformat()
                )
                
                raise HTTPException(status_code=415, detail=error_response.dict())
    
    def _validate_path_parameters(self, request: Request):
        """Validate path parameters for security issues"""
        path = request.url.path
        
        # Check for blocked patterns in path
        for pattern in self.config.blocked_patterns:
            import re
            if re.search(pattern, path, re.IGNORECASE):
                middleware_logger.warning(f"Blocked pattern in path: {pattern} -> {path}")
                
                error_response = ValidationError(
                    error="INVALID_PATH",
                    message="Path contains blocked patterns",
                    timestamp=datetime.utcnow().isoformat()
                )
                
                raise HTTPException(status_code=400, detail=error_response.dict())
    
    async def _validate_query_parameters(self, request: Request):
        """Validate query parameters"""
        query_params = request.query_params
        
        for key, value in query_params.items():
            # Check parameter length
            if len(value) > self.config.max_query_length:
                middleware_logger.warning(
                    f"Query parameter too long: {key} ({len(value)} chars)"
                )
                
                error_response = ValidationError(
                    error="QUERY_TOO_LONG",
                    message=f"Query parameter '{key}' too long",
                    field=key,
                    value=value[:100] + "..." if len(value) > 100 else value,
                    timestamp=datetime.utcnow().isoformat()
                )
                
                raise HTTPException(status_code=400, detail=error_response.dict())
            
            # Check for blocked patterns
            for pattern in self.config.blocked_patterns:
                import re
                if re.search(pattern, value, re.IGNORECASE):
                    middleware_logger.warning(
                        f"Blocked pattern in query: {pattern} -> {key}={value}"
                    )
                    
                    error_response = ValidationError(
                        error="INVALID_QUERY",
                        message=f"Query parameter '{key}' contains blocked patterns",
                        field=key,
                        value=value,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    
                    raise HTTPException(status_code=400, detail=error_response.dict())
    
    async def _validate_request_body(self, request: Request):
        """Validate request body content"""
        try:
            # For JSON requests, we'll let Pydantic handle validation
            # This is a basic check for non-JSON requests
            content_type = request.headers.get('Content-Type', '').lower()
            
            if 'application/json' in content_type:
                # JSON validation will be handled by route handlers
                pass
            else:
                # For other content types, check for blocked patterns
                body = await request.body()
                body_str = body.decode('utf-8', errors='ignore')
                
                for pattern in self.config.blocked_patterns:
                    import re
                    if re.search(pattern, body_str, re.IGNORECASE):
                        middleware_logger.warning(
                            f"Blocked pattern in request body: {pattern}"
                        )
                        
                        error_response = ValidationError(
                            error="INVALID_BODY",
                            message="Request body contains blocked patterns",
                            timestamp=datetime.utcnow().isoformat()
                        )
                        
                        raise HTTPException(status_code=400, detail=error_response.dict())
        
        except Exception as e:
            middleware_logger.error(f"Error validating request body: {e}")
            raise HTTPException(status_code=400, detail="Invalid request body")
    
    def _validate_security_headers(self, request: Request):
        """Validate security-related headers"""
        # Check for CSRF token on state-changing operations
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            csrf_token = request.headers.get('X-CSRF-Token')
            if not csrf_token:
                # For API endpoints, CSRF is less critical but still good practice
                middleware_logger.warning(f"Missing CSRF token for {request.method} request")
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = SecurityConfig.SECURE_HEADERS
        
        for header, value in security_headers.items():
            if header not in response.headers:
                response.headers[header] = value
        
        # Add custom security headers
        response.headers['X-Content-Processing'] = 'ArchIntel-Secure'
        response.headers['X-Request-ID'] = str(hash(time.time()))[-8:]


# Global instances
rate_limiter = RateLimiter(
    window_size=SecurityConfig.RATE_LIMIT_WINDOW,
    max_attempts=SecurityConfig.RATE_LIMIT_MAX_ATTEMPTS,
    block_duration=SecurityConfig.RATE_LIMIT_BLOCK_DURATION
)