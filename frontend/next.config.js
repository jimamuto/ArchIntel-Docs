/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8001/:path*',
      },
    ];
  },

  // Security headers including CSP
  async headers() {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';

    // Build connect-src dynamically to include backend API and localhost
    const connectSrc = [
      "'self'",
      'https://*.supabase.co',
      'https://api.github.com',
      'https://github.com',
      'ws://*.supabase.co',
      'wss://*.supabase.co',
      'http://localhost:8000',
      'http://localhost:8000/*',
      'http://localhost:8001',
      'http://localhost:8001/*',
      'http://127.0.0.1:8000',
      'http://127.0.0.1:8000/*'
    ].join(' ');

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
              "img-src 'self' data: blob: https://http:", // Allow data URIs and external images
              "font-src 'self'",
              `connect-src ${connectSrc}`, // Allow Supabase, GitHub, and backend API
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
