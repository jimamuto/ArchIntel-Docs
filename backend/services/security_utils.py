"""
Secure Path Validation Utility Module

This module provides comprehensive path validation and security functions
to prevent path traversal attacks and ensure secure file access.

Author: ArchIntel Security Team
Requirements: Defense-in-depth approach for path traversal protection
"""

import logging
import os
import pathlib
import re
import sys
from pathlib import Path
from typing import Optional, Union
from urllib.parse import unquote

# Configure logging for security events
security_logger = logging.getLogger("archintel.security")
security_logger.setLevel(logging.INFO)

# Create handler for security logs
if not security_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)


class PathTraversalError(Exception):
    """Custom exception for path traversal security violations"""
    pass


class PathValidator:
    """Comprehensive path validation and security utility class"""
    
    # Common malicious patterns that should be blocked
    MALICIOUS_PATTERNS = [
        r'\.\./',           # Directory traversal
        r'\.\.\\',          # Windows directory traversal
        r'%2e%2e/',         # URL encoded traversal
        r'%2e%2e\\',        # URL encoded Windows traversal
        r'%252e%252e/',     # Double URL encoded traversal
        r'%252e%252e\\',    # Double URL encoded Windows traversal
        r'\.\.%2f',         # Mixed encoding traversal
        r'\.\.%5c',         # Mixed encoding Windows traversal
        r'~/',               # Home directory access
        r'/root/',           # Root directory access
        r'/etc/',            # System directory access
        r'/proc/',           # System process access
        r'/sys/',            # System information access
    ]
    
    # Valid path characters (whitelist approach)
    VALID_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9._/-\\]+$', re.IGNORECASE)
    
    def __init__(self, allowed_paths: Optional[list] = None):
        """
        Initialize path validator with allowed base paths
        
        Args:
            allowed_paths: List of allowed base directory paths
        """
        self.allowed_paths = allowed_paths or []
        
    def sanitize_input(self, path_input: str) -> str:
        """
        Sanitize and normalize path input to prevent injection attacks
        
        Args:
            path_input: Raw path input from user
            
        Returns:
            Sanitized path string
            
        Raises:
            PathTraversalError: If input contains malicious patterns
        """
        if not isinstance(path_input, str):
            raise PathTraversalError("Path input must be a string")
            
        # URL decode the input
        decoded_path = unquote(path_input)
        
        # Remove null bytes and control characters
        cleaned_path = ''.join(char for char in decoded_path if ord(char) >= 32)
        
        # Check for malicious patterns
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, cleaned_path, re.IGNORECASE):
                security_logger.warning(
                    f"Blocked malicious path pattern: {pattern} in input: {path_input}"
                )
                raise PathTraversalError(
                    f"Invalid path contains malicious pattern: {pattern}"
                )
                
        # Validate character set
        if not self.VALID_PATH_PATTERN.match(cleaned_path):
            security_logger.warning(f"Blocked invalid characters in path: {cleaned_path}")
            raise PathTraversalError("Path contains invalid characters")
            
        return cleaned_path.strip()
    
    def validate_path(self, base_path: Union[str, Path], relative_path: str) -> Path:
        """
        Validate that a relative path is within the allowed base path
        
        Args:
            base_path: Base directory path (absolute)
            relative_path: Relative path to validate
            
        Returns:
            Resolved absolute Path object
            
        Raises:
            PathTraversalError: If path traversal is detected
        """
        try:
            # Convert to Path objects for secure handling
            base_path = Path(base_path).resolve()
            relative_path = self.sanitize_input(relative_path)
            
            # Handle empty relative path
            if not relative_path or relative_path == '.':
                return base_path
                
            # Create the target path
            target_path = base_path / relative_path
            
            # Resolve the target path to handle any internal .. or . components
            resolved_target = target_path.resolve()
            
            # Security check: Ensure the resolved path is still within the base path
            try:
                resolved_target.relative_to(base_path)
            except ValueError:
                security_logger.warning(
                    f"Path traversal attempt blocked: {relative_path} resolves to {resolved_target} "
                    f"which is outside base path {base_path}"
                )
                raise PathTraversalError(
                    f"Path traversal detected: {relative_path} attempts to access paths outside {base_path}"
                )
                
            # Additional check: Verify no symlinks point outside base path
            if self._check_symlink_security(base_path, resolved_target):
                security_logger.warning(
                    f"Symlink security violation: {resolved_target} points outside base path {base_path}"
                )
                raise PathTraversalError("Symlink attempts to access paths outside allowed directory")
                
            return resolved_target
            
        except (OSError, IOError) as e:
            security_logger.error(f"Path validation failed due to system error: {e}")
            raise PathTraversalError(f"Path validation failed: {str(e)}")
        except Exception as e:
            security_logger.error(f"Unexpected error during path validation: {e}")
            raise PathTraversalError(f"Path validation failed: {str(e)}")
    
    def _check_symlink_security(self, base_path: Path, target_path: Path) -> bool:
        """
        Check if symlinks in the path chain point outside the base path
        
        Args:
            base_path: Allowed base directory
            target_path: Path to check for symlink violations
            
        Returns:
            True if security violation detected, False otherwise
        """
        try:
            # Walk up the path chain checking each component
            current_path = target_path
            while current_path != current_path.parent:
                if current_path.is_symlink():
                    try:
                        link_target = current_path.resolve()
                        # Check if symlink target is outside base path
                        link_target.relative_to(base_path)
                    except ValueError:
                        return True  # Symlink points outside base path
                current_path = current_path.parent
            return False
        except Exception as e:
            # If we can't check symlinks, be conservative and allow
            security_logger.warning(f"Could not verify symlink security: {e}")
            return False
    
    def validate_file_access(self, file_path: Union[str, Path], allowed_extensions: Optional[list] = None) -> Path:
        """
        Validate file access with additional security checks
        
        Args:
            file_path: Path to the file to validate
            allowed_extensions: List of allowed file extensions (optional)
            
        Returns:
            Validated Path object
            
        Raises:
            PathTraversalError: If file access is not allowed
        """
        file_path = Path(file_path)
        
        # Check if file exists and is a file (not directory)
        if not file_path.exists():
            raise PathTraversalError(f"File does not exist: {file_path}")
            
        if not file_path.is_file():
            raise PathTraversalError(f"Path is not a file: {file_path}")
            
        # Check file extension if specified
        if allowed_extensions:
            file_ext = file_path.suffix.lower()
            if file_ext not in [ext.lower() for ext in allowed_extensions]:
                security_logger.warning(f"Blocked access to file with disallowed extension: {file_path}")
                raise PathTraversalError(f"File extension not allowed: {file_ext}")
                
        # Additional security: Check file size limit (prevent DoS)
        try:
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                raise PathTraversalError("File too large to read")
        except OSError:
            pass  # If we can't get file stats, proceed with other checks
            
        return file_path
    
    def is_safe_path(self, base_path: Union[str, Path], test_path: str) -> bool:
        """
        Quick check if a path is safe (returns boolean instead of raising exceptions)
        
        Args:
            base_path: Base directory path
            test_path: Path to test
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            self.validate_path(base_path, test_path)
            return True
        except PathTraversalError:
            return False
    
    def add_allowed_path(self, path: Union[str, Path]):
        """Add a path to the allowed paths list"""
        self.allowed_paths.append(str(Path(path).resolve()))
    
    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """Check if a path is in the allowed paths list"""
        path = str(Path(path).resolve())
        return any(path.startswith(allowed) for allowed in self.allowed_paths)


def resolve_repo_path_safe(repo_path: str, validator: Optional[PathValidator] = None) -> Path:
    """
    Secure repository path resolution with comprehensive validation
    
    Args:
        repo_path: Repository path to resolve
        validator: Optional PathValidator instance
        
    Returns:
        Resolved Path object
        
    Raises:
        PathTraversalError: If path resolution fails security checks
    """
    if validator is None:
        validator = PathValidator()
    
    # Handle special path formats
    if repo_path == ".":
        # Current directory (project root)
        current_dir = Path(__file__).parent  # backend/routers/
        backend_dir = current_dir.parent      # backend/
        project_root = backend_dir.parent     # project root
        return validator.validate_path(project_root, ".")
    
    elif repo_path.startswith("repos/"):
        # Repository in repos/ directory
        current_dir = Path(__file__).parent  # backend/routers/
        backend_dir = current_dir.parent      # backend/
        project_root = backend_dir.parent     # project root
        repo_path_full = project_root / repo_path
        return validator.validate_path(project_root, repo_path)
    
    else:
        # Direct path - validate it's absolute and safe
        path_obj = Path(repo_path).resolve()
        validator.add_allowed_path(path_obj.parent)
        if not validator.is_path_allowed(path_obj):
            raise PathTraversalError(f"Repository path not allowed: {repo_path}")
        return path_obj


def read_file_secure(
    repo_path: Union[str, Path], 
    file_path: str, 
    validator: Optional[PathValidator] = None,
    allowed_extensions: Optional[list] = None
) -> str:
    """
    Secure file reading with comprehensive validation
    
    Args:
        repo_path: Repository base path
        file_path: Relative file path within repository
        validator: Optional PathValidator instance
        allowed_extensions: List of allowed file extensions
        
    Returns:
        File content as string
        
    Raises:
        PathTraversalError: If file access is not secure
    """
    if validator is None:
        validator = PathValidator()
    
    try:
        # Resolve repository path securely
        base_path = resolve_repo_path_safe(str(repo_path), validator)
        
        # Validate the file path
        full_path = validator.validate_path(base_path, file_path)
        
        # Additional file access validation
        validator.validate_file_access(full_path, allowed_extensions)
        
        # Read the file
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        security_logger.info(f"Successfully read file: {file_path} from {repo_path}")
        return content
        
    except PathTraversalError:
        security_logger.warning(f"Blocked insecure file access attempt: {file_path} in {repo_path}")
        raise
    except Exception as e:
        security_logger.error(f"File read failed for {file_path}: {e}")
        raise PathTraversalError(f"Failed to read file: {str(e)}")


# Convenience function for backward compatibility
def validate_and_read_file(repo_path: str, file_path: str) -> str:
    """
    Backward compatible function for secure file reading
    
    Args:
        repo_path: Repository path
        file_path: File path relative to repository
        
    Returns:
        File content or error message
    """
    try:
        return read_file_secure(repo_path, file_path)
    except PathTraversalError as e:
        return f"// Security violation: {str(e)}"
    except Exception as e:
        return f"// Error reading file: {str(e)}"


# Default validator instance for common use
default_validator = PathValidator()

# Common allowed file extensions for code analysis
CODE_EXTENSIONS = [
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
    '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.cs', '.vb',
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.json', '.xml',
    '.yml', '.yaml', '.md', '.txt', '.sql', '.sh', '.bash', '.zsh'
]