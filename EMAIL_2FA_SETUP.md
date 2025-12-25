# Email Authentication with 2FA Setup Guide

This guide explains how to set up email-based authentication with Two-Factor Authentication (2FA) for ArchIntel.

## Environment Variables

### Backend (.env)

Add the following SMTP configuration to your `backend/.env` file:

```bash
# SMTP Configuration for Email Authentication
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@archintel.com
SMTP_FROM_NAME=ArchIntel

# 2FA Configuration
2FA_CODE_EXPIRE_MINUTES=10
2FA_CODE_LENGTH=6
```

### Frontend (.env)

Update your `frontend/.env` file with:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Setting Up Gmail SMTP

If you want to use Gmail for sending emails:

1. **Enable 2FA on your Google Account**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate an App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password (this is your `SMTP_PASSWORD`)

3. **Update environment variables**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Your app password
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

## Alternative SMTP Providers

### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### Mailgun
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.com
SMTP_PASSWORD=your-mailgun-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### AWS SES
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### Outlook/Hotmail
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-outlook-password
SMTP_FROM_EMAIL=your-email@outlook.com
```

## How It Works

### 1. User Signup
- User enters email and password
- Account is created in Supabase
- 6-digit verification code is sent to their email
- User is redirected to verification page

### 2. User Login
- User enters email and password
- Credentials are verified with Supabase
- 6-digit verification code is sent to their email
- User is redirected to verification page

### 3. 2FA Verification
- User enters the 6-digit code
- Code is verified (expires in 10 minutes)
- User receives authentication tokens
- Redirected to projects dashboard

### 4. Code Resend
- User can request a new code
- Previous code is invalidated
- 10-minute timer resets

## API Endpoints

### POST `/auth/signup`
Create a new account

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### POST `/auth/login`
Login with credentials

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### POST `/auth/verify-2fa`
Verify 2FA code

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

### POST `/auth/resend-2fa`
Resend verification code

```json
{
  "email": "user@example.com"
}
```

## Security Features

1. **Rate Limiting**: Prevents brute force attacks
2. **Code Expiration**: Codes expire in 10 minutes
3. **Code Invalidation**: Old codes are invalidated when new ones are generated
4. **Secure Storage**: Codes are stored in memory (not database)
5. **CSRF Protection**: Token-based CSRF protection
6. **Secure Headers**: Additional security headers on responses

## Email Template

The verification email includes:
- 6-digit verification code (large, easy to read)
- Expiration time
- Security warning about not sharing the code
- ArchIntel branding

## Troubleshooting

### Emails not sending
- Check SMTP credentials are correct
- Verify SMTP host and port
- Check if your email provider allows app passwords
- Review backend logs for errors

### 2FA codes not working
- Ensure code is entered correctly (6 digits)
- Check if code has expired (10 minutes)
- Try resending the code

### Login fails after 2FA verification
- The implementation currently returns success and redirects to login
- In production, you would want to store the user session between login and 2FA verification
- Consider using Redis or a temporary session store

## Production Considerations

1. **Session Management**: Implement proper session storage between login and 2FA verification
2. **Email Queueing**: Use a task queue (like Celery or arq) for sending emails
3. **Rate Limiting**: Configure stricter rate limits for production
4. **Monitoring**: Add monitoring for failed login attempts
5. **Backup SMTP**: Configure a backup SMTP provider for reliability

## Next Steps

1. Set up your SMTP provider
2. Add environment variables to your `.env` files
3. Test signup and login flows
4. Configure rate limits for production
5. Set up email monitoring
6. Consider adding additional security features (login alerts, device management, etc.)