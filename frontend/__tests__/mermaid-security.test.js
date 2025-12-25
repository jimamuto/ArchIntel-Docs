import React from 'react';
import { render, screen } from '@testing-library/react';
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

    render(<Mermaid chart={maliciousChart} />);
    
    // Check that script tags are removed
    expect(screen.getByRole('mermaid')).toBeInTheDocument();
  });

  test('should handle event handlers safely', () => {
    const maliciousChart = `
      graph TD
        A[Click me] --> B{<div onclick="alert('XSS')">Decision</div>}
    `;

    render(<Mermaid chart={maliciousChart} />);
    
    // Check that onclick handlers are removed
    expect(screen.getByRole('mermaid')).toBeInTheDocument();
  });

  test('should validate chart content size', () => {
    const largeChart = 'graph TD\n' + 'A --> B\n'.repeat(10000);

    render(<Mermaid chart={largeChart} />);
    
    // Should show error for large content
    expect(screen.getByText(/Chart content too large/)).toBeInTheDocument();
  });

  test('should handle invalid syntax gracefully', () => {
    const invalidChart = 'not a valid mermaid syntax';

    render(<Mermaid chart={invalidChart} />);
    
    // Should show syntax error
    expect(screen.getByText(/Invalid Mermaid syntax/)).toBeInTheDocument();
  });

  test('should render safe content correctly', () => {
    const safeChart = `
      graph TD
        A[Start] --> B[Process]
        B --> C[End]
    `;

    render(<Mermaid chart={safeChart} />);
    
    // Should render without errors
    expect(screen.getByRole('mermaid')).toBeInTheDocument();
  });
});