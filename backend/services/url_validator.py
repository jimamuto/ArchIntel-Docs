"""
URL validation and sanitization service to prevent malicious repository URLs.
Provides comprehensive URL validation with allowlisting, sanitization, and security logging.
"""

import re
import logging
import urllib.parse
from typing import Optional, List, Dict, Union
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger("archintel.url_validation")
security_logger = logging.getLogger("archintel.security")

class URLValidationError(Exception):
    """Custom exception for URL validation failures."""
    pass

class URLSanitizationError(Exception):
    """Custom exception for URL sanitization failures."""
    pass

class URLValidationConfig:
    """Configuration for URL validation settings."""
    
    # Allowed URL schemes
    ALLOWED_SCHEMES = ['https', 'ssh', 'git']
    
    # Allowed domains for repository URLs
    ALLOWED_DOMAINS = {
        'github.com',
        'gitlab.com', 
        'bitbucket.org',
        'gitlab.internal.company.com',  # Example internal domain
        'github.company.com'           # Example internal GitHub Enterprise
    }
    
    # Maximum URL length
    MAX_URL_LENGTH = 2000
    
    # Maximum path depth
    MAX_PATH_DEPTH = 10
    
    # Allowed characters in URL components (basic whitelist)
    ALLOWED_HOST_PATTERN = r'^[a-zA-Z0-9.-]+$'
    ALLOWED_PATH_PATTERN = r'^[a-zA-Z0-9._/-]+$'
    ALLOWED_USERINFO_PATTERN = r'^[a-zA-Z0-9._-]+$'
    
    # Forbidden patterns
    FORBIDDEN_PATTERNS = [
        r'&', r'\|', r';', r'\$\(', r'`', r'>', r'<', r'&&', r'\|\|',  # Shell metacharacters
        r'\.\./', r'%2e%2e%2f', r'%2e%2e/', r'\.\.\\', r'%2e%2e%5c', r'%2e%2e\\',  # Path traversal
        r'javascript:', r'data:', r'file:', r'ftp:',  # Dangerous schemes
        r'@.*@',  # Multiple @ symbols (potential confusion)
        r'#.*#',  # Multiple # symbols
    ]


class URLValidator:
    """URL validation and sanitization service with comprehensive security measures."""
    
    def __init__(self, config: Optional[URLValidationConfig] = None):
        self.config = config or URLValidationConfig()
        
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format and security compliance.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
            
        Raises:
            URLValidationError: If URL fails validation
        """
        if not url:
            raise URLValidationError("Empty URL not allowed")
            
        # Check URL length
        if len(url) > self.config.MAX_URL_LENGTH:
            raise URLValidationError(f"URL too long: {len(url)} chars (max: {self.config.MAX_URL_LENGTH})")
            
        # Check forbidden patterns
        if self._contains_forbidden_patterns(url):
            raise URLValidationError("URL contains forbidden patterns")
            
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise URLValidationError(f"Invalid URL format: {str(e)}")
            
        # Validate scheme
        if parsed.scheme not in self.config.ALLOWED_SCHEMES:
            raise URLValidationError(f"Scheme '{parsed.scheme}' not allowed. Allowed: {self.config.ALLOWED_SCHEMES}")
            
        # Validate domain
        if not self._validate_domain(parsed.hostname):
            raise URLValidationError(f"Domain '{parsed.hostname}' not in allowed domains: {self.config.ALLOWED_DOMAINS}")
            
        # Validate path
        if not self._validate_path(parsed.path):
            raise URLValidationError(f"Path '{parsed.path}' contains invalid characters")
            
        # Validate user info (for SSH URLs)
        if parsed.username and not self._validate_userinfo(parsed.username):
            raise URLValidationError(f"Username '{parsed.username}' contains invalid characters")
            
        if parsed.password:
            raise URLValidationError("URLs with passwords are not allowed")
            
        # Validate path depth
        path_segments = [seg for seg in parsed.path.split('/') if seg]
        if len(path_segments) > self.config.MAX_PATH_DEPTH:
            raise URLValidationError(f"URL path too deep: {len(path_segments)} segments (max: {self.config.MAX_PATH_DEPTH})")
            
        # Log validation success
        security_logger.info(f"URL validated successfully: {self._sanitize_url_for_logging(url)}")
        
        return True
        
    def sanitize_url(self, url: str) -> str:
        """
        Sanitize URL by removing sensitive information while preserving functionality.
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL with sensitive information removed
            
        Raises:
            URLSanitizationError: If URL sanitization fails
        """
        try:
            self.validate_url(url)
            
            # Parse and sanitize URL
            parsed = urlparse(url)
            sanitized_components = []
            
            # Scheme
            sanitized_components.append(parsed.scheme)
            
            # Netloc (user:pass@host:port)
            netloc = ""
            if parsed.username:
                netloc += f"{parsed.username}"
            if parsed.password:
                netloc += ":***"
            if parsed.hostname:
                netloc += f"@{parsed.hostname}" if netloc else parsed.hostname
            if parsed.port:
                netloc += f":{parsed.port}"
            sanitized_components.append(netloc)
            
            # Path
            sanitized_components.append(parsed.path)
            
            # Params, Query, Fragment
            sanitized_components.extend([parsed.params, parsed.query, parsed.fragment])
            
            sanitized_url = urlunparse(sanitized_components)
            
            # Log sanitization
            logger.info(f"URL sanitized: {url} -> {sanitized_url}")
            
            return sanitized_url
            
        except Exception as e:
            raise URLSanitizationError(f"URL sanitization failed: {str(e)}")
            
    def _contains_forbidden_patterns(self, url: str) -> bool:
        """Check if URL contains forbidden patterns."""
        url_lower = url.lower()
        
        for pattern in self.config.FORBIDDEN_PATTERNS:
            if re.search(pattern, url_lower):
                security_logger.warning(f"Forbidden pattern detected in URL: {pattern} in {self._sanitize_url_for_logging(url)}")
                return True
                
        return False
        
    def _validate_domain(self, hostname: Optional[str]) -> bool:
        """Validate domain against allowed domains list."""
        if not hostname:
            return False
            
        # Normalize hostname
        hostname = hostname.lower().rstrip('.')
        
        # Check exact match
        if hostname in self.config.ALLOWED_DOMAINS:
            return True
            
        # Check subdomain matches (e.g., gitlab.company.com matches gitlab.company.com)
        for allowed_domain in self.config.ALLOWED_DOMAINS:
            if hostname.endswith('.' + allowed_domain) or hostname == allowed_domain:
                return True
                
        return False
        
    def _validate_path(self, path: str) -> bool:
        """Validate path components."""
        if not path:
            return True
            
        # Check allowed characters
        if not re.match(self.config.ALLOWED_PATH_PATTERN, path):
            return False
            
        # Check for path traversal attempts
        path_segments = path.split('/')
        for segment in path_segments:
            if segment == '..' or (segment.startswith('%2e%2e') and len(segment) >= 6):
                return False
                
        return True
        
    def _validate_userinfo(self, userinfo: str) -> bool:
        """Validate user info components."""
        if not userinfo:
            return True
            
        return bool(re.match(self.config.ALLOWED_USERINFO_PATTERN, userinfo))
        
    def _sanitize_url_for_logging(self, url: str) -> str:
        """Sanitize URL for logging purposes (remove sensitive info)."""
        try:
            parsed = urlparse(url)
            sanitized_components = []
            
            # Scheme
            sanitized_components.append(parsed.scheme)
            
            # Netloc (remove password, obscure username if needed)
            netloc = ""
            if parsed.hostname:
                netloc = parsed.hostname
            if parsed.port:
                netloc += f":{parsed.port}"
            sanitized_components.append(netloc)
            
            # Path, Params, Query, Fragment
            sanitized_components.extend([parsed.path, "****", "****", parsed.fragment])
            
            return urlunparse(sanitized_components)
            
        except:
            return "[SANITIZED_URL]"
            
    def validate_git_url(self, url: str) -> Dict[str, Union[str, bool]]:
        """
        Comprehensive Git URL validation with detailed results.
        
        Args:
            url: URL to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': False,
            'url': url,
            'sanitized_url': None,
            'scheme': None,
            'domain': None,
            'path': None,
            'error': None
        }
        
        try:
            parsed = urlparse(url)
            result['scheme'] = parsed.scheme
            result['domain'] = parsed.hostname
            result['path'] = parsed.path
            
            self.validate_url(url)
            result['valid'] = True
            result['sanitized_url'] = self.sanitize_url(url)
            
        except URLValidationError as e:
            result['error'] = str(e)
            security_logger.warning(f"Git URL validation failed: {str(e)} for URL: {self._sanitize_url_for_logging(url)}")
            
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected URL validation error: {str(e)}")
            
        return result


# Global URL validator instance
url_validator = URLValidator()


def is_valid_repository_url(url: str) -> bool:
    """
    Quick check if URL is a valid repository URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        return url_validator.validate_url(url)
    except URLValidationError:
        return False
    except Exception:
        return False


def sanitize_repository_url(url: str) -> str:
    """
    Sanitize repository URL for safe logging and display.
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL
        
    Raises:
        URLSanitizationError: If sanitization fails
    """
    return url_validator.sanitize_url(url)


def validate_and_sanitize_url(url: str) -> Dict[str, Union[str, bool]]:
    """
    Validate and sanitize URL in one operation.
    
    Args:
        url: URL to validate and sanitize
        
    Returns:
        Dictionary with validation and sanitization results
    """
    return url_validator.validate_git_url(url)