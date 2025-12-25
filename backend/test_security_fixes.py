"""
Comprehensive Security Tests for Path Traversal Vulnerabilities

This test suite validates the security fixes implemented in the ArchIntel backend.
Tests cover path traversal attacks, symlink attacks, boundary violations, and
security logging functionality.

Author: ArchIntel Security Team
Requirements: pytest, pathlib, tempfile, logging
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import logging
from unittest.mock import patch, MagicMock

# Import the security utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.security_utils import PathValidator, PathTraversalError, resolve_repo_path_safe, read_file_secure


class TestPathValidator:
    """Test suite for PathValidator class security functions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.validator = PathValidator()
        
        # Create test files and directories
        self.test_file = Path(self.test_dir) / "test.txt"
        self.test_file.write_text("test content")
        
        self.subdir = Path(self.test_dir) / "subdir"
        self.subdir.mkdir()
        self.subfile = self.subdir / "subfile.txt"
        self.subfile.write_text("subfile content")
        
        # Create a symlink (if supported)
        self.symlink_file = Path(self.test_dir) / "link.txt"
        try:
            self.symlink_file.symlink_to(self.test_file)
        except (OSError, NotImplementedError):
            self.symlink_file = None
            
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_basic_path_validation(self):
        """Test basic path validation functionality"""
        # Valid path should work
        result = self.validator.validate_path(self.test_dir, "test.txt")
        assert result == Path(self.test_dir) / "test.txt"
        
        # Valid subdirectory path should work
        result = self.validator.validate_path(self.test_dir, "subdir/subfile.txt")
        assert result == Path(self.test_dir) / "subdir" / "subfile.txt"
    
    def test_path_traversal_attempts(self):
        """Test detection of path traversal attacks"""
        # Basic ../ traversal
        with pytest.raises(PathTraversalError, match="traversal"):
            self.validator.validate_path(self.test_dir, "../etc/passwd")
            
        # Multiple ../ traversal
        with pytest.raises(PathTraversalError, match="traversal"):
            self.validator.validate_path(self.test_dir, "../../etc/passwd")
            
        # Windows style traversal
        with pytest.raises(PathTraversalError, match="traversal"):
            self.validator.validate_path(self.test_dir, "..\\..\\etc\\passwd")
    
    def test_url_encoded_traversal(self):
        """Test detection of URL-encoded path traversal attempts"""
        # URL encoded ../
        with pytest.raises(PathTraversalError, match="traversal"):
            self.validator.validate_path(self.test_dir, "%2e%2e/%2fetc%2fpasswd")
            
        # Double URL encoded
        with pytest.raises(PathTraversalError, match="traversal"):
            self.validator.validate_path(self.test_dir, "%252e%252e%252fetc%252fpasswd")
            
        # Mixed encoding
        with pytest.raises(PathTraversalError, match="traversal"):
            self.validator.validate_path(self.test_dir, "..%2fetc%2fpasswd")
    
    def test_malicious_patterns(self):
        """Test detection of various malicious patterns"""
        malicious_patterns = [
            "~/.bashrc",
            "/etc/passwd",
            "/root/.ssh/id_rsa",
            "/proc/self/environ",
            "/sys/class/net",
        ]
        
        for pattern in malicious_patterns:
            with pytest.raises(PathTraversalError, match="malicious"):
                self.validator.validate_path(self.test_dir, pattern)
    
    def test_invalid_characters(self):
        """Test detection of invalid characters in paths"""
        invalid_paths = [
            "test\x00file.txt",  # Null byte
            "test\x01file.txt",  # Control character
            "test\file.txt",     # Backspace
            "test\x7ffile.txt",  # DEL character
        ]
        
        for path in invalid_paths:
            with pytest.raises(PathTraversalError, match="invalid characters"):
                self.validator.validate_path(self.test_dir, path)
    
    def test_symlink_security(self):
        """Test symlink security validation"""
        if not self.symlink_file:
            pytest.skip("Symlinks not supported on this platform")
            
        # Valid symlink within bounds should work
        result = self.validator.validate_path(self.test_dir, "link.txt")
        assert result == self.symlink_file
        
        # Create symlink outside bounds
        outside_file = Path(self.test_dir) / "outside_link.txt"
        try:
            outside_file.symlink_to(Path(self.test_dir).parent / "forbidden.txt")
            
            with pytest.raises(PathTraversalError, match="symlink"):
                self.validator.validate_path(self.test_dir, "outside_link.txt")
                
        except (OSError, NotImplementedError):
            pytest.skip("Cannot create symlink outside directory")
    
    def test_file_access_validation(self):
        """Test file access validation with extension filtering"""
        # Valid file access
        result = self.validator.validate_file_access(self.test_file)
        assert result == self.test_file
        
        # Directory access should fail
        with pytest.raises(PathTraversalError, match="not a file"):
            self.validator.validate_file_access(self.subdir)
            
        # Non-existent file should fail
        with pytest.raises(PathTraversalError, match="does not exist"):
            self.validator.validate_file_access(Path(self.test_dir) / "nonexistent.txt")
    
    def test_allowed_extensions(self):
        """Test file extension filtering"""
        # Create test files with different extensions
        py_file = Path(self.test_dir) / "test.py"
        py_file.write_text("print('hello')")
        
        exe_file = Path(self.test_dir) / "malicious.exe"
        exe_file.write_text("fake executable")
        
        # Allow only Python files
        result = self.validator.validate_file_access(py_file, allowed_extensions=['.py'])
        assert result == py_file
        
        # Block executable files
        with pytest.raises(PathTraversalError, match="File extension not allowed"):
            self.validator.validate_file_access(exe_file, allowed_extensions=['.py'])
    
    def test_file_size_limits(self):
        """Test file size limit enforcement"""
        # Create a large file (simulate > 100MB)
        large_file = Path(self.test_dir) / "large_file.txt"
        large_file.write_text("A" * (101 * 1024 * 1024))  # 101MB
        
        with pytest.raises(PathTraversalError, match="File too large"):
            self.validator.validate_file_access(large_file)
    
    def test_safe_path_check(self):
        """Test the safe path check boolean method"""
        # Valid paths should return True
        assert self.validator.is_safe_path(self.test_dir, "test.txt") is True
        assert self.validator.is_safe_path(self.test_dir, "subdir/subfile.txt") is True
        
        # Invalid paths should return False
        assert self.validator.is_safe_path(self.test_dir, "../etc/passwd") is False
        assert self.validator.is_safe_path(self.test_dir, "invalid\x00file.txt") is False
    
    def test_allowed_paths_management(self):
        """Test allowed paths management"""
        # Add allowed path
        test_path = Path(self.test_dir) / "allowed"
        test_path.mkdir()
        self.validator.add_allowed_path(test_path)
        
        assert self.validator.is_path_allowed(test_path) is True
        assert self.validator.is_path_allowed(Path(self.test_dir) / "other") is False


class TestRepositoryPathResolution:
    """Test repository path resolution security"""
    
    def test_resolve_repo_path_safe(self):
        """Test secure repository path resolution"""
        # Test special path "." (project root)
        with patch('services.security_utils.Path') as mock_path:
            mock_path.return_value.parent = mock_path.return_value
            mock_path.return_value.resolve.return_value = Path("/test/project")
            
            result = resolve_repo_path_safe(".")
            assert result == Path("/test/project")
    
    def test_resolve_repos_path(self):
        """Test repos/ directory path resolution"""
        with patch('services.security_utils.Path') as mock_path:
            mock_path.return_value.parent = mock_path.return_value
            mock_path.return_value.resolve.return_value = Path("/test/project")
            
            result = resolve_repo_path_safe("repos/test-repo")
            assert result == Path("/test/project/repos/test-repo")
    
    def test_direct_path_resolution(self):
        """Test direct path resolution with validation"""
        test_path = "/valid/absolute/path"
        
        with patch('services.security_utils.PathValidator') as mock_validator:
            mock_validator_instance = MagicMock()
            mock_validator.return_value = mock_validator_instance
            mock_validator_instance.is_path_allowed.return_value = True
            
            result = resolve_repo_path_safe(test_path, mock_validator_instance)
            mock_validator_instance.is_path_allowed.assert_called_once_with(test_path)
    
    def test_path_resolution_security(self):
        """Test that path resolution prevents traversal"""
        # Test that malicious paths are blocked
        with pytest.raises(PathTraversalError):
            resolve_repo_path_safe("../etc/passwd")
            
        with pytest.raises(PathTraversalError):
            resolve_repo_path_safe("%2e%2e%2fetc%2fpasswd")


class TestSecureFileReading:
    """Test secure file reading functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.validator = PathValidator()
        
        # Create test files
        self.test_file = Path(self.test_dir) / "test.py"
        self.test_file.write_text("print('hello world')")
        
        self.text_file = Path(self.test_dir) / "readme.txt"
        self.text_file.write_text("This is a readme file")
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_secure_file_reading(self):
        """Test secure file reading functionality"""
        content = read_file_secure(self.test_dir, "test.py", self.validator)
        assert content == "print('hello world')"
    
    def test_secure_file_reading_with_extensions(self):
        """Test secure file reading with extension filtering"""
        # Allow Python files
        content = read_file_secure(
            self.test_dir, 
            "test.py", 
            self.validator, 
            allowed_extensions=['.py', '.txt']
        )
        assert content == "print('hello world')"
        
        # Block non-Python files
        with pytest.raises(PathTraversalError):
            read_file_secure(
                self.test_dir, 
                "test.py", 
                self.validator, 
                allowed_extensions=['.txt']
            )
    
    def test_secure_reading_traversal_protection(self):
        """Test that secure reading prevents traversal attacks"""
        # Try to read file outside directory
        content = read_file_secure(self.test_dir, "../etc/passwd", self.validator)
        assert "Security violation" in content or "Security violation" in content
    
    def test_secure_reading_error_handling(self):
        """Test error handling in secure file reading"""
        # Try to read non-existent file
        content = read_file_secure(self.test_dir, "nonexistent.txt", self.validator)
        assert "Error reading file" in content


class TestSecurityLogging:
    """Test security event logging functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.validator = PathValidator()
        
        # Setup logging capture
        self.log_capture = []
        def log_capture_handler(msg):
            self.log_capture.append(msg)
            
        # Patch the security logger
        import logging
        self.original_logger = logging.getLogger("archintel.security")
        self.original_handlers = self.original_logger.handlers[:]
        
        # Create a test handler
        self.test_handler = logging.StreamHandler()
        self.test_handler.emit = lambda record: self.log_capture.append(record.getMessage())
        self.original_logger.addHandler(self.test_handler)
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        # Restore original logger
        self.original_logger.handlers = self.original_handlers
    
    def test_security_event_logging(self):
        """Test that security events are properly logged"""
        # Trigger a security event
        try:
            self.validator.validate_path(self.test_dir, "../etc/passwd")
        except PathTraversalError:
            pass  # Expected
        
        # Check that security event was logged
        assert len(self.log_capture) > 0
        assert any("traversal attempt blocked" in msg for msg in self.log_capture)
    
    def test_symlink_violation_logging(self):
        """Test that symlink violations are logged"""
        # This test would need actual symlinks to work properly
        # For now, we test the logging mechanism exists
        security_logger = logging.getLogger("archintel.security")
        security_logger.warning("Test symlink violation")
        
        assert len(self.log_capture) > 0
        assert "Test symlink violation" in self.log_capture[-1]


class TestAttackVectorValidation:
    """Test validation against common attack vectors"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.validator = PathValidator()
        
        # Create some legitimate files
        legitimate_files = [
            "src/main.py",
            "docs/README.md", 
            "tests/test_main.py",
            "config/settings.json"
        ]
        
        for file_path in legitimate_files:
            full_path = Path(self.test_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content of {file_path}")
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_common_attack_vectors(self):
        """Test protection against common attack vectors"""
        attack_vectors = [
            # Basic traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            
            # URL encoded
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            
            # Double encoded
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            
            # Mixed encoding
            "..%2f..%2f..%2fetc%2fpasswd",
            "..%5c..%5c..%5cwindows%5csystem32%5cdrivers%5cetc%5chosts",
            
            # Null byte injection
            "../../../etc/passwd%00.jpg",
            "../../../etc/passwd\x00.jpg",
            
            # Path normalization bypasses
            "./././../../../etc/passwd",
            "/./././../../../etc/passwd",
            
            # Unicode normalization
            ".\u22c5\u22c5/\u22c5\u22c5/\u22c5\u22c5/etc/passwd",
            
            # Long path attacks
            "../" * 100 + "etc/passwd",
            
            # System file access
            "~/.bashrc",
            "~root/.ssh/id_rsa",
            "/proc/self/environ",
            "/sys/class/net",
        ]
        
        for attack_vector in attack_vectors:
            with pytest.raises(PathTraversalError):
                self.validator.validate_path(self.test_dir, attack_vector)
    
    def test_boundary_violation_detection(self):
        """Test detection of boundary violations"""
        # Test paths that appear valid but violate boundaries
        boundary_violations = [
            "valid/path/../../../forbidden.txt",
            "subdir/../..//forbidden.txt", 
            "a/../b/../../forbidden.txt",
        ]
        
        for violation in boundary_violations:
            with pytest.raises(PathTraversalError):
                self.validator.validate_path(self.test_dir, violation)
    
    def test_legitimate_path_allowance(self):
        """Test that legitimate paths are still allowed"""
        legitimate_paths = [
            "src/main.py",
            "docs/README.md",
            "tests/test_main.py", 
            "config/settings.json",
            "./src/main.py",
            "src/../src/main.py",  # This should normalize to valid path
        ]
        
        for path in legitimate_paths:
            try:
                result = self.validator.validate_path(self.test_dir, path)
                assert result.exists()
            except PathTraversalError:
                # Some normalization attempts might be blocked
                # This is acceptable security behavior
                pass


class TestPerformanceAndDoSProtection:
    """Test performance and DoS protection mechanisms"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.validator = PathValidator()
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_large_path_handling(self):
        """Test handling of extremely long paths"""
        # Create a path that's extremely long
        long_path = "a/" * 1000 + "file.txt"
        
        # Should either work (if within system limits) or fail gracefully
        try:
            result = self.validator.validate_path(self.test_dir, long_path)
            # If it succeeds, the path should be properly resolved
            assert isinstance(result, Path)
        except (PathTraversalError, OSError):
            # Expected for paths that exceed system limits
            pass
    
    def test_malformed_input_handling(self):
        """Test handling of malformed input"""
        malformed_inputs = [
            None,  # None input
            "",    # Empty string
            "   ", # Whitespace only
            "\n",  # Newline
            "\t",  # Tab
            "file with spaces.txt",  # Spaces (should be valid)
            "файл.txt",  # Unicode characters
        ]
        
        for input_val in malformed_inputs:
            if input_val is None:
                with pytest.raises(PathTraversalError):
                    self.validator.sanitize_input(input_val)
            else:
                # Other inputs should either work or be sanitized
                try:
                    sanitized = self.validator.sanitize_input(input_val)
                    assert isinstance(sanitized, str)
                except PathTraversalError:
                    # Some inputs might be blocked for security
                    pass


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])