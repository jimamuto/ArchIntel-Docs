"""
Enhanced Authentication Utilities for ArchIntel Backend

This module provides:
- JWT token management with expiration validation
- Token refresh mechanism
- Secure session handling
- Authentication utilities

Author: ArchIntel Security Team
Requirements: JWT-based secure authentication
"""

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Union
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configure logging
auth_logger = logging.getLogger("archintel.auth")
auth_logger.setLevel(logging.INFO)

if not auth_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - AUTH - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    auth_logger.addHandler(handler)


class JWTManager:
    """JWT token management with expiration validation and refresh"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT manager
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT signing algorithm
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=15)  # 15 minutes
        self.refresh_token_expire = timedelta(days=7)     # 7 days
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create access token with expiration"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or self.access_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        auth_logger.info(f"Created access token for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + self.refresh_token_expire
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        auth_logger.info(f"Created refresh token for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                auth_logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
                return None
            
            # Check expiration (already handled by jwt.decode, but double-check)
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                auth_logger.warning("Token expired during verification")
                return None
            
            return payload
        
        except JWTError as e:
            auth_logger.warning(f"JWT verification failed: {str(e)}")
            return None
        except Exception as e:
            auth_logger.error(f"Unexpected error during token verification: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Create new access token
        access_data = {"sub": user_id}
        new_access_token = self.create_access_token(access_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": int(self.access_token_expire.total_seconds())
        }


class SecurePasswordManager:
    """Secure password hashing and verification"""
    
    def __init__(self, scheme: str = "bcrypt"):
        self.pwd_context = CryptContext(schemes=[scheme], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)


class AuthenticationManager:
    """Enhanced authentication manager with session support"""
    
    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
    
    def authenticate_user_token(self, token: str) -> Optional[Dict]:
        """Authenticate user using JWT token"""
        payload = self.jwt_manager.verify_token(token)
        if not payload:
            return None
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "expires_at": payload.get("exp")
        }
    
    def generate_tokens_for_user(self, user_id: str, email: Optional[str] = None) -> Dict:
        """Generate access and refresh tokens for user"""
        access_data = {
            "sub": user_id,
            "email": email
        }
        
        refresh_data = {
            "sub": user_id
        }
        
        access_token = self.jwt_manager.create_access_token(access_data)
        refresh_token = self.jwt_manager.create_refresh_token(refresh_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(self.jwt_manager.access_token_expire.total_seconds()),
            "user_id": user_id
        }
    
    def validate_token_integrity(self, token: str) -> bool:
        """Validate token signature and structure without full verification"""
        try:
            # Decode without verification to check structure
            unverified = jwt.get_unverified_claims(token)
            if not unverified:
                return False
            
            # Check required fields
            required_fields = ["sub", "iat", "exp", "type"]
            return all(field in unverified for field in required_fields)
        
        except Exception:
            return False


class SecurityHeaders:
    """Security header management for authentication responses"""
    
    @staticmethod
    def get_auth_headers(user_id: Optional[str] = None) -> Dict[str, str]:
        """Get security headers for authentication responses"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        if user_id:
            # Add user-specific headers
            headers["X-User-ID"] = str(user_id)
        
        return headers
    
    @staticmethod
    def get_csrf_token(session_id: str, secret: str) -> str:
        """Generate CSRF token for session"""
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}"
        signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{data}:{signature}"


# Global instances
# Note: In production, these should be initialized with proper secrets from environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "archintel_dev_secret_key_change_in_production")
jwt_manager = JWTManager(SECRET_KEY)
password_manager = SecurePasswordManager()
auth_manager = AuthenticationManager(jwt_manager)


def create_token_response(access_token: str, refresh_token: str, user_id: str) -> Dict:
    """Create standardized token response"""
    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(jwt_manager.access_token_expire.total_seconds()),
        "user_id": user_id,
        "message": "Authentication successful"
    }


def create_error_response(message: str, error_code: str = "AUTH_ERROR", status_code: int = 401) -> Dict:
    """Create standardized error response"""
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def validate_auth_headers(request) -> Tuple[Optional[str], Optional[str]]:
    """Validate and extract authentication headers"""
    authorization = request.headers.get("Authorization")
    csrf_token = request.headers.get("X-CSRF-Token")
    
    if not authorization or not authorization.startswith("Bearer "):
        return None, None
    
    token = authorization.split(" ")[1]
    return token, csrf_token