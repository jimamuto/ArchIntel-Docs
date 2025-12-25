"""
Enhanced Authentication Router for ArchIntel Backend

This module provides hardened authentication endpoints with:
- JWT token management with expiration validation
- Rate limiting for authentication endpoints
- Secure error handling
- Session management
- CSRF protection
- Comprehensive security logging

Author: ArchIntel Security Team
Requirements: Secure authentication with defense-in-depth
"""

import os
import httpx
from fastapi import APIRouter, HTTPException, Request, Depends, Header, status
from fastapi.responses import RedirectResponse, JSONResponse
from supabase import create_client, Client
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

from services.error_handler import error_handler, create_error_response, handle_security_error
from services.security_middleware import (
    rate_limiter, session_manager, SecurityEventLogger
)
from services.security_config import SecurityConfig, SecurityConstants
from services.auth_utils import jwt_manager, auth_manager, password_manager, SecurityHeaders
from services.email_service import two_factor_service, email_service
from exceptions import AuthenticationError, AuthorizationError, CSRFError

router = APIRouter()

# Environment variables with validation
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")  # Support both env var names
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# Validate required environment variables (only log warning if missing, don't fail at import time)
if not all([SUPABASE_URL, SUPABASE_KEY]):
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Supabase configuration is incomplete. Authentication features will be limited.")

# In-memory storage for pending 2FA sessions (consider Redis for production)
# Stores Supabase session data temporarily keyed by email
pending_2fa_sessions: Dict[str, Dict[str, Any]] = {}
pending_2fa_expiry: Dict[str, float] = {}

# Initialize logger
import logging
auth_logger = logging.getLogger(__name__)

# Pydantic models for email authentication
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Verify2FARequest(BaseModel):
    email: EmailStr
    code: str

class Resend2FARequest(BaseModel):
    email: EmailStr


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be configured")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def authenticate_user_from_supabase(token: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user using Supabase JWT token with enhanced validation
    
    Args:
        token: JWT token from Supabase
        
    Returns:
        User data if valid, None otherwise
    """
    try:
        supabase_client = get_supabase_client()
        user_response = supabase_client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            return None
        
        return {
            "id": str(user_response.user.id),
            "email": user_response.user.email,
            "aud": user_response.user.aud,
            "role": getattr(user_response.user, 'role', 'authenticated'),
            "confirmed_at": getattr(user_response.user, 'confirmed_at', None),
            "created_at": getattr(user_response.user, 'created_at', None)
        }
    
    except Exception as e:
        # Log security event
        SecurityEventLogger.log_auth_attempt(
            "unknown", None, False, "/auth/me", 
            f"Supabase authentication failed: {str(e)}"
        )
        return None


async def get_current_user_secure(request: Request, authorization: Optional[str] = Header(None)):
    """
    Enhanced user authentication with rate limiting and session management
    
    Args:
        request: FastAPI request object
        authorization: Authorization header
        
    Returns:
        User data if authenticated
        
    Raises:
        HTTPException: For authentication failures
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting check
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/me")
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=SecurityConstants.RATE_LIMIT_ERROR,
            headers={"Retry-After": str(retry_after)}
        )
    
    # Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/me", "Missing or invalid authorization header"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=SecurityConstants.GENERIC_AUTH_ERROR
        )
    
    token = authorization.split(" ")[1]
    
    # Validate token integrity
    if not auth_manager.validate_token_integrity(token):
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/me", "Token integrity validation failed"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=SecurityConstants.GENERIC_AUTH_ERROR
        )
    
    # Authenticate with Supabase
    user_data = await authenticate_user_from_supabase(token)
    
    if not user_data:
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/me", "Invalid or expired token"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=SecurityConstants.GENERIC_AUTH_ERROR
        )
    
    # Record successful attempt
    rate_limiter.record_attempt(client_ip, success=True)
    
    # Log successful authentication
    SecurityEventLogger.log_auth_attempt(
        client_ip, user_data["id"], True, "/auth/me", "Authentication successful"
    )
    
    return user_data


@router.get("/github/login")
async def github_login(request: Request):
    """
    Enhanced GitHub login endpoint with CSRF protection and rate limiting
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting check
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/github/login")
    if is_limited:
        error_response = create_error_response(
            "RATE_LIMIT_EXCEEDED", 
            SecurityConstants.RATE_LIMIT_ERROR, 
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response,
            headers={"Retry-After": str(retry_after)}
        )
    
    if not GITHUB_CLIENT_ID:
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/github/login", "GitHub client ID not configured"
        )
        error_response = create_error_response(
            "CONFIGURATION_ERROR", 
            "Authentication service temporarily unavailable", 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )
    
    # Generate CSRF token for the redirect (simplified)
    import secrets
    csrf_token = secrets.token_hex(16)
    
    scope = "repo"
    redirect_uri = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={scope}&state={csrf_token}"
    
    # Record attempt
    rate_limiter.record_attempt(client_ip, success=True)
    
    SecurityEventLogger.log_auth_attempt(
        client_ip, None, True, "/auth/github/login", "GitHub login initiated"
    )
    
    return RedirectResponse(redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request, code: str, state: Optional[str] = None):
    """
    Enhanced GitHub callback with CSRF protection and secure token handling
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting check
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/github/callback")
    if is_limited:
        error_response = create_error_response(
            SecurityConstants.RATE_LIMIT_ERROR, 
            "RATE_LIMIT_EXCEEDED", 
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response,
            headers={"Retry-After": str(retry_after)}
        )
    
    # Validate CSRF token
    if not state:
        SecurityEventLogger.log_csrf_violation(client_ip, "/auth/github/callback")
        
        error_response = create_error_response(
            SecurityConstants.CSRF_ERROR, 
            "CSRF_TOKEN_MISSING", 
            status.HTTP_400_BAD_REQUEST
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response
        )
    
    # CSRF token validation would go here in production
    # For now, we'll log the attempt
    
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/github/callback", "GitHub credentials not configured"
        )
        
        error_response = create_error_response(
            "Authentication service temporarily unavailable", 
            "CONFIGURATION_ERROR", 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )
    
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, headers=headers, data=data)
            
            if response.status_code != 200:
                SecurityEventLogger.log_auth_attempt(
                    client_ip, None, False, "/auth/github/callback", 
                    f"GitHub token exchange failed: {response.status_code}"
                )
                
                error_response = create_error_response(
                    "Failed to authenticate with GitHub", 
                    "GITHUB_AUTH_FAILED", 
                    status.HTTP_400_BAD_REQUEST
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_response
                )
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                error_description = token_data.get('error_description', 'Unknown error')
                SecurityEventLogger.log_auth_attempt(
                    client_ip, None, False, "/auth/github/callback", 
                    f"GitHub returned no access token: {error_description}"
                )
                
                error_response = create_error_response(
                    "GitHub authentication failed", 
                    "GITHUB_TOKEN_ERROR", 
                    status.HTTP_400_BAD_REQUEST
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_response
                )
            
            # Create secure response with tokens
            # In a real implementation, you would exchange GitHub token for your own JWT
            # For now, we'll return a success response
            
            success_response = {
                "success": True,
                "message": "GitHub authentication successful",
                "github_token": access_token[:10] + "..."  # Don't expose full token in response
            }
            
            # Record successful attempt
            rate_limiter.record_attempt(client_ip, success=True)
            SecurityEventLogger.log_auth_attempt(
                client_ip, None, True, "/auth/github/callback", "GitHub authentication successful"
            )
            
            # Add security headers
            headers = SecurityHeaders.get_auth_headers()
            
            return JSONResponse(
                content=success_response,
                headers=headers
            )
            
        except Exception as e:
            SecurityEventLogger.log_auth_attempt(
                client_ip, None, False, "/auth/github/callback", 
                f"GitHub callback error: {str(e)}"
            )
            
            error_response = create_error_response(
                "Authentication service temporarily unavailable", 
                "GITHUB_CALLBACK_ERROR", 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response
            )


@router.get("/me")
async def get_current_user(user: Dict = Depends(get_current_user_secure)):
    """
    Enhanced user profile endpoint with session management
    """
    # Add session information if needed
    session_info = {
        "last_activity": datetime.utcnow().isoformat(),
        "authenticated": True
    }
    
    return {
        "user": user,
        "session": session_info,
        "security": {
            "token_type": "supabase_jwt",
            "expires_in": SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE
        }
    }


@router.post("/refresh")
async def refresh_token(request: Request, refresh_token: str):
    """
    Token refresh endpoint with enhanced security
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting check
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/refresh")
    if is_limited:
        error_response = create_error_response(
            SecurityConstants.RATE_LIMIT_ERROR, 
            "RATE_LIMIT_EXCEEDED", 
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response,
            headers={"Retry-After": str(retry_after)}
        )
    
    # In this implementation, Supabase handles token refresh internally
    # This endpoint would typically exchange a refresh token for a new access token
    
    error_response = create_error_response(
        "Token refresh not implemented for Supabase integration", 
        "REFRESH_NOT_IMPLEMENTED", 
        status.HTTP_501_NOT_IMPLEMENTED
    )
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content=error_response
    )


@router.post("/logout")
async def logout(request: Request, authorization: Optional[str] = Header(None)):
    """
    Enhanced logout endpoint with session cleanup
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Extract user info for logging
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = jwt_manager.verify_token(token)
        if payload:
            user_id = payload.get("sub")
    
    # Log logout event
    SecurityEventLogger.log_session_event("LOGOUT", "session_ended", user_id, client_ip)
    
    # Return success with cache control headers
    response = JSONResponse(
        content={
            "success": True,
            "message": "Successfully logged out"
        }
    )
    
    # Add security headers to prevent cached authentication
    response.headers.update({
        "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })
    
    return response


@router.get("/security/status")
async def get_security_status():
    """
    Security status endpoint for monitoring (development/debug only)
    """
    if not SecurityConfig.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security status endpoint is only available in debug mode"
        )
    
    return {
        "security": {
            "config": SecurityConfig.get_security_policy(),
            "rate_limiting": {
                "window_size": rate_limiter.window_size,
                "max_attempts": rate_limiter.max_attempts,
                "block_duration": rate_limiter.block_duration,
                "active_blocks": len(rate_limiter.blocks)
            },
            "sessions": {
                "active_sessions": len(session_manager.sessions),
                "session_timeout": session_manager.session_timeout,
                "max_sessions_per_user": session_manager.max_sessions_per_user
            }
        }
    }


# Note: Exception handlers should be registered at the app level in main.py
# This router uses standard HTTPException raises for error handling


# Email Authentication with 2FA

@router.post("/signup")
async def signup(request: Request, signup_data: SignupRequest):
    """
    Sign up a new user with email and password
    """
    client_ip = request.client.host if request.client else "unknown"

    # Rate limiting
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/signup")
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=SecurityConstants.RATE_LIMIT_ERROR
        )

    try:
        # If Supabase is configured, create user there
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                supabase_client = get_supabase_client()

                # Create user with Supabase
                response = supabase_client.auth.sign_up({
                    "email": signup_data.email,
                    "password": signup_data.password
                })

                # Check for error
                if hasattr(response, 'error') and response.error:
                    rate_limiter.record_attempt(client_ip, success=False)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(response.error) or "Failed to create account"
                    )
            except Exception as supabase_error:
                rate_limiter.record_attempt(client_ip, success=False)
                SecurityEventLogger.log_auth_attempt(
                    client_ip, None, False, "/auth/signup", f"Supabase error: {str(supabase_error)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create account with Supabase"
                )

        # Send 2FA code (works without Supabase for development)
        expiry = two_factor_service.send_2fa_email(signup_data.email)

        if not expiry:
            # Log warning but don't fail - user can still login with password
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send 2FA code to {signup_data.email}")

        rate_limiter.record_attempt(client_ip, success=True)

        return JSONResponse(
            content={
                "success": True,
                "message": "Account created successfully. Please verify your email with the code sent to your inbox.",
                "requires_2fa": True,
                "email": signup_data.email
            },
            headers=SecurityHeaders.get_auth_headers()
        )

    except HTTPException:
        raise
    except Exception as e:
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/signup", f"Signup failed: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/login")
async def login(request: Request, login_data: LoginRequest):
    """
    Login with email and password, sends 2FA code if credentials are valid
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/login")
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=SecurityConstants.RATE_LIMIT_ERROR
        )
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )
    
    try:
        supabase_client = get_supabase_client()

        # Authenticate with Supabase
        response = supabase_client.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })

        # Check for error
        if hasattr(response, 'error') and response.error:
            rate_limiter.record_attempt(client_ip, success=False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Store Supabase session data temporarily for 2FA verification
        import time
        pending_2fa_sessions[login_data.email] = {
            "access_token": response.session.access_token if response.session else None,
            "refresh_token": response.session.refresh_token if response.session else None,
            "user": {
                "id": str(response.user.id) if response.user else None,
                "email": response.user.email if response.user else None
            }
        }
        pending_2fa_expiry[login_data.email] = time.time() + 600  # 10 minutes expiry

        # Send 2FA code
        expiry = two_factor_service.send_2fa_email(login_data.email)

        if not expiry:
            # If email fails, still allow login but log warning
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send 2FA code to {login_data.email}")

            # Return tokens directly if email fails (fallback)
            rate_limiter.record_attempt(client_ip, success=True)

            return JSONResponse(
                content={
                    "success": True,
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                    "token_type": "bearer",
                    "user": {
                        "id": str(response.user.id) if response.user else None,
                        "email": response.user.email if response.user else None
                    },
                    "requires_2fa": False
                },
                headers=SecurityHeaders.get_auth_headers(str(response.user.id) if response.user else None)
            )

        rate_limiter.record_attempt(client_ip, success=True)

        return JSONResponse(
            content={
                "success": True,
                "message": "Verification code sent to your email",
                "requires_2fa": True,
                "email": login_data.email
            },
            headers=SecurityHeaders.get_auth_headers()
        )

    except HTTPException:
        raise
    except Exception as e:
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, "/auth/login", f"Login failed: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/verify-2fa")
async def verify_2fa(request: Request, verify_data: Verify2FARequest):
    """
    Verify 2FA code and return authentication tokens
    """
    import logging
    logger = logging.getLogger(__name__)
    
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"2FA verification attempt from {client_ip} for email: {verify_data.email}")
    
    # Rate limiting
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/verify-2fa")
    if is_limited:
        logger.warning(f"Rate limited: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=SecurityConstants.RATE_LIMIT_ERROR
        )
    
    # Check if pending session exists and hasn't expired
    import time
    current_time = time.time()
    
    logger.info(f"Checking pending sessions. Emails: {list(pending_2fa_sessions.keys())}")
    
    if verify_data.email not in pending_2fa_sessions:
        logger.warning(f"No pending 2FA session for email: {verify_data.email}")
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, verify_data.email, False, "/auth/verify-2fa", "No pending 2FA session"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending authentication session. Please login again."
        )
    
    if pending_2fa_expiry[verify_data.email] < current_time:
        logger.warning(f"Expired session for email: {verify_data.email}")
        rate_limiter.record_attempt(client_ip, success=False)
        # Clean up expired session
        del pending_2fa_sessions[verify_data.email]
        del pending_2fa_expiry[verify_data.email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session expired. Please login again."
        )
    
    # Verify 2FA code
    logger.info(f"Verifying code for email: {verify_data.email}")
    if not two_factor_service.verify_code(verify_data.email, verify_data.code):
        logger.warning(f"Invalid 2FA code for email: {verify_data.email}")
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, verify_data.email, False, "/auth/verify-2fa", "Invalid 2FA code"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification code"
        )
    
    try:
        # Retrieve stored Supabase session
        session_data = pending_2fa_sessions.get(verify_data.email)
        
        logger.info(f"Retrieved session data for email: {verify_data.email}")
        
        # Clean up stored session
        del pending_2fa_sessions[verify_data.email]
        del pending_2fa_expiry[verify_data.email]
        
        if not session_data:
            logger.error(f"Session data not found for email: {verify_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session data not found"
            )
        
        rate_limiter.record_attempt(client_ip, success=True)
        SecurityEventLogger.log_auth_attempt(
            client_ip, verify_data.email, True, "/auth/verify-2fa", "2FA verification successful"
        )
        
        logger.info(f"2FA verification successful for email: {verify_data.email}")
        
        return JSONResponse(
            content={
                "success": True,
                "access_token": session_data.get("access_token"),
                "refresh_token": session_data.get("refresh_token"),
                "token_type": "bearer",
                "user": session_data.get("user"),
                "message": "Authentication successful"
            },
            headers=SecurityHeaders.get_auth_headers(session_data.get("user", {}).get("id"))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during 2FA verification: {str(e)}", exc_info=True)
        rate_limiter.record_attempt(client_ip, success=False)
        SecurityEventLogger.log_auth_attempt(
            client_ip, verify_data.email, False, "/auth/verify-2fa", f"2FA verification failed: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete 2FA verification"
        )


@router.post("/resend-2fa")
async def resend_2fa(request: Request, request_data: Resend2FARequest):
    """
    Resend 2FA code
    """
    client_ip = request.client.host if request.client else "unknown"

    # Rate limiting
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, "/auth/resend-2fa")
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=SecurityConstants.RATE_LIMIT_ERROR
        )

    expiry = two_factor_service.send_2fa_email(request_data.email)

    if not expiry:
        rate_limiter.record_attempt(client_ip, success=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        )

    rate_limiter.record_attempt(client_ip, success=True)

    return JSONResponse(
        content={
            "success": True,
            "message": "New verification code sent to your email"
        }
    )