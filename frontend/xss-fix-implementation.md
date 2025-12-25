# XSS Vulnerability Fix Implementation

## Summary

This document provides the specific code changes needed to fix the XSS vulnerability in the ArchIntel Mermaid component at `frontend/pages/docs.js:95`.

## 1. Core Fix: Secure SVG Rendering

### 1.1 Import DOMPurify
Add to the imports section in `frontend/pages/docs.js`:

```javascript
import DOMPurify from 'dompurify';
```

### 1.2 Replace Vulnerable Code (Line 95)
**Current vulnerable code:**
```javascript
ref.current.innerHTML = svg;
```

**Secure replacement:**
```javascript
// Secure SVG rendering with sanitization
const sanitizeAndRenderSVG = (svgContent) => {
  try {
    // Configure DOMPurify for SVG content
    const config = {
      USE_PROFILES: { svg: true, svgFilters: true },
      ADD_ATTR: ['target'], // Allow safe attributes
      FORBID_ATTR: [
        'onerror', 'onload', 'onclick', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onkeydown', 'onkeyup', 'onkeypress'
      ], // Explicitly forbid dangerous attributes
      ADD_TAGS: ['foreignobject'], // Allow SVG foreignObject if needed
    };
    
    // Sanitize the SVG content
    const cleanSVG = DOMPurify.sanitize(svgContent, config);
    
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

// In the Mermaid render function, replace line 95:
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

## 2. Enhanced Input Validation

### 2.1 Add Mermaid Content Validation
Add this function before the Mermaid component:

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
    /<embed[\s\S]*?>[\s\S]*?<\/embed>/gi,
    /<form[\s\S]*?>[\s\S]*?<\/form>/gi,
    /<input[\s\S]*?>/gi
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(chartContent)) {
      throw new Error('Potentially malicious content detected in chart');
    }
  }

  // Limit content size to prevent DoS
  if (chartContent.length > 50000) {
    throw new Error('Chart content too large');
  }

  // Validate Mermaid syntax (basic check)
  const mermaidKeywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'requirementDiagram'];
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

### 2.2 Update Mermaid Component to Use Validation
In the Mermaid component's useEffect, add validation:

```javascript
useEffect(() => {
  if (ref.current && chart) {
    setError(null);
    ref.current.removeAttribute('data-processed');

    // Pre-process chart to remove potential LLM mess-ups
    let cleanedChart = String(chart).trim();

    // Remove markdown code fences if they were accidentally included by LLM or parser
    cleanedChart = cleanedChart.replace(/^```mermaid\n?/, '').replace(/\n?```$/, '');

    // Fix common LLM arrow syntax errors: -->|label|> should be -->|"label"|
    // This regex matches patterns like -->|text|> and converts to -->|"text"|
    cleanedChart = cleanedChart.replace(/-->\|([^|]+)\|>/g, '-->|"$1"|');

    // Also fix the variant without the initial arrow: --|text|>
    cleanedChart = cleanedChart.replace(/--\|([^|]+)\|>/g, '--|"$1"|');

    // Validate content before processing
    try {
      validateMermaidContent(cleanedChart);
    } catch (validationError) {
      setError(validationError.message);
      return;
    }

    // Ensure the chart starts with a valid Mermaid keyword (ignoring comments)
    const validKeywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'requirementDiagram'];
    const lines = cleanedChart.split('\n');
    const firstLine = lines[0].trim();
    const hasKeyword = validKeywords.some(keyword => firstLine.toLowerCase().startsWith(keyword.toLowerCase()));

    if (!hasKeyword && !firstLine.startsWith('%%')) {
      // If no keyword, try to fix it if it looks like a flowchart
      if (cleanedChart.includes('-->')) {
        cleanedChart = 'graph TD\n' + cleanedChart;
      }
    }

    console.log('Rendering Mermaid chart:', cleanedChart);

    const uniqueId = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

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
  }
}, [chart]);
```

## 3. Secure Error Handling

### 3.1 Update Error Messages
Replace error handling to prevent information leakage:

```javascript
// Secure error handling function
const handleMermaidError = (error) => {
  console.error('Mermaid rendering error:', error);
  
  // Don't expose detailed error information to users
  if (error?.message?.includes('malicious') || 
      error?.message?.includes('script') || 
      error?.message?.includes('XSS')) {
    return 'Failed to render diagram: Invalid content detected';
  }
  
  if (error?.message?.includes('syntax') || 
      error?.message?.includes('parse')) {
    return 'Failed to render diagram: Please check the syntax';
  }
  
  return 'Failed to render diagram: Please try again';
};
```

### 3.2 Update Error Display in Component
In the error rendering section:

```javascript
if (error) {
  return (
    <div className="my-6 p-6 rounded-xl border border-red-500/20 bg-red-500/5 text-center">
      <p className="text-sm text-red-400 font-medium mb-1">Visual Generation Error</p>
      <p className="text-xs text-red-400/70 font-mono">{handleMermaidError(new Error(error))}</p>
      <details className="mt-3 text-left">
        <summary className="text-[10px] text-gray-500 cursor-pointer hover:text-gray-400 underline uppercase tracking-widest">Show Source Code</summary>
        <pre className="mt-2 p-3 bg-black/40 rounded text-[10px] text-gray-400 overflow-x-auto border border-white/5">
          {chart}
        </pre>
      </details>
    </div>
  );
}
```

## 4. Content Security Policy (CSP)

### 4.1 Create/Update Next.js Configuration
Create `next.config.js` if it doesn't exist:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React Strict Mode for development
  reactStrictMode: true,
  
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
              "connect-src 'self'", // Restrict network connections
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
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          }
        ]
      }
    ];
  }
};

module.exports = nextConfig;
```

## 5. Testing Implementation

### 5.1 Create Test File
Create `__tests__/mermaid-security.test.js`:

```javascript
import { render } from '@testing-library/react';
import Mermaid from '../pages/docs';

// Mock DOMPurify
jest.mock('dompurify', () => ({
  sanitize: jest.fn((content) => content.replace(/<script.*?<\/script>/gi, ''))
}));

describe('Mermaid XSS Protection', () => {
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
  });

  test('should sanitize SVG with script tags', () => {
    const maliciousChart = `
      graph TD
        A[Start] --> B[<script>alert("XSS")</script>Process]
        B --> C[End]
    `;

    const { container } = render(<Mermaid chart={maliciousChart} />);
    
    // Check that script tags are removed
    expect(container.innerHTML).not.toContain('<script>');
  });

  test('should handle event handlers safely', () => {
    const maliciousChart = `
      graph TD
        A[Click me] --> B{<div onclick="alert('XSS')">Decision</div>}
    `;

    const { container } = render(<Mermaid chart={maliciousChart} />);
    
    // Check that onclick handlers are removed
    expect(container.innerHTML).not.toContain('onclick');
  });

  test('should validate chart content size', () => {
    const largeChart = 'graph TD\n' + 'A --> B\n'.repeat(10000);

    const { container } = render(<Mermaid chart={largeChart} />);
    
    // Should show error for large content
    expect(container.textContent).toContain('Chart content too large');
  });

  test('should handle invalid syntax gracefully', () => {
    const invalidChart = 'not a valid mermaid syntax';

    const { container } = render(<Mermaid chart={invalidChart} />);
    
    // Should show syntax error
    expect(container.textContent).toContain('Invalid Mermaid syntax');
  });

  test('should render safe content correctly', () => {
    const safeChart = `
      graph TD
        A[Start] --> B[Process]
        B --> C[End]
    `;

    const { container } = render(<Mermaid chart={safeChart} />);
    
    // Should render without errors
    expect(container.querySelector('.mermaid')).toBeInTheDocument();
  });
});
```

### 5.2 Run Tests
```bash
npm test -- mermaid-security.test.js
```

## 6. Performance Considerations

### 6.1 Add Performance Monitoring
Add performance tracking to the sanitization function:

```javascript
const sanitizeAndRenderSVG = (svgContent) => {
  const startTime = performance.now();
  
  try {
    const config = {
      USE_PROFILES: { svg: true, svgFilters: true },
      FORBID_ATTR: [
        'onerror', 'onload', 'onclick', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onkeydown', 'onkeyup', 'onkeypress'
      ],
    };
    
    const cleanSVG = DOMPurify.sanitize(svgContent, config);
    
    // Performance logging (development only)
    if (process.env.NODE_ENV === 'development') {
      const duration = performance.now() - startTime;
      if (duration > 50) { // Log slow operations
        console.warn(`SVG sanitization took ${duration.toFixed(2)}ms`);
      }
    }
    
    return cleanSVG;
  } catch (error) {
    console.error('SVG sanitization failed:', error);
    throw new Error('Failed to sanitize SVG content');
  }
};
```

## 7. Deployment Checklist

### 7.1 Pre-Deployment
- [ ] Run security tests
- [ ] Verify CSP headers are applied
- [ ] Test with existing Mermaid diagrams
- [ ] Performance testing with large diagrams
- [ ] Cross-browser testing

### 7.2 Post-Deployment
- [ ] Monitor error logs for sanitization failures
- [ ] Check CSP violation reports
- [ ] Verify no functionality is broken
- [ ] Performance monitoring

## 8. Rollback Plan

If issues are discovered:

1. **Feature Flag**: Implement a feature flag to disable sanitization temporarily
2. **Environment Variables**: Use `NEXT_PUBLIC_ENABLE_XSS_PROTECTION=false` to disable
3. **Quick Rollback**: Revert to original `innerHTML` usage if critical issues found

```javascript
// Add to configuration
const ENABLE_XSS_PROTECTION = process.env.NEXT_PUBLIC_ENABLE_XSS_PROTECTION !== 'false';

const sanitizeAndRenderSVG = (svgContent) => {
  if (!ENABLE_XSS_PROTECTION) {
    return svgContent; // Fallback to original behavior
  }
  
  // ... sanitization logic
};
```

This implementation provides comprehensive XSS protection while maintaining backward compatibility and performance.