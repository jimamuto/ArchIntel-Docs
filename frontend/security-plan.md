# XSS Vulnerability Fix Plan for ArchIntel Mermaid Component

## Executive Summary

The XSS vulnerability in `frontend/pages/docs.js:95` is caused by direct injection of unsanitized SVG content from Mermaid into the DOM using `innerHTML`. This allows malicious content to execute JavaScript code. The fix involves implementing proper SVG sanitization, Content Security Policy (CSP), and secure error handling.

## Vulnerability Analysis

### Current Vulnerable Code (Line 95)
```javascript
ref.current.innerHTML = svg;
```

### Attack Vectors
1. **SVG Script Injection**: Malicious Mermaid diagrams containing `<script>` tags
2. **Event Handler Injection**: SVG elements with `onclick`, `onload` attributes
3. **Data URI Execution**: SVG with embedded JavaScript via data URIs
4. **SVG Filter Exploits**: CSS-based XSS through SVG filters
5. **External Entity Injection**: SVG referencing external malicious resources

### Impact Assessment
- **Severity**: Critical (XSS allows full client-side code execution)
- **Affected Users**: All users viewing generated documentation
- **Data Exposure**: Session tokens, cookies, and user data at risk
- **System Compromise**: Potential for account takeover and data theft

## Implementation Plan

### Phase 1: Immediate Fix - SVG Sanitization

#### 1.1 Add DOMPurify Dependency
```bash
npm install dompurify
```

#### 1.2 Implement Secure SVG Rendering
Replace the vulnerable code in `frontend/pages/docs.js:95`:

```javascript
// Import DOMPurify
import DOMPurify from 'dompurify';

// Secure SVG rendering function
const sanitizeAndRenderSVG = (svg) => {
  try {
    // Configure DOMPurify for SVG content
    const config = {
      USE_PROFILES: { svg: true, svgFilters: true },
      ADD_ATTR: ['target'], // Allow safe attributes
      FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover'], // Explicitly forbid dangerous attributes
    };
    
    // Sanitize the SVG content
    const cleanSVG = DOMPurify.sanitize(svg, config);
    
    // Additional validation for SVG structure
    if (!cleanSVG.includes('<svg') || !cleanSVG.includes('</svg>')) {
      throw new Error('Invalid SVG structure');
    }
    
    return cleanSVG;
  } catch (error) {
    console.error('SVG sanitization failed:', error);
    throw new Error('Failed to sanitize SVG content');
  }
};

// In the Mermaid component render function:
try {
  mermaid.render(uniqueId, cleanedChart)
    .then(({ svg }) => {
      if (ref.current) {
        const sanitizedSVG = sanitizeAndRenderSVG(svg);
        ref.current.innerHTML = sanitizedSVG;
      }
    })
    .catch((err) => {
      console.error('Mermaid async error:', err);
      setError(err?.message || 'Syntax error in diagram description');
    });
} catch (err) {
  console.error('Mermaid sync error:', err);
  setError(err?.message || 'Failed to initialize rendering');
}
```

### Phase 2: Content Security Policy (CSP)

#### 2.1 Update Next.js Configuration
Create/update `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // ... existing config
  
  // Security headers including CSP
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Allow Mermaid execution
              "style-src 'self' 'unsafe-inline'", // Allow Mermaid styles
              "img-src 'self' data:", // Allow data URIs for SVG
              "font-src 'self'",
              "connect-src 'self' https://api.mermaid.ink", // Allow Mermaid CDN if used
              "object-src 'none'",
              "base-uri 'self'",
              "form-action 'self'",
              "frame-ancestors 'none'",
              "upgrade-insecure-requests"
            ].join('; ')
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          }
        ]
      }
    ];
  }
};

module.exports = nextConfig;
```

#### 2.2 Environment-Specific CSP
Create CSP configuration for different environments:

```javascript
// lib/security.js
export const getCSPConfig = () => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  const baseDirectives = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", 'data:'],
    'font-src': ["'self'"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  };

  if (isDevelopment) {
    baseDirectives['script-src'].push("'unsafe-eval'");
  }

  return baseDirectives;
};
```

### Phase 3: Enhanced Input Validation

#### 3.1 Mermaid Content Validation
Add validation before Mermaid processing:

```javascript
// Enhanced chart validation function
const validateMermaidContent = (chartContent) => {
  if (!chartContent || typeof chartContent !== 'string') {
    throw new Error('Invalid chart content');
  }

  // Check for common XSS patterns
  const dangerousPatterns = [
    /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
    /javascript:/gi,
    /data:\s*text\/javascript/gi,
    /on\w+\s*=/gi,
    /<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi,
    /<object[\s\S]*?>[\s\S]*?<\/object>/gi,
    /<embed[\s\S]*?>[\s\S]*?<\/embed>/gi
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(chartContent)) {
      throw new Error('Potentially malicious content detected');
    }
  }

  // Limit content size to prevent DoS
  if (chartContent.length > 50000) {
    throw new Error('Chart content too large');
  }

  // Validate Mermaid syntax (basic check)
  const mermaidKeywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram'];
  const trimmed = chartContent.trim();
  const hasValidKeyword = mermaidKeywords.some(keyword => 
    trimmed.toLowerCase().startsWith(keyword.toLowerCase())
  );

  if (!hasValidKeyword && !trimmed.startsWith('%%')) {
    throw new Error('Invalid Mermaid syntax');
  }

  return true;
};
```

### Phase 4: Secure Error Handling

#### 4.1 Non-Informational Error Messages
Update error handling to prevent information leakage:

```javascript
// Secure error handling
const handleMermaidError = (error) => {
  console.error('Mermaid rendering error:', error);
  
  // Don't expose detailed error information to users
  if (error?.message?.includes('malicious') || error?.message?.includes('script')) {
    return 'Failed to render diagram: Invalid content detected';
  }
  
  return 'Failed to render diagram: Please check the syntax';
};

// In the component error handling:
.catch((err) => {
  console.error('Mermaid async error:', err);
  setError(handleMermaidError(err));
})
.catch((err) => {
  console.error('Mermaid sync error:', err);
  setError(handleMermaidError(err));
});
```

#### 4.2 Error Logging Service
Create centralized error logging:

```javascript
// lib/error-logger.js
export const logSecurityError = (error, context = {}) => {
  const errorData = {
    timestamp: new Date().toISOString(),
    error: error?.message || String(error),
    stack: error?.stack,
    context,
    userAgent: navigator.userAgent,
    url: window.location.href
  };

  // Send to secure logging endpoint
  fetch('/api/security-logs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(errorData)
  }).catch(console.error);
};
```

### Phase 5: Testing Strategy

#### 5.1 XSS Test Cases
Create comprehensive test suite:

```javascript
// __tests__/security.test.js
describe('Mermaid XSS Protection', () => {
  test('should sanitize SVG with script tags', () => {
    const maliciousSVG = `
      <svg>
        <script>alert('XSS')</script>
        <rect x="10" y="10" width="100" height="100"/>
      </svg>
    `;
    
    const sanitized = sanitizeAndRenderSVG(maliciousSVG);
    expect(sanitized).not.toContain('<script>');
    expect(sanitized).toContain('<rect');
  });

  test('should block event handlers', () => {
    const maliciousSVG = `
      <svg>
        <rect onclick="alert('XSS')" x="10" y="10" width="100" height="100"/>
      </svg>
    `;
    
    const sanitized = sanitizeAndRenderSVG(maliciousSVG);
    expect(sanitized).not.toContain('onclick');
  });

  test('should handle JavaScript URIs', () => {
    const maliciousContent = 'javascript:alert("XSS")';
    expect(() => validateMermaidContent(maliciousContent)).toThrow();
  });

  test('should allow safe SVG content', () => {
    const safeSVG = `
      <svg>
        <rect x="10" y="10" width="100" height="100" fill="blue"/>
        <circle cx="50" cy="50" r="20" fill="red"/>
      </svg>
    `;
    
    const sanitized = sanitizeAndRenderSVG(safeSVG);
    expect(sanitized).toContain('<rect');
    expect(sanitized).toContain('<circle');
  });
});
```

#### 5.2 Performance Testing
Ensure sanitization doesn't impact performance:

```javascript
// Performance test
test('sanitization performance', () => {
  const largeSVG = generateLargeSVG(); // 1000+ elements
  const start = performance.now();
  
  sanitizeAndRenderSVG(largeSVG);
  
  const duration = performance.now() - start;
  expect(duration).toBeLessThan(100); // Should complete in <100ms
});
```

### Phase 6: Backward Compatibility

#### 6.1 Graceful Degradation
Ensure existing functionality remains intact:

```javascript
// Fallback mechanism
const sanitizeAndRenderSVG = (svg) => {
  try {
    // Primary sanitization
    return DOMPurify.sanitize(svg, {
      USE_PROFILES: { svg: true },
      FORBID_ATTR: ['onerror', 'onload', 'onclick']
    });
  } catch (error) {
    console.warn('DOMPurify failed, using fallback sanitization:', error);
    
    // Fallback: Remove all potentially dangerous elements
    return svg
      .replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .replace(/javascript:/gi, '');
  }
};
```

#### 6.2 Feature Flags
Implement gradual rollout:

```javascript
// config/security.js
export const securityConfig = {
  enableXSSProtection: process.env.NEXT_PUBLIC_ENABLE_XSS_PROTECTION !== 'false',
  enableCSP: process.env.NEXT_PUBLIC_ENABLE_CSP !== 'false',
  logSecurityEvents: process.env.NEXT_PUBLIC_LOG_SECURITY_EVENTS === 'true'
};
```

## Implementation Timeline

### Week 1: Core Security Fix
- [ ] Install DOMPurify dependency
- [ ] Implement SVG sanitization in Mermaid component
- [ ] Add input validation for Mermaid content
- [ ] Update error handling

### Week 2: CSP and Headers
- [ ] Configure Content Security Policy
- [ ] Add security headers via Next.js config
- [ ] Test CSP in different environments

### Week 3: Testing and Validation
- [ ] Write comprehensive XSS test cases
- [ ] Performance testing
- [ ] Security audit of the implementation
- [ ] Cross-browser compatibility testing

### Week 4: Deployment and Monitoring
- [ ] Deploy to staging environment
- [ ] Monitor for security events
- [ ] User acceptance testing
- [ ] Production deployment

## Security Considerations

### 1. Defense in Depth
- Multiple layers of protection (input validation, sanitization, CSP)
- Fail-safe defaults (block unknown content)
- Regular security reviews

### 2. Monitoring and Alerting
- Log all sanitization failures
- Monitor for XSS attack patterns
- Alert on security configuration changes

### 3. Documentation and Training
- Document security practices for developers
- Create incident response procedures
- Regular security awareness training

## Success Metrics

1. **Security**: Zero XSS vulnerabilities in security scans
2. **Performance**: <5% impact on page load times
3. **Compatibility**: 100% existing functionality preserved
4. **User Experience**: No degradation in diagram rendering quality

## Risk Mitigation

### High Risk Items
- **DOMPurify Compatibility**: Test thoroughly with existing Mermaid diagrams
- **CSP Conflicts**: Careful CSP configuration to avoid breaking functionality
- **Performance Impact**: Monitor rendering performance with large diagrams

### Contingency Plans
- **Rollback Strategy**: Feature flags allow quick disabling
- **Alternative Libraries**: Research alternative sanitization libraries
- **Manual Review**: Fallback to manual content review if automated fails

## Conclusion

This comprehensive security plan addresses the XSS vulnerability through multiple layers of protection while maintaining backward compatibility and performance. The implementation follows security best practices and includes thorough testing to ensure the fix is robust and reliable.