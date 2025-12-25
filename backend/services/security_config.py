"""
Security Configuration for ArchIntel Backend

This module provides centralized security configuration including:
- Security policies and constants
- Configuration validation
- Security settings management

Author: ArchIntel Security Team
Requirements: Centralized security configuration management
"""

import os
from typing import Dict, List, Optional


class SecurityConfig:
    """Security configuration constants and policies"""
    
    # Authentication Security
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "1800"))  # 30 minutes
    MAX_SESSIONS_PER_USER = int(os.getenv("MAX_SESSIONS_PER_USER", "5"))
    JWT_ACCESS_TOKEN_EXPIRE = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE", "900"))  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRE = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE", "604800"))  # 7 days
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 1 minute
    RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "5"))
    RATE_LIMIT_BLOCK_DURATION = int(os.getenv("RATE_LIMIT_BLOCK_DURATION", "300"))  # 5 minutes
    
    # Security Headers
    SECURE_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    # Allowed File Extensions for Code Analysis
    ALLOWED_EXTENSIONS = [
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.cs', '.vb',
        '.html', '.htm', '.css', '.scss', '.sass', '.less', '.json', '.xml',
        '.yml', '.yaml', '.md', '.txt', '.sql', '.sh', '.bash', '.zsh'
    ]
    
    # Security Events
    LOG_LEVEL = os.getenv("SECURITY_LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("SECURITY_LOG_FILE", "security.log")
    
    # CSRF Protection
    CSRF_TOKEN_EXPIRE = int(os.getenv("CSRF_TOKEN_EXPIRE", "300"))  # 5 minutes
    
    # Password Security
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_NUMBERS = os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
    # Security Monitoring
    ERROR_THRESHOLD = int(os.getenv("ERROR_THRESHOLD", "10"))
    TIME_WINDOW = int(os.getenv("TIME_WINDOW", "300"))  # 5 minutes
    BRUTE_FORCE_THRESHOLD = int(os.getenv("BRUTE_FORCE_THRESHOLD", "5"))
    RATE_LIMIT_ABUSE_THRESHOLD = int(os.getenv("RATE_LIMIT_ABUSE_THRESHOLD", "3"))
    
    # Token Security
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate security configuration and return list of issues"""
        issues = []
        
        # Validate required environment variables
        if not cls.SECRET_KEY and cls.ENVIRONMENT == "production":
            issues.append("JWT_SECRET_KEY is required in production environment")
        
        if len(cls.SECRET_KEY or "") < 32 and cls.ENVIRONMENT == "production":
            issues.append("JWT_SECRET_KEY should be at least 32 characters long in production")
        
        # Validate numerical values
        if cls.SESSION_TIMEOUT < 300:  # 5 minutes minimum
            issues.append("SESSION_TIMEOUT should be at least 300 seconds (5 minutes)")
        
        if cls.MAX_SESSIONS_PER_USER < 1:
            issues.append("MAX_SESSIONS_PER_USER should be at least 1")
        
        if cls.JWT_ACCESS_TOKEN_EXPIRE < 300:  # 5 minutes minimum
            issues.append("JWT_ACCESS_TOKEN_EXPIRE should be at least 300 seconds (5 minutes)")
        
        if cls.RATE_LIMIT_MAX_ATTEMPTS < 1:
            issues.append("RATE_LIMIT_MAX_ATTEMPTS should be at least 1")
        
        if cls.RATE_LIMIT_BLOCK_DURATION < 60:  # 1 minute minimum
            issues.append("RATE_LIMIT_BLOCK_DURATION should be at least 60 seconds")
        
        return issues
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def get_security_policy(cls) -> Dict:
        """Get current security policy configuration"""
        return {
            "session_timeout": cls.SESSION_TIMEOUT,
            "max_sessions_per_user": cls.MAX_SESSIONS_PER_USER,
            "jwt_expiration": {
                "access_token": cls.JWT_ACCESS_TOKEN_EXPIRE,
                "refresh_token": cls.JWT_REFRESH_TOKEN_EXPIRE
            },
            "rate_limiting": {
                "window": cls.RATE_LIMIT_WINDOW,
                "max_attempts": cls.RATE_LIMIT_MAX_ATTEMPTS,
                "block_duration": cls.RATE_LIMIT_BLOCK_DURATION
            },
            "password_policy": {
                "min_length": cls.PASSWORD_MIN_LENGTH,
                "require_uppercase": cls.PASSWORD_REQUIRE_UPPERCASE,
                "require_lowercase": cls.PASSWORD_REQUIRE_LOWERCASE,
                "require_numbers": cls.PASSWORD_REQUIRE_NUMBERS,
                "require_special": cls.PASSWORD_REQUIRE_SPECIAL
            },
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG
        }


class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, List[str]]:
        """
        Validate password against security policy
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            issues.append(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters long")
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL and not any(not c.isalnum() for c in password):
            issues.append("Password must contain at least one special character")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_user_input(input_string: str, max_length: int = 255) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(input_string, str):
            input_string = str(input_string)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in input_string if ord(char) >= 32 and ord(char) <= 126)
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()


class SecurityConstants:
    """Security event constants and messages"""
    
    # Authentication Events
    AUTH_SUCCESS = "AUTH_SUCCESS"
    AUTH_FAILURE = "AUTH_FAILURE"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_REVOKED = "AUTH_REVOKED"
    
    # Security Events
    RATE_LIMIT_VIOLATION = "RATE_LIMIT_VIOLATION"
    CSRF_VIOLATION = "CSRF_VIOLATION"
    SESSION_HIJACK_ATTEMPT = "SESSION_HIJACK_ATTEMPT"
    TOKEN_MANIPULATION = "TOKEN_MANIPULATION"
    PATH_TRAVERSAL_ATTEMPT = "PATH_TRAVERSAL_ATTEMPT"
    
    # Error Messages
    GENERIC_AUTH_ERROR = "Authentication failed"
    RATE_LIMIT_ERROR = "Too many requests. Please try again later."
    CSRF_ERROR = "Invalid or missing CSRF token"
    SESSION_EXPIRED_ERROR = "Session expired. Please log in again."
    TOKEN_EXPIRED_ERROR = "Token expired"
    PERMISSION_DENIED_ERROR = "Access denied"
    
    # Security Headers
    SECURITY_HEADERS = [
        "X-Content-Type-Options",
        "X-Frame-Options", 
        "X-XSS-Protection",
        "Referrer-Policy",
        "Content-Security-Policy",
        "Strict-Transport-Security"
    ]


# Initialize and validate security configuration
def init_security_config():
    """Initialize and validate security configuration"""
    issues = SecurityConfig.validate_config()
    
    if issues:
        print("Security Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
        
        if SecurityConfig.is_production():
            raise ValueError("Security configuration validation failed in production environment")
    
    print("Security configuration initialized successfully")
    print(f"Environment: {SecurityConfig.ENVIRONMENT}")
    print(f"Debug Mode: {SecurityConfig.DEBUG}")
    print(f"Session Timeout: {SecurityConfig.SESSION_TIMEOUT} seconds")
    print(f"Rate Limit: {SecurityConfig.RATE_LIMIT_MAX_ATTEMPTS} attempts per {SecurityConfig.RATE_LIMIT_WINDOW} seconds")


# Auto-initialize on import
if __name__ != "__main__":
    init_security_config()