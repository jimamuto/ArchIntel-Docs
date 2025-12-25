"""
Integration Test for Path Traversal Security Fixes

This test verifies that the security fixes in the ArchIntel backend
properly prevent path traversal attacks while maintaining functionality.

Author: ArchIntel Security Team
Requirements: Tests the actual router endpoints with security protections
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestSecurityIntegration:
    """Integration tests for the security fixes in routers"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test repository structure
        self.repo_dir = Path(self.test_dir) / "test-repo"
        self.repo_dir.mkdir()
        
        # Create legitimate files
        self.legitimate_files = {
            "src/main.py": "print('hello world')",
            "docs/README.md": "# Test Documentation",
            "config/settings.json": '{"debug": true}',
            "tests/test_main.py": "def test_main(): pass"
        }
        
        for file_path, content in self.legitimate_files.items():
            full_path = self.repo_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_projects_router_security(self):
        """Test that projects router prevents path traversal"""
        # Import the router function
        from routers.projects import get_file_code
        from supabase import Client
        
        # Create mock supabase client
        mock_supabase = MagicMock()
        mock_project = {"id": "test-project", "repo_url": "https://github.com/test/repo.git"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[mock_project]
        )
        
        # Test legitimate file access
        result = get_file_code(
            project_id="test-project",
            path="src/main.py", 
            repo_path=str(self.repo_dir),
            supabase=mock_supabase
        )
        
        # Should return the file content
        assert "print('hello world')" in result
        
        # Test path traversal attempt
        result = get_file_code(
            project_id="test-project",
            path="../../../etc/passwd",
            repo_path=str(self.repo_dir),
            supabase=mock_supabase
        )
        
        # Should block the traversal attempt
        assert "access denied" in result or "Security violation" in result
    
    def test_docs_router_security(self):
        """Test that docs router prevents path traversal"""
        # Import the router function
        from routers.docs import get_file_llm_documentation
        from supabase import Client
        
        # Create mock supabase client
        mock_supabase = MagicMock()
        mock_project = {"id": "test-project", "repo_url": "https://github.com/test/repo.git"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[mock_project]
        )
        
        # Test legitimate file access
        result = get_file_llm_documentation(
            project_id="test-project",
            path="src/main.py",
            repo_path=str(self.repo_dir),
            supabase=mock_supabase
        )
        
        # Should not immediately fail (might return error due to missing LLM setup)
        # But should not crash or expose files outside the repository
        
        # Test path traversal attempt
        result = get_file_llm_documentation(
            project_id="test-project",
            path="../../../etc/passwd",
            repo_path=str(self.repo_dir),
            supabase=mock_supabase
        )
        
        # Should block the traversal attempt
        assert "access denied" in result or "Security violation" in result
    
    def test_malicious_input_variations(self):
        """Test various malicious input patterns"""
        from routers.projects import get_file_code
        from supabase import Client
        
        mock_supabase = MagicMock()
        mock_project = {"id": "test-project", "repo_url": "https://github.com/test/repo.git"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[mock_project]
        )
        
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e/%2e%2e/%2e%2e/etc/passwd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "~/.bashrc",
            "/etc/passwd",
            "/root/.ssh/id_rsa",
            "../" * 100 + "etc/passwd",
        ]
        
        for malicious_input in malicious_inputs:
            result = get_file_code(
                project_id="test-project",
                path=malicious_input,
                repo_path=str(self.repo_dir),
                supabase=mock_supabase
            )
            
            # Should block all traversal attempts
            assert (
                "access denied" in result.lower() or 
                "security violation" in result.lower() or
                "invalid file path" in result.lower()
            ), f"Failed to block malicious input: {malicious_input}"
    
    def test_boundary_testing(self):
        """Test boundary conditions and edge cases"""
        from routers.projects import get_file_code
        from supabase import Client
        
        mock_supabase = MagicMock()
        mock_project = {"id": "test-project", "repo_url": "https://github.com/test/repo.git"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[mock_project]
        )
        
        # Test legitimate boundary cases
        boundary_cases = [
            "src/main.py",           # Normal path
            "./src/main.py",         # Current directory prefix
            "src/../src/main.py",    # Self-referential (should normalize)
            "src/./main.py",         # Current directory in middle
        ]
        
        for case in boundary_cases:
            result = get_file_code(
                project_id="test-project",
                path=case,
                repo_path=str(self.repo_dir),
                supabase=mock_supabase
            )
            
            # These should either work or fail gracefully (not expose files outside repo)
            if "access denied" not in result and "Security violation" not in result:
                # If it doesn't block, it should return valid content or an error
                assert isinstance(result, str)
        
        # Test actual boundary violations
        violation_cases = [
            "src/../../../forbidden.txt",
            "docs/../..//forbidden.txt",
            "a/../b/../../forbidden.txt",
        ]
        
        for violation in violation_cases:
            result = get_file_code(
                project_id="test-project",
                path=violation,
                repo_path=str(self.repo_dir),
                supabase=mock_supabase
            )
            
            # Should block boundary violations
            assert (
                "access denied" in result.lower() or 
                "security violation" in result.lower() or
                "invalid file path" in result.lower()
            ), f"Failed to block boundary violation: {violation}"
    
    def test_symlink_security(self):
        """Test symlink security (if supported)"""
        from routers.projects import get_file_code
        from supabase import Client
        
        mock_supabase = MagicMock()
        mock_project = {"id": "test-project", "repo_url": "https://github.com/test/repo.git"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[mock_project]
        )
        
        # Create a symlink within the repository (should be allowed)
        test_file = self.repo_dir / "test.py"
        test_file.write_text("test content")
        symlink_file = self.repo_dir / "link.py"
        
        try:
            symlink_file.symlink_to(test_file)
            
            result = get_file_code(
                project_id="test-project",
                path="link.py",
                repo_path=str(self.repo_dir),
                supabase=mock_supabase
            )
            
            # Should work for legitimate symlinks
            assert "test content" in result or "access denied" in result.lower()
            
        except (OSError, NotImplementedError):
            # Symlinks not supported on this platform
            pytest.skip("Symlinks not supported on this platform")
    
    def test_error_handling(self):
        """Test that errors are handled gracefully"""
        from routers.projects import get_file_code
        from supabase import Client
        
        mock_supabase = MagicMock()
        mock_project = {"id": "test-project", "repo_url": "https://github.com/test/repo.git"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[mock_project]
        )
        
        # Test non-existent file
        result = get_file_code(
            project_id="test-project",
            path="nonexistent.py",
            repo_path=str(self.repo_dir),
            supabase=mock_supabase
        )
        
        # Should return error message, not crash
        assert isinstance(result, str)
        assert "File not found" in result
        
        # Test invalid repository path
        result = get_file_code(
            project_id="test-project",
            path="test.py",
            repo_path="/nonexistent/path",
            supabase=mock_supabase
        )
        
        # Should handle gracefully
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "-s"])