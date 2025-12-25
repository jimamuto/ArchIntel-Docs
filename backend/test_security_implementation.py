"""
Test script to verify secure error handling implementation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
def test_imports():
    """Test that all security modules can be imported"""
    try:
        from services.error_handler import error_handler, ERROR_CODES, ERROR_CATEGORIES
        print("✓ Error handler imported successfully")
        
        from exceptions import SecurityError, AuthenticationError, AuthorizationError
        print("✓ Custom exceptions imported successfully")
        
        from services.security_monitoring import security_monitor, SecurityAlert
        print("✓ Security monitoring imported successfully")
        
        from services.security_config import SecurityConfig, SecurityConstants
        print("✓ Security configuration imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_error_handler():
    """Test error handler functionality"""
    try:
        from services.error_handler import error_handler, create_error_response
        from exceptions import AuthenticationError
        
        # Test error creation
        auth_error = AuthenticationError("Invalid credentials")
        print("✓ Custom exception created")
        
        # Test error response creation
        response = create_error_response("AUTH_INVALID_TOKEN", "Authentication failed", 401)
        print("✓ Error response created")
        
        # Test error handling
        try:
            raise auth_error
        except Exception as e:
            handled = error_handler.handle_error(e)
            print("✓ Error handling works")
        
        return True
    except Exception as e:
        print(f"✗ Error handler test failed: {e}")
        return False

def test_security_monitoring():
    """Test security monitoring functionality"""
    try:
        from services.security_monitoring import security_monitor
        
        # Test monitoring status
        status = security_monitor.get_security_status()
        print("✓ Security monitoring status retrieved")
        
        # Test threat indicators
        indicators = security_monitor.get_threat_indicators()
        print("✓ Threat indicators retrieved")
        
        return True
    except Exception as e:
        print(f"✗ Security monitoring test failed: {e}")
        return False

def test_configuration():
    """Test security configuration"""
    try:
        from services.security_config import SecurityConfig, SecurityConstants
        
        # Test configuration validation
        issues = SecurityConfig.validate_config()
        print(f"✓ Configuration validation completed (issues: {len(issues)})")
        
        # Test policy retrieval
        policy = SecurityConfig.get_security_policy()
        print("✓ Security policy retrieved")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing ArchIntel Secure Error Handling Implementation")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Error Handler Tests", test_error_handler),
        ("Security Monitoring Tests", test_security_monitoring),
        ("Configuration Tests", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"Failed: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Secure error handling is ready.")
        return True
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)