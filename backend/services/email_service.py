"""
Email Service for ArchIntel Backend

This module provides:
- SMTP email sending functionality
- 2FA code generation and sending
- Email template management
- Secure email handling

Author: ArchIntel Security Team
Requirements: Email-based authentication
"""

import os
import smtplib
import random
import string
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jinja2 import Template

# Configure logging
email_logger = logging.getLogger("archintel.email")
email_logger.setLevel(logging.INFO)

if not email_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - EMAIL - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    email_logger.addHandler(handler)


class EmailConfig:
    """Email configuration from environment variables"""

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@archintel.com")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "ArchIntel")

    TWO_FA_CODE_LENGTH = int(os.getenv("2FA_CODE_LENGTH", "6"))
    TWO_FA_CODE_EXPIRE_MINUTES = int(os.getenv("2FA_CODE_EXPIRE_MINUTES", "10"))

    @classmethod
    def is_configured(cls) -> bool:
        """Check if SMTP is properly configured"""
        return bool(cls.SMTP_USER and cls.SMTP_PASSWORD)


class EmailService:
    """Email service with SMTP support"""

    def __init__(self):
        pass

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email using SMTP

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not EmailConfig.is_configured():
            email_logger.error("SMTP not configured. Cannot send email.")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{EmailConfig.SMTP_FROM_NAME} <{EmailConfig.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Connect to SMTP server and send
            with smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()

            email_logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            email_logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


class TwoFactorAuthService:
    """2FA code generation and email sending service"""

    def __init__(self, email_service: EmailService):
        self.email_service = email_service
        self.codes_store = {}  # email: (code, expiry_time)

    def generate_code(self) -> str:
        """Generate a random 2FA code"""
        return ''.join(random.choices(string.digits, k=EmailConfig.TWO_FA_CODE_LENGTH))

    def store_code(self, email: str, code: str) -> datetime:
        """Store code with expiry time"""
        expiry = datetime.utcnow() + timedelta(minutes=EmailConfig.TWO_FA_CODE_EXPIRE_MINUTES)
        self.codes_store[email] = (code, expiry)
        return expiry

    def verify_code(self, email: str, code: str) -> bool:
        """
        Verify 2FA code

        Args:
            email: User email
            code: Code to verify

        Returns:
            True if valid, False otherwise
        """
        if email not in self.codes_store:
            return False

        stored_code, expiry = self.codes_store[email]

        # Check if code has expired
        if datetime.utcnow() > expiry:
            del self.codes_store[email]
            return False

        # Verify code
        if stored_code == code:
            del self.codes_store[email]
            return True

        return False

    def send_2fa_email(self, email: str) -> Optional[datetime]:
        """
        Generate and send 2FA code via email

        Args:
            email: User email address

        Returns:
            Code expiry time if sent, None otherwise
        """
        # Check if email is configured first
        if not EmailConfig.is_configured():
            email_logger.error("SMTP not configured. Cannot send email.")
            return None

        code = self.generate_code()

        subject = "Your ArchIntel Verification Code"

        # HTML email template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verification Code</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background-color: #0A0C10;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: #0d1117;
                    border-radius: 12px;
                    padding: 40px;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                .logo {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    background: linear-gradient(135deg, #8B5CF6, #06B6D4);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .code-box {
                    background: linear-gradient(135deg, #8B5CF6, #06B6D4);
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 30px 0;
                }
                .code {
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    font-family: monospace;
                }
                .info {
                    color: #888;
                    font-size: 14px;
                    line-height: 1.6;
                }
                .warning {
                    color: #EF4444;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">ArchIntel</div>
                <h2>Verification Code</h2>
                <p>Use the following code to complete your sign-in:</p>

                <div class="code-box">
                    <div class="code">{{ code }}</div>
                </div>

                <div class="info">
                    <p>This code will expire in {{ minutes }} minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </div>

                <div class="warning">
                    <p>For your security, never share this code with anyone.</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(
            code=code,
            minutes=EmailConfig.TWO_FA_CODE_EXPIRE_MINUTES
        )

        # Text version
        text_content = f"""
        ArchIntel - Verification Code

        Your verification code is: {code}

        This code will expire in {EmailConfig.TWO_FA_CODE_EXPIRE_MINUTES} minutes.

        If you didn't request this code, please ignore this email.

        For your security, never share this code with anyone.
        """

        # Try to send email first
        if not self.email_service.send_email(email, subject, html_content, text_content):
            email_logger.error(f"Failed to send 2FA code to {email}")
            return None

        # Only store code after successful send
        expiry = self.store_code(email, code)
        email_logger.info(f"2FA code sent to {email}")
        return expiry


# Global instances
email_service = EmailService()
two_factor_service = TwoFactorAuthService(email_service)