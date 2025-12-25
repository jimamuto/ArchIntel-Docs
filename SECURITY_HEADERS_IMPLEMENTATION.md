"""
Security Headers Implementation Guide for ArchIntel Backend

This document provides a comprehensive guide for implementing security headers
in the ArchIntel FastAPI backend to protect against common web vulnerabilities.

## Overview

Security headers are HTTP response headers that help protect web applications
from common vulnerabilities such as XSS, clickjacking, MIME type sniffing,
and protocol downgrade attacks.

## Security Headers Implemented

### 1. Content Security Policy (CSP)
- **Purpose**: Prevents XSS attacks by controlling resource loading
- **Directives**: 
  - `default-src 'self'`: Default policy allows only same-origin resources
  - `script-src`: Controls JavaScript execution
  - `style-src`: Controls CSS loading
  - `img-src`: Controls image loading
  - `connect-src`: Controls AJAX/fetch requests
  - `object-src 'none'`: Disables plugins (Flash, etc.)
  - `frame-ancestors 'none'`: Prevents clickjacking

### 2. HTTP Strict Transport Security (HSTS)
- **Purpose**: Enforces HTTPS connections
- **Configuration**: `max-age=31536000; includeSubDomains; preload`
- **Environment**: Only in production

### 3. X-Frame-Options
- **Purpose**: Prevents clickjacking attacks
- **Value**: `DENY` (prevents any framing)

### 4. X-Content-Type-Options
- **Purpose**: Prevents MIME type sniffing
- **Value**: `nosniff`

### 5. X-XSS-Protection
- **Purpose**: Legacy XSS protection for older browsers
- **Value**: `1; mode=block`

### 6. Referrer-Policy
- **Purpose**: Controls referrer information in requests
- **Value**: `strict-origin-when-cross-origin`

### 7. X-Permitted-Cross-Domain-Policies
- **Purpose**: Controls cross-domain policy for Adobe products
- **Value**: `none`

### 8. Permissions-Policy (formerly Feature-Policy)
- **Purpose**: Controls browser features and APIs
- **Disabled**: geolocation, microphone, camera, payment, etc.

## Environment-Specific Configuration

### Development Mode
- Relaxed CSP for debugging (allows 'unsafe-inline', 'unsafe-eval')
- Server headers preserved for development
- Nonce-based CSP disabled for easier debugging

### Production Mode
- Strict CSP with nonce-based inline scripts
- Server headers removed
- HSTS enabled
- All security headers enforced

## Implementation Files

### 1. `backend/middleware/security_headers.py`
- Main security headers middleware implementation
- Environment-specific configuration
- CSP policy generation
- Header validation utilities

### 2. `backend/main.py`
- Middleware registration
- Environment configuration
- Error handling integration

### 3. `backend/services/csp_reporting.py`
- CSP violation analysis and reporting
- Security monitoring integration
- Violation categorization

### 4. `backend/routers/csp.py`
- CSP violation reporting endpoint
- CSP status monitoring endpoint

## Configuration

### Environment Variables
```bash
ENVIRONMENT=production  # or development
HSTS_MAX_AGE=31536000   # 1 year in seconds
HSTS_INCLUDE_SUBDOMAINS=true
HSTS_PRELOAD=true
CONTENT_SECURITY_POLICY=...  # Custom CSP (optional)
```

### Default Headers
```python
{
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'nonce-...'; ...",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

## Security Monitoring

### CSP Violation Reporting
- Violations are logged to security event logger
- Real-time violation analysis
- Risk assessment (LOW, MEDIUM, HIGH, CRITICAL)
- Alert generation for high-risk violations

### Monitoring Endpoints
- `GET /api/v1/csp-status`: Get CSP configuration and statistics
- `POST /api/v1/csp-report`: Submit CSP violation reports

## Testing

### Automated Tests
- Security headers presence verification
- Header value validation
- Environment-specific behavior
- CSP violation reporting functionality

### Manual Testing
```bash
# Test with curl
curl -I https://your-app.com/

# Check specific headers
curl -I https://your-app.com/ | grep -i "content-security-policy\|x-frame-options\|strict-transport-security"
```

### Browser Developer Tools
- Network tab to inspect response headers
- Console for CSP violations
- Security tab for header analysis

## Troubleshooting

### Common Issues

1. **CSP Blocking Resources**
   - Check CSP policy in development mode
   - Add necessary domains to CSP directives
   - Use nonces for inline scripts

2. **HSTS Issues**
   - Only enabled in production
   - Requires HTTPS
   - Clear HSTS cache if needed

3. **Development Debugging**
   - Use development mode for relaxed headers
   - Check browser console for CSP violations
   - Use network inspection tools

### CSP Violation Debugging
1. Check browser console for violation reports
2. Use `report-uri` directive to send reports to server
3. Analyze violation patterns in security logs
4. Adjust CSP policy based on legitimate needs

## Security Best Practices

1. **Regular Policy Review**
   - Review CSP policies regularly
   - Remove unnecessary permissions
   - Stay updated with security best practices

2. **Monitoring and Alerting**
   - Monitor CSP violation reports
   - Set up alerts for high-risk violations
   - Regular security header audits

3. **Environment Management**
   - Use strict headers in production
   - Use relaxed headers in development
   - Clear separation between environments

4. **Documentation and Training**
   - Document security header configuration
   - Train developers on CSP and security headers
   - Maintain security guidelines

## Integration with Existing Security

### CORS Integration
- Security headers work alongside CORS configuration
- No conflicts with existing CORS settings
- Enhanced protection when used together

### Authentication Integration
- Security headers complement authentication
- Additional layer of protection
- No impact on authentication flows

### Error Handling Integration
- Security headers applied to error responses
- Consistent security across all responses
- Secure error message handling

## Future Enhancements

1. **Dynamic CSP**
   - Runtime CSP policy updates
   - User-specific policies
   - Adaptive security based on threat level

2. **Enhanced Monitoring**
   - Real-time security dashboard
   - Advanced threat detection
   - Automated policy tuning

3. **Additional Headers**
   - Expect-CT header for certificate transparency
   - Public-Key-Pins for key pinning
   - Cross-Origin-Embedder-Policy for isolation

This implementation provides comprehensive protection against common web vulnerabilities
while maintaining application functionality and developer productivity.