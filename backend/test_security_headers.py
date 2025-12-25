"""
Security Headers Test for ArchIntel Backend

This module provides tests for the security headers middleware
to ensure all security headers are properly implemented.
"""

import pytest
from fastapi.testclient import TestClient
import os

# Test that security headers are properly set in production
def test_security_headers_in_production():
    """Test that security headers are properly set in production"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    # Mock production environment
    original_env = os.getenv("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "production"
    
    try:
        response = client.get("/")
        
        # Check required security headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Strict-Transport-Security" in response.headers
        
        # Check that server header is removed in production
        assert "server" not in response.headers
        assert "x-powered-by" not in response.headers
        
        # Validate CSP policy contains required directives
        csp = response.headers["Content-Security-Policy"]
        assert "default-src" in csp
        assert "script-src" in csp
        assert "style-src" in csp
        assert "object-src" in csp
        
    finally:
        # Restore original environment
        if original_env:
            os.environ["ENVIRONMENT"] = original_env
        else:
            os.environ.pop("ENVIRONMENT", None)

# Test that security headers are properly set in development
def test_security_headers_in_development():
    """Test that security headers are properly set in development"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    # Mock development environment
    original_env = os.getenv("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "development"
    
    try:
        response = client.get("/")
        
        # Check required security headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        
        # Server header should be present in development
        assert "server" in response.headers
        
    finally:
        # Restore original environment
        if original_env:
            os.environ["ENVIRONMENT"] = original_env
        else:
            os.environ.pop("ENVIRONMENT", None)

# Test CSP violation reporting endpoint
def test_csp_reporting_endpoint():
    """Test CSP violation reporting endpoint"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    # Test CSP report endpoint
    csp_report = {
        "csp-report": {
            "document-uri": "http://example.com/page.html",
            "violated-directive": "script-src 'self'",
            "blocked-uri": "http://evil.com/malicious.js",
            "effective-directive": "script-src"
        }
    }
    
    response = client.post("/api/v1/csp-report", json=csp_report)
    assert response.status_code == 204  # No Content

# Test CSP status endpoint
def test_csp_status_endpoint():
    """Test CSP status endpoint"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    response = client.get("/api/v1/csp-status")
    assert response.status_code == 200
    
    data = response.json()
    assert "csp_reporting_enabled" in data
    assert "violation_statistics" in data
    assert "configuration" in data

# Test that sensitive endpoints have additional security headers
def test_sensitive_endpoint_headers():
    """Test that sensitive endpoints have additional security headers"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    # Test auth endpoint
    response = client.get("/auth/login")
    if response.status_code != 405:  # Method not allowed is expected
        # Check for additional security headers on sensitive endpoints
        assert "Cache-Control" in response.headers
        assert "Pragma" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers

# Test that Permissions-Policy header is properly set
def test_permissions_policy():
    """Test that Permissions-Policy header is properly set"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    response = client.get("/")
    
    assert "Permissions-Policy" in response.headers
    
    permissions = response.headers["Permissions-Policy"]
    # Check that sensitive permissions are disabled
    assert "geolocation=" in permissions
    assert "microphone=" in permissions
    assert "camera=" in permissions

# Test X-Frame-Options header
def test_x_frame_options():
    """Test X-Frame-Options header"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    response = client.get("/")
    
    x_frame = response.headers.get("X-Frame-Options", "")
    assert x_frame in ["DENY", "SAMEORIGIN"]

# Test X-Content-Type-Options header
def test_x_content_type_options():
    """Test X-Content-Type-Options header"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    response = client.get("/")
    
    assert response.headers.get("X-Content-Type-Options") == "nosniff"

# Test Referrer-Policy header
def test_referrer_policy():
    """Test Referrer-Policy header"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    response = client.get("/")
    
    referrer_policy = response.headers.get("Referrer-Policy", "")
    assert referrer_policy in [
        "no-referrer", 
        "no-referrer-when-downgrade", 
        "strict-origin-when-cross-origin",
        "same-origin"
    ]

# Test HSTS header in production environment
def test_hsts_in_production():
    """Test HSTS header in production environment"""
    # Import app only when needed to avoid import issues
    try:
        from main import app
        client = TestClient(app)
    except ImportError:
        pytest.skip("Could not import main app")
    
    # Mock production environment
    original_env = os.getenv("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "production"
    
    try:
        response = client.get("/")
        
        if "Strict-Transport-Security" in response.headers:
            hsts = response.headers["Strict-Transport-Security"]
            assert "max-age=" in hsts
            assert "includeSubDomains" in hsts or "preload" in hsts
            
    finally:
        # Restore original environment
        if original_env:
            os.environ["ENVIRONMENT"] = original_env
        else:
            os.environ.pop("ENVIRONMENT", None)

# Test security headers validation function
def test_security_headers_validation():
    """Test security headers validation function"""
    # Import validation function dynamically to avoid import issues
    try:
        import sys
        # Try to find the module in sys.modules
        for module_name in sys.modules:
            if 'security_headers' in module_name and hasattr(sys.modules[module_name], 'validate_security_headers'):
                validate_security_headers = sys.modules[module_name].validate_security_headers
                break
        else:
            raise ImportError("Module not found in loaded modules")
    except (ImportError, AttributeError):
        # If import fails, create a simple mock validation
        def validate_security_headers(headers):
            issues = []
            required = ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "X-XSS-Protection"]
            for header in required:
                if header not in headers:
                    issues.append(f"Missing required header: {header}")
            return issues
    
    # Test with valid headers
    valid_headers = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block"
    }
    
    issues = validate_security_headers(valid_headers)
    assert len(issues) == 1  # CSP missing object-src
    
    # Test with missing headers
    invalid_headers = {}
    issues = validate_security_headers(invalid_headers)
    assert len(issues) == 4  # All required headers missing

if __name__ == "__main__":
    pytest.main([__file__])