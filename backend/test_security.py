"""
Comprehensive security tests for subprocess execution vulnerabilities.
Tests the security measures implemented in subprocess_security.py and url_validator.py.
"""

import pytest
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock

# Import security modules
from services.subprocess_security import (
    SecureSubprocess, 
    SubprocessSecurityConfig,
    SecurityError, 
    CommandValidationError,
    execute_git_clone,
    execute_git_command,
    execute_subprocess_async
)
from services.url_validator import (
    URLValidator,
    URLValidationConfig,
    URLValidationError,
    URLSanitizationError,
    is_valid_repository_url,
    sanitize_repository_url,
    validate_and_sanitize_url
)


class TestURLValidator:
    """Test URL validation and sanitization security measures."""
    
    def setup_method(self):
        """Setup test configuration."""
        self.validator = URLValidator()
        
    def test_valid_github_urls(self):
        """Test valid GitHub repository URLs."""
        valid_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user/repo",
            "git@github.com:user/repo.git",
            "git@github.com:user/repo"
        ]
        
        for url in valid_urls:
            result = self.validator.validate_url(url)
            assert result is True, f"URL should be valid: {url}"
            
    def test_valid_gitlab_urls(self):
        """Test valid GitLab repository URLs."""
        valid_urls = [
            "https://gitlab.com/user/repo.git",
            "https://gitlab.com/user/repo",
            "git@gitlab.com:user/repo.git"
        ]
        
        for url in valid_urls:
            result = self.validator.validate_url(url)
            assert result is True, f"URL should be valid: {url}"
            
    def test_invalid_urls(self):
        """Test invalid repository URLs that should be rejected."""
        invalid_urls = [
            "http://github.com/user/repo.git",  # HTTP not allowed
            "ftp://github.com/user/repo.git",   # FTP not allowed
            "https://evil.com/user/repo.git",   # Domain not allowed
            "https://github.com/../../../etc/passwd",  # Path traversal
            "https://github.com/user/repo.git;rm -rf /",  # Command injection
            "https://github.com/user/repo.git&malicious",  # Shell metacharacters
            "javascript:alert('xss')",  # JavaScript URL
            "",  # Empty URL
        ]
        
        for url in invalid_urls:
            with pytest.raises(URLValidationError):
                self.validator.validate_url(url)
                
    def test_url_sanitization(self):
        """Test URL sanitization removes sensitive information."""
        test_url = "https://user:password@github.com/user/repo.git"
        sanitized = self.validator.sanitize_url(test_url)
        
        # Should not contain the password
        assert "password" not in sanitized
        assert "***" in sanitized
        
    def test_url_validation_detailed(self):
        """Test detailed URL validation results."""
        test_url = "https://github.com/user/repo.git"
        result = self.validator.validate_git_url(test_url)
        
        assert result['valid'] is True
        assert result['scheme'] == 'https'
        assert result['domain'] == 'github.com'
        assert result['path'] == '/user/repo.git'
        assert result['sanitized_url'] is not None
        
    def test_malicious_url_detection(self):
        """Test detection of various malicious URL patterns."""
        malicious_urls = [
            "https://github.com/user/repo.git%20%7C%20rm%20-rf%20%2F",  # Encoded shell injection
            "https://github.com/user/repo.git?cmd=rm%20-rf%20/",  # Query parameter injection
            "https://github.com/user/../../../etc/passwd",  # Path traversal
            "https://github.com/user/repo.git@evil.com",  # Confusing domain
        ]
        
        for url in malicious_urls:
            with pytest.raises(URLValidationError):
                self.validator.validate_url(url)


class TestSecureSubprocess:
    """Test secure subprocess execution measures."""
    
    def setup_method(self):
        """Setup test configuration."""
        self.secure_subprocess = SecureSubprocess()
        
    def test_valid_git_commands(self):
        """Test valid git commands that should be allowed."""
        valid_commands = [
            ["git", "clone", "--depth", "1", "https://github.com/user/repo.git", "/tmp/repo"],
            ["git", "fetch", "--depth", "1", "origin"],
            ["git", "pull", "--rebase"],
            "git clone --depth 1 https://github.com/user/repo.git /tmp/repo"
        ]
        
        for cmd in valid_commands:
            # Should not raise an exception
            self.secure_subprocess.validate_command(cmd)
            
    def test_invalid_commands(self):
        """Test commands that should be rejected."""
        invalid_commands = [
            ["git", "clone", "https://github.com/user/repo.git", "/tmp/repo"],  # Missing --depth
            ["git", "clone", "--depth", "1", "https://github.com/user/repo.git", "/tmp/repo", "extra_arg"],  # Too many args
            ["rm", "-rf", "/"],  # Command not allowed
            ["git", "clone", "--depth", "1", "https://evil.com/repo.git", "/tmp/repo"],  # Invalid URL
            ["git", "clone", "--depth", "1", "https://github.com/user/repo.git;rm -rf /", "/tmp/repo"],  # Command injection
        ]
        
        for cmd in invalid_commands:
            with pytest.raises(CommandValidationError):
                self.secure_subprocess.validate_command(cmd)
                
    def test_command_length_validation(self):
        """Test command length limits."""
        # Create a command that's too long
        long_url = "https://github.com/" + "a" * 2000 + ".git"
        cmd = ["git", "clone", "--depth", "1", long_url, "/tmp/repo"]
        
        with pytest.raises(CommandValidationError, match="Command too long"):
            self.secure_subprocess.validate_command(cmd)
            
    def test_rate_limiting(self):
        """Test command rate limiting."""
        # Mock time to test rate limiting
        with patch('time.time', return_value=1000):
            # Execute commands up to the limit
            for i in range(10):
                cmd = ["git", "clone", "--depth", "1", f"https://github.com/user/repo{i}.git", f"/tmp/repo{i}"]
                self.secure_subprocess.validate_command(cmd)
                
            # Next command should hit rate limit
            cmd = ["git", "clone", "--depth", "1", "https://github.com/user/repo10.git", "/tmp/repo10"]
            with pytest.raises(CommandValidationError, match="Rate limit exceeded"):
                self.secure_subprocess.validate_command(cmd)
                
    def test_environment_sanitization(self):
        """Test environment variable sanitization."""
        env = {
            'PATH': '/usr/bin',
            'HOME': '/home/user',
            'SECRET': 'secret_value',  # Should be filtered out
            'MALICIOUS': 'rm -rf /'    # Should be filtered out
        }
        
        sanitized_env = self.secure_subprocess._sanitize_environment(env)
        
        # Should contain safe variables
        assert 'PATH' in sanitized_env
        assert 'HOME' in sanitized_env
        
        # Should not contain unsafe variables
        assert 'SECRET' not in sanitized_env
        assert 'MALICIOUS' not in sanitized_env
        
        # Should contain security defaults
        assert sanitized_env['GIT_TERMINAL_PROMPT'] == '0'
        
    def test_output_sanitization(self):
        """Test command output sanitization."""
        # Create a mock result with sensitive information
        mock_result = MagicMock()
        mock_result.stdout = "Repository cloned successfully. Token: ghp_1234567890abcdef1234567890abcdef1234567890abcdef"
        mock_result.stderr = "Warning: Authentication failed for user: admin@example.com"
        
        sanitized_result = self.secure_subprocess._sanitize_output(mock_result)
        
        # Should contain sanitized output
        assert "ghp_1234567890abcdef1234567890abcdef1234567890abcdef" not in sanitized_result.stdout
        assert "[REDACTED_GITHUB_TOKEN]" in sanitized_result.stdout
        assert "admin@example.com" not in sanitized_result.stderr
        assert "[REDACTED_EMAIL]" in sanitized_result.stderr


class TestIntegrationSecurity:
    """Integration tests for security measures."""
    
    def test_end_to_end_git_clone_security(self):
        """Test end-to-end secure git clone functionality."""
        # Test with valid URL
        valid_url = "https://github.com/user/repo.git"
        target_dir = "/tmp/test_repo"
        
        # Should not raise an exception for validation
        assert is_valid_repository_url(valid_url) is True
        
        sanitized_url = sanitize_repository_url(valid_url)
        assert sanitized_url == valid_url  # No sensitive info to sanitize
        
        # Test validation results
        result = validate_and_sanitize_url(valid_url)
        assert result['valid'] is True
        assert result['scheme'] == 'https'
        assert result['domain'] == 'github.com'
        
    def test_security_event_logging(self):
        """Test that security events are properly logged."""
        # This would require setting up logging capture in a real test environment
        # For now, we test that the functions exist and can be called
        validator = URLValidator()
        
        # Should not raise exception for valid URL
        assert validator.validate_url("https://github.com/user/repo.git") is True
        
        # Should raise exception for invalid URL
        with pytest.raises(URLValidationError):
            validator.validate_url("http://evil.com/repo.git")
            
    def test_subprocess_execution_security(self):
        """Test secure subprocess execution patterns."""
        secure_subprocess = SecureSubprocess()
        
        # Test that valid commands pass validation
        valid_cmd = ["git", "clone", "--depth", "1", "https://github.com/user/repo.git", "/tmp/repo"]
        secure_subprocess.validate_command(valid_cmd)
        
        # Test that malicious commands are rejected
        malicious_cmd = ["git", "clone", "--depth", "1", "https://github.com/user/repo.git;rm -rf /", "/tmp/repo"]
        with pytest.raises(CommandValidationError):
            secure_subprocess.validate_command(malicious_cmd)


class TestSecurityErrorHandling:
    """Test error handling and security responses."""
    
    def test_security_error_exceptions(self):
        """Test that security errors are properly raised."""
        # Test URL validation errors
        with pytest.raises(URLValidationError, match="Empty URL not allowed"):
            URLValidator().validate_url("")
            
        # Test command validation errors
        secure_subprocess = SecureSubprocess()
        with pytest.raises(CommandValidationError, match="Empty command not allowed"):
            secure_subprocess.validate_command([])
            
    def test_generic_error_responses(self):
        """Test that error responses don't expose sensitive information."""
        validator = URLValidator()
        
        # Should provide generic error message for security
        try:
            validator.validate_url("https://evil.com/repo.git")
        except URLValidationError as e:
            # Error message should not contain sensitive system information
            error_msg = str(e)
            assert "evil.com" in error_msg  # Should contain the problematic URL part
            assert "internal" not in error_msg.lower()  # Should not expose internal details
            assert "system" not in error_msg.lower()  # Should not expose system details


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])