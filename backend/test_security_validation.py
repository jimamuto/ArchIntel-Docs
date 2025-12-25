"""
Security Testing Module for ArchIntel Backend Input Validation

This module provides comprehensive tests for all input validation functionality
including security tests, edge cases, and attack simulations.
"""

import pytest
import json
from fastapi.testclient import TestClient
from fastapi import status
from typing import Dict, Any, List
import requests


class SecurityTestSuite:
    """Comprehensive security test suite for input validation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = TestClient(self.get_app()) if self.base_url == "http://localhost:8000" else None
        
    def get_app(self):
        """Get FastAPI app instance for testing"""
        try:
            from main import app
            return app
        except ImportError:
            return None
    
    def test_repository_url_validation(self):
        """Test repository URL validation against various attack vectors"""
        test_cases = [
            # Valid URLs
            ("https://github.com/user/repo", True, "Valid GitHub URL"),
            ("https://gitlab.com/user/repo", True, "Valid GitLab URL"),
            ("https://bitbucket.org/user/repo", True, "Valid Bitbucket URL"),
            
            # Path traversal attempts
            ("https://example.com/../../../etc/passwd", False, "Path traversal attempt"),
            ("https://github.com/user/repo/../../../etc/passwd", False, "GitHub path traversal"),
            ("https://github.com/user/../root/system", False, "GitHub directory traversal"),
            
            # Protocol manipulation
            ("javascript:alert('xss')", False, "JavaScript protocol"),
            ("data:text/html,<script>alert('xss')</script>", False, "Data URI injection"),
            ("file:///etc/passwd", False, "File protocol"),
            
            # SQL injection patterns
            ("https://github.com/user/repo'; DROP TABLE projects--", False, "SQL injection attempt"),
            ("https://github.com/user/repo?id=1' OR '1'='1", False, "SQL injection in parameter"),
            
            # XSS attempts
            ("https://github.com/user/<script>alert('xss')</script>", False, "XSS in path"),
            ("https://github.com/user/repo?callback=<script>alert('xss')</script>", False, "XSS in parameter"),
            
            # Command injection
            ("https://github.com/user/repo; rm -rf /", False, "Command injection attempt"),
            ("https://github.com/user/repo|cat /etc/passwd", False, "Pipeline injection"),
            
            # Long URLs
            ("https://github.com/" + "a" * 5000 + "/repo", False, "Extremely long URL"),
        ]
        
        results = []
        for url, should_pass, description in test_cases:
            result = self._test_project_creation({"name": "test", "repo_url": url})
            passed = (result.status_code < 400) == should_pass
            results.append({
                "url": url[:100] + "..." if len(url) > 100 else url,
                "should_pass": should_pass,
                "actually_passed": result.status_code < 400,
                "status_code": result.status_code,
                "description": description,
                "test_passed": passed
            })
        
        return results
    
    def test_file_path_validation(self):
        """Test file path validation against traversal attacks"""
        test_cases = [
            # Valid paths
            ("src/main.py", True, "Valid relative path"),
            ("lib/utils/helper.js", True, "Valid nested path"),
            ("README.md", True, "Valid root file"),
            
            # Path traversal attempts
            ("../../../etc/passwd", False, "Basic path traversal"),
            ("..\\..\\windows\\system32", False, "Windows path traversal"),
            ("./../../../etc/passwd", False, "Traversaith dot"),
            ("src/../../etc/passwd", False, "Mixed traversal"),
            
            # Encoded traversal
            ("%2e%2e%2fetc%2fpasswd", False, "URL encoded traversal"),
            ("%2e%2e%5cwindows%5csystem32", False, "URL encoded Windows traversal"),
            ("%252e%252e%252fetc%252fpasswd", False, "Double URL encoded traversal"),
            
            # Special files
            (".git/config", False, "Git config access"),
            ("../.env", False, "Environment file access"),
            ("~/.bashrc", False, "Home directory access"),
            
            # System paths
            ("/etc/passwd", False, "Absolute Unix path"),
            ("C:\\Windows\\System32", False, "Absolute Windows path"),
            ("\\var\\log", False, "Windows network path"),
            
            # Long paths
            ("a" * 1000 + ".txt", False, "Extremely long filename"),
        ]
        
        results = []
        for path, should_pass, description in test_cases:
            result = self._test_file_access("test-project-id", path, ".")
            passed = (result.status_code < 400) == should_pass
            results.append({
                "path": path[:50] + "..." if len(path) > 50 else path,
                "should_pass": should_pass,
                "actually_passed": result.status_code < 400,
                "status_code": result.status_code,
                "description": description,
                "test_passed": passed
            })
        
        return results
    
    def test_search_query_validation(self):
        """Test search query validation against injection attacks"""
        test_cases = [
            # Valid queries
            ("function", True, "Valid search term"),
            ("user authentication", True, "Valid phrase"),
            ("API endpoint", True, "Valid technical term"),
            
            # XSS attempts
            ("<script>alert('xss')</script>", False, "Script tag injection"),
            ("javascript:alert('xss')", False, "JavaScript protocol"),
            ("'><script>alert('xss')</script>", False, "Quote escaping + XSS"),
            ("\";alert('xss');//", False, "JavaScript in quotes"),
            
            # SQL injection
            ("'; DROP TABLE projects--", False, "SQL injection attempt"),
            ("' OR '1'='1", False, "Boolean SQL injection"),
            ("admin';--", False, "Admin bypass attempt"),
            ("1' UNION SELECT * FROM users--", False, "Union SQL injection"),
            
            # Command injection
            ("; rm -rf /", False, "Command injection"),
            ("| cat /etc/passwd", False, "Pipeline injection"),
            ("$(whoami)", False, "Command substitution"),
            
            # Path traversal in search
            ("../../../etc/passwd", False, "Path traversal in search"),
            ("..\\..\\windows", False, "Windows traversal in search"),
            
            # Long queries
            ("a" * 10000, False, "Extremely long query"),
        ]
        
        results = []
        for query, should_pass, description in test_cases:
            result = self._test_search("test-project-id", query)
            passed = (result.status_code < 400) == should_pass
            results.append({
                "query": query[:50] + "..." if len(query) > 50 else query,
                "should_pass": should_pass,
                "actually_passed": result.status_code < 400,
                "status_code": result.status_code,
                "description": description,
                "test_passed": passed
            })
        
        return results
    
    def test_request_size_limits(self):
        """Test request size validation"""
        test_cases = [
            # Valid sizes
            ({"name": "test", "repo_url": "https://github.com/user/repo"}, True, "Normal request"),
            ({"name": "test" * 100, "repo_url": "https://github.com/user/repo"}, True, "Large name field"),
            
            # Oversized requests
            ({"name": "test", "repo_url": "https://github.com/user/repo" + "a" * 50000}, False, "Oversized repo URL"),
            ({"name": "test" * 10000, "repo_url": "https://github.com/user/repo"}, False, "Oversized name field"),
            
            # Nested large objects
            ({"name": "test", "repo_url": "https://github.com/user/repo", 
              "description": "a" * 100000}, False, "Oversized description field"),
        ]
        
        results = []
        for payload, should_pass, description in test_cases:
            result = self._test_project_creation(payload)
            passed = (result.status_code < 400) == should_pass
            results.append({
                "payload_size": len(json.dumps(payload)),
                "should_pass": should_pass,
                "actually_passed": result.status_code < 400,
                "status_code": result.status_code,
                "description": description,
                "test_passed": passed
            })
        
        return results
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        endpoint = "/projects"
        test_results = []
        
        # Make multiple rapid requests
        for i in range(20):
            result = self._make_request("POST", endpoint, {
                "name": f"test-project-{i}",
                "repo_url": f"https://github.com/test/repo{i}"
            })
            
            if i < 15:  # First 15 should pass (assuming rate limit is 100 per minute)
                expected_status = 200 if result.status_code != 429 else 429
                test_results.append({
                    "request_number": i + 1,
                    "status_code": result.status_code,
                    "expected": "pass or rate limit",
                    "actual": "passed" if result.status_code < 400 else "rate limited",
                    "passed": result.status_code != 500  # Should not cause server errors
                })
            else:
                # Later requests might hit rate limits
                test_results.append({
                    "request_number": i + 1,
                    "status_code": result.status_code,
                    "expected": "rate limited or passed",
                    "actual": "rate limited" if result.status_code == 429 else "passed",
                    "passed": result.status_code != 500
                })
            
            if result.status_code == 429:
                retry_after = result.headers.get("Retry-After")
                test_results[-1]["retry_after"] = retry_after
                break
        
        return test_results
    
    def test_content_type_validation(self):
        """Test Content-Type header validation"""
        test_cases = [
            ("application/json", True, "Valid JSON content type"),
            ("application/x-www-form-urlencoded", True, "Valid form content type"),
            ("multipart/form-data", True, "Valid multipart content type"),
            ("text/plain", True, "Valid text content type"),
            ("application/xml", False, "Invalid XML content type"),
            ("text/html", False, "Invalid HTML content type"),
            ("application/javascript", False, "Invalid JS content type"),
        ]
        
        results = []
        for content_type, should_pass, description in test_cases:
            result = self._test_content_type("/projects", content_type, {
                "name": "test", "repo_url": "https://github.com/user/repo"
            })
            
            passed = (result.status_code < 400) == should_pass
            results.append({
                "content_type": content_type,
                "should_pass": should_pass,
                "actually_passed": result.status_code < 400,
                "status_code": result.status_code,
                "description": description,
                "test_passed": passed
            })
        
        return results
    
    def _test_project_creation(self, payload: Dict[str, Any]):
        """Helper method to test project creation"""
        if self.client:
            return self.client.post("/projects", json=payload)
        else:
            return requests.post(f"{self.base_url}/projects", json=payload)
    
    def _test_file_access(self, project_id: str, path: str, repo_path: str):
        """Helper method to test file access"""
        if self.client:
            return self.client.get(f"/docs/{project_id}/file/code", params={"path": path, "repo_path": repo_path})
        else:
            return requests.get(f"{self.base_url}/docs/{project_id}/file/code", params={"path": path, "repo_path": repo_path})
    
    def _test_search(self, project_id: str, query: str):
        """Helper method to test search"""
        if self.client:
            return self.client.post(f"/docs/{project_id}/search", json={"query": query})
        else:
            return requests.post(f"{self.base_url}/docs/{project_id}/search", json={"query": query})
    
    def _test_content_type(self, endpoint: str, content_type: str, payload: Dict[str, Any]):
        """Helper method to test content type validation"""
        if self.client:
            headers = {"Content-Type": content_type}
            return self.client.post(endpoint, data=json.dumps(payload), headers=headers)
        else:
            headers = {"Content-Type": content_type}
            return requests.post(f"{self.base_url}{endpoint}", data=json.dumps(payload), headers=headers)
    
    def _make_request(self, method: str, endpoint: str, payload: Dict[str, Any]):
        """Helper method to make HTTP requests"""
        if self.client:
            if method.upper() == "POST":
                return self.client.post(endpoint, json=payload)
            elif method.upper() == "GET":
                return self.client.get(endpoint, params=payload)
            else:
                return self.client.request(method, endpoint, json=payload)
        else:
            if method.upper() == "POST":
                return requests.post(f"{self.base_url}{endpoint}", json=payload)
            elif method.upper() == "GET":
                return requests.get(f"{self.base_url}{endpoint}", params=payload)
            else:
                return requests.request(method, f"{self.base_url}{endpoint}", json=payload)
    
    def run_all_tests(self):
        """Run all security tests and return comprehensive results"""
        results = {
            "repository_url_validation": self.test_repository_url_validation(),
            "file_path_validation": self.test_file_path_validation(),
            "search_query_validation": self.test_search_query_validation(),
            "request_size_limits": self.test_request_size_limits(),
            "rate_limiting": self.test_rate_limiting(),
            "content_type_validation": self.test_content_type_validation(),
            "summary": {}
        }
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_results in results.items():
            if test_name == "summary":
                continue
            
            if isinstance(test_results, list):
                total_tests += len(test_results)
                passed_tests += sum(1 for r in test_results if r.get("test_passed", False))
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return results
    
    def generate_security_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive security test report"""
        report = ["=" * 60]
        report.append("ARCHINTEL BACKEND SECURITY TEST REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append(f"Test Summary:")
        report.append(f"  Total Tests: {summary['total_tests']}")
        report.append(f"  Passed: {summary['passed_tests']}")
        report.append(f"  Failed: {summary['failed_tests']}")
        report.append(f"  Success Rate: {summary['success_rate']:.2f}%")
        report.append("")
        
        # Detailed results
        for test_name, test_results in results.items():
            if test_name == "summary":
                continue
            
            report.append(f"{'=' * 40}")
            report.append(f"Test: {test_name.replace('_', ' ').title()}")
            report.append(f"{'=' * 40}")
            
            if isinstance(test_results, list):
                passed_count = sum(1 for r in test_results if r.get("test_passed", False))
                report.append(f"Passed: {passed_count}/{len(test_results)}")
                
                # Show failed tests
                failed_tests = [r for r in test_results if not r.get("test_passed", False)]
                if failed_tests:
                    report.append("Failed Tests:")
                    for test in failed_tests[:5]:  # Show first 5 failures
                        report.append(f"  - {test.get('description', 'Unknown test')}")
                        report.append(f"    Expected: {'Pass' if test.get('should_pass') else 'Fail'}")
                        report.append(f"    Actual: {'Pass' if test.get('actually_passed') else 'Fail'}")
                        report.append(f"    Status Code: {test.get('status_code')}")
                    if len(failed_tests) > 5:
                        report.append(f"    ... and {len(failed_tests) - 5} more")
                else:
                    report.append("All tests passed! ✓")
            
            report.append("")
        
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)
        
        return "\n".join(report)


def run_security_tests():
    """Run security tests and print results"""
    test_suite = SecurityTestSuite()
    results = test_suite.run_all_tests()
    report = test_suite.generate_security_report(results)
    
    print(report)
    
    # Save results to file
    with open("security_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    results = run_security_tests()
    print(f"\nSecurity test results saved to security_test_results.json")
    print(f"Overall success rate: {results['summary']['success_rate']:.2f}%")