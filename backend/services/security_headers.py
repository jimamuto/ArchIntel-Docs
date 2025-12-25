"""
Security Headers Middleware for ArchIntel Backend

This module provides security headers middleware to enhance response security
by adding appropriate HTTP security headers to all responses.

Author: ArchIntel Security Team
Requirements: Security headers for response hardening
"""

import os
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses"""
    
    def __init__(self):
        # Security configuration from environment or defaults
        self.csp_policy = os.getenv("CONTENT_SECURITY_POLICY", 
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';"
        )
        self.frame_options = os.getenv("X_FRAME_OPTIONS", "DENY")
        self.xss_protection = os.getenv("X_XSS_PROTECTION", "1; mode=block")
        self.content_type_options = os.getenv("X_CONTENT_TYPE_OPTIONS", "nosniff")
        self.referrer_policy = os.getenv("REFERRER_POLICY", "strict-origin-when-cross-origin")
        self.hsts_max_age = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
        self.hsts_include_subdomains = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
        
        # Development mode check
        self.debug_mode = os.getenv("ENVIRONMENT", "production").lower() == "development"
    
    async def __call__(self, request: Request, call_next):
        """Process request and add security headers to response"""
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        # Remove server information in production
        if not self.debug_mode:
            response.headers.pop("server", None)
        
        return response
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers to response"""
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = self.frame_options
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = self.xss_protection
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = self.content_type_options
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = self.referrer_policy
        
        # Strict-Transport-Security (HSTS)
        hsts_value = f"max-age={self.hsts_max_age}"
        if self.hsts_include_subdomains:
            hsts_value += "; includeSubDomains"
        response.headers["Strict-Transport-Security"] = hsts_value
        
        # X-Permitted-Cross-Domain-Policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # X-Download-Options
        response.headers["X-Download-Options"] = "noopen"
        
        # Clear-Site-Data (for logout endpoints)
        # This can be conditionally added based on the endpoint
        
        # Permissions-Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=()"
        )
        
        # Cache-Control for sensitive endpoints
        # This can be conditionally set based on authentication requirements
    
    def get_security_headers(self) -> dict:
        """Get current security headers configuration"""
        return {
            "Content-Security-Policy": self.csp_policy,
            "X-Frame-Options": self.frame_options,
            "X-XSS-Protection": self.xss_protection,
            "X-Content-Type-Options": self.content_type_options,
            "Referrer-Policy": self.referrer_policy,
            "Strict-Transport-Security": f"max-age={self.hsts_max_age}" + 
                ("; includeSubDomains" if self.hsts_include_subdomains else ""),
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), "
                "accelerometer=()"
            )
        }


class CORSHeadersMiddleware:
    """Enhanced CORS middleware with security features"""
    
    def __init__(self, allowed_origins: list = None, allow_credentials: bool = True):
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]
        self.allow_credentials = allow_credentials
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        origin = request.headers.get("origin")
        
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            
            # Only add these headers if credentials are allowed
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = (
                    "Content-Type, Authorization, X-Requested-With, "
                    "X-CSRF-Token, X-Content-Type-Options"
                )
                response.headers["Access-Control-Expose-Headers"] = "X-Content-Type-Options"
        
        return response


# Global security headers instance
security_headers = SecurityHeadersMiddleware()
cors_headers = CORSHeadersMiddleware()


def get_security_headers() -> dict:
    """Get security headers for manual application"""
    return security_headers.get_security_headers()