"""
Enhanced Security Headers Middleware for ArchIntel Backend

This module provides comprehensive security headers middleware to protect against
common web vulnerabilities including XSS, clickjacking, MIME sniffing, and
protocol downgrade attacks.

Author: ArchIntel Security Team
Requirements: Comprehensive security headers implementation
"""

import os
import re
from typing import Dict, List, Optional, Union
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import ClientDisconnect
from starlette.datastructures import MutableHeaders
import logging

# Configure security logging
security_logger = logging.getLogger("archintel.security")
security_logger.setLevel(logging.INFO)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enhanced security headers middleware with CSP and environment-specific configuration"""
    
    def __init__(self, app):
        super().__init__(app)
        self.debug_mode = os.getenv("ENVIRONMENT", "production").lower() == "development"
        self.environment = os.getenv("ENVIRONMENT", "production").lower()
        
        # Initialize security headers configuration
        self._init_security_headers()
    
    def _init_security_headers(self):
        """Initialize security headers configuration based on environment"""
        
        # Base CSP policy
        base_csp = "default-src 'self'"
        
        if self.debug_mode:
            # Development mode - relaxed CSP for debugging
            self.csp_policy = (
                f"{base_csp}; "
                f"script-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
                f"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                f"img-src 'self' data: https:; "
                f"font-src 'self' https://fonts.gstatic.com; "
                f"connect-src 'self' https: ws: wss:; "
                f"frame-ancestors 'none'; "
                f"base-uri 'self'; "
                f"object-src 'none'; "
                f"media-src 'self' data: blob:; "
                f"report-uri /api/v1/csp-report; "
                f"report-to csp-endpoint"
            )
        else:
            # Production mode - strict CSP
            self.csp_policy = (
                f"{base_csp}; "
                f"script-src 'self' 'nonce-{self._generate_nonce()}'; "
                f"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                f"img-src 'self' data: https://api.github.com https://avatars.githubusercontent.com; "
                f"font-src 'self' https://fonts.gstatic.com; "
                f"connect-src 'self' https://api.groq.com https://api.github.com https://api.openai.com; "
                f"frame-ancestors 'none'; "
                f"base-uri 'self'; "
                f"object-src 'none'; "
                f"media-src 'self' data:; "
                f"report-uri /api/v1/csp-report; "
                f"report-to csp-endpoint"
            )
        
        # Other security headers
        self.security_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
                "magnetometer=(), gyroscope=(), accelerometer=(), "
                "interest-cohort=(), sync-xhr=()"
            )
        }
        
        # HSTS configuration
        self.hsts_max_age = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
        self.hsts_include_subdomains = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
        self.hsts_preload = os.getenv("HSTS_PRELOAD", "true").lower() == "true"
        
        # Additional headers for HTTPS
        if self.environment == "production":
            self.security_headers["Strict-Transport-Security"] = self._build_hsts_header()
    
    def _generate_nonce(self) -> str:
        """Generate a nonce for CSP inline scripts"""
        import secrets
        return secrets.token_urlsafe(16)
    
    def _build_hsts_header(self) -> str:
        """Build HSTS header value"""
        hsts_parts = [f"max-age={self.hsts_max_age}"]
        
        if self.hsts_include_subdomains:
            hsts_parts.append("includeSubDomains")
        
        if self.hsts_preload:
            hsts_parts.append("preload")
        
        return "; ".join(hsts_parts)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers to response"""
        try:
            response = await call_next(request)
            self._add_security_headers(response, request)
            return response
            
        except ClientDisconnect:
            # Handle client disconnect gracefully
            security_logger.debug(f"Client disconnected during request: {request.url.path}")
            return Response(status_code=499)  # Client Closed Request
            
        except Exception as e:
            security_logger.error(f"Error in security headers middleware: {e}")
            # Still try to return a response with headers
            response = Response(
                content="Internal Server Error",
                status_code=500,
                media_type="text/plain"
            )
            self._add_security_headers(response, request)
            return response

    def _add_security_headers(self, response: Response, request: Request):
        """Add security headers to response"""
        
        # Add CSP header
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Add other security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Remove server information in production
        if self.environment == "production":
            if "server" in response.headers:
                del response.headers["server"]
            if "x-powered-by" in response.headers:
                del response.headers["x-powered-by"]
        
        # Add cache control for sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # Add security headers for authentication endpoints
        if self._is_auth_endpoint(request.url.path):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
    
    def _is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint handles sensitive data"""
        sensitive_patterns = [
            r'/auth/',
            r'/api/v1/auth/',
            r'/api/v1/users/',
            r'/admin/',
            r'/api/v1/admin/',
            r'/api/v1/system/',
            r'/api/v1/csp-report'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, path):
                return True
        return False
    
    def _is_auth_endpoint(self, path: str) -> bool:
        """Check if endpoint is authentication-related"""
        auth_patterns = [
            r'/auth/login',
            r'/auth/logout', 
            r'/auth/register',
            r'/auth/refresh',
            r'/auth/reset-password'
        ]
        
        for pattern in auth_patterns:
            if re.search(pattern, path):
                return True
        return False
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get current security headers configuration"""
        headers = {
            "Content-Security-Policy": self.csp_policy,
            **self.security_headers
        }
        
        if self.environment == "production":
            headers["Strict-Transport-Security"] = self._build_hsts_header()
        
        return headers
    
    def update_csp_policy(self, new_policy: str):
        """Update CSP policy (for dynamic CSP updates)"""
        self.csp_policy = new_policy
        security_logger.info(f"CSP policy updated: {new_policy}")


class CSPReportingMiddleware(BaseHTTPMiddleware):
    """Middleware specifically for handling CSP violation reports"""
    
    def __init__(self, app):
        super().__init__(app)
        self.report_count = 0
        self.logger = logging.getLogger("archintel.csp")
    
    async def dispatch(self, request: Request, call_next):
        """Handle CSP violation reports"""
        
        # Check if this is a CSP violation report
        if self._is_csp_report(request):
            return await self._handle_csp_report(request)
        
        # Normal request processing
        response = await call_next(request)
        return response
    
    def _is_csp_report(self, request: Request) -> bool:
        """Check if request is a CSP violation report"""
        content_type = request.headers.get("Content-Type", "")
        path = request.url.path
        
        return (
            path == "/api/v1/csp-report" and 
            ("application/csp-report" in content_type or "application/json" in content_type)
        )
    
    async def _handle_csp_report(self, request: Request) -> Response:
        """Handle CSP violation report"""
        try:
            # Parse the report
            if "application/csp-report" in request.headers.get("Content-Type", ""):
                report_data = await request.json()
                csp_report = report_data.get("csp-report", {})
            else:
                csp_report = await request.json()
            
            # Log the violation
            self._log_csp_violation(request, csp_report)
            
            # Return success response
            return Response(
                content="CSP violation report received",
                status_code=204  # No Content
            )
            
        except Exception as e:
            self.logger.error(f"Error processing CSP report: {e}")
            return Response(
                content="Error processing CSP report",
                status_code=400,
                media_type="text/plain"
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

    def _log_csp_violation(self, request: Request, report: Dict):
        """Log CSP violation details"""
        self.report_count += 1
        
        violation_details = {
            "violated_directive": report.get("violated-directive", ""),
            "blocked_uri": report.get("blocked-uri", ""),
            "document_uri": report.get("document-uri", ""),
            "source_file": report.get("source-file", ""),
            "line_number": report.get("line-number", ""),
            "column_number": report.get("column-number", ""),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        self.logger.warning(f"CSP Violation #{self.report_count}: {violation_details}")
        
        try:
            import sys
            
            # Try to access security_monitor from the running application if available
            try:
                # Try to find it in loaded modules
                for module_name, module in sys.modules.items():
                    if 'security_monitoring' in module_name and hasattr(module, 'security_monitor'):
                        module.security_monitor.record_event("CSP_VIOLATION", violation_details)
                        return
            except Exception:
                pass
                    
        except Exception:
            pass  # Security monitoring not available


# Global middleware instances
security_headers_middleware = None  # Will be initialized in main.py
csp_reporting_middleware = None  # Will be initialized in main.py


def get_security_headers_config() -> Dict[str, str]:
    """Get security headers configuration"""
    if security_headers_middleware:
        return security_headers_middleware.get_security_headers()
    return {}


def validate_security_headers(headers: Dict[str, str]) -> List[str]:
    """Validate security headers configuration"""
    issues = []
    
    required_headers = [
        "Content-Security-Policy",
        "X-Frame-Options", 
        "X-Content-Type-Options",
        "X-XSS-Protection"
    ]
    
    for header in required_headers:
        if header not in headers:
            issues.append(f"Missing required header: {header}")
    
    # Validate CSP policy
    csp = headers.get("Content-Security-Policy", "")
    if "default-src" not in csp:
        issues.append("CSP policy missing default-src directive")
    
    if "object-src" not in csp:
        issues.append("CSP policy missing object-src directive")
    
    # Validate X-Frame-Options
    x_frame = headers.get("X-Frame-Options", "")
    if x_frame not in ["DENY", "SAMEORIGIN"]:
        issues.append("X-Frame-Options should be DENY or SAMEORIGIN")
    
    return issues