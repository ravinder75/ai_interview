"""
SMTP Email Service for sending verification OTPs, password reset codes, and security notices.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger("email_service")

import re

def validate_email_address(email: str) -> bool:
    """Validate email address format strictly supporting subdomains and TLDs."""
    if not email or not isinstance(email, str):
        return False
    regex = r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return bool(re.match(regex, email.strip()))

def normalize_email_address(email: str) -> str:
    """Normalize email address to lowercase and stripped."""
    return email.strip().lower() if email else ""

def detect_email_provider(email: str) -> dict:
    """
    Detect recipient domain and provider type.
    Does NOT affect backend email delivery — backend uses ONE unified transactional SMTP provider for all recipients.
    """
    normalized = normalize_email_address(email)
    if "@" not in normalized:
        return {"email": normalized, "domain": "", "provider": "unknown"}

    domain = normalized.split("@")[-1]

    if domain in ["gmail.com", "googlemail.com"]:
        provider = "google"
    elif domain in ["outlook.com", "hotmail.com", "live.com", "msn.com"]:
        provider = "microsoft"
    elif domain in ["yahoo.com", "ymail.com", "myyahoo.com"]:
        provider = "yahoo"
    elif domain in ["icloud.com", "me.com", "mac.com"]:
        provider = "apple"
    elif domain.endswith(".edu") or domain.endswith(".ac.in") or domain.endswith(".edu.in"):
        provider = "educational"
    else:
        provider = "custom"

    return {
        "email": normalized,
        "domain": domain,
        "provider": provider
    }


class EmailService:
    """Production Email Service class wrapper."""

    @staticmethod
    def validate_email(email: str) -> bool:
        return validate_email_address(email)

    @staticmethod
    def normalize_email(email: str) -> str:
        return normalize_email_address(email)

    @staticmethod
    def detect_provider(email: str) -> dict:
        return detect_email_provider(email)

    @staticmethod
    def send_verification_email(to_email: str, otp: str) -> bool:
        return send_email_verification_otp(to_email, otp)

    @staticmethod
    def send_password_reset_email(to_email: str, otp: str) -> bool:
        return send_password_reset_otp(to_email, otp)


def send_email(to_email: str, subject: str, body_html: str, body_text: str = "") -> bool:
    """Send an HTML/text email via Resend API or SMTP settings to ANY recipient domain."""
    if not validate_email_address(to_email):
        logger.error(f"Invalid recipient email address: {to_email}")
        return False

    to_email = normalize_email_address(to_email)
    provider_info = detect_email_provider(to_email)
    logger.info(f"Preparing email send to {to_email} (Detected recipient domain: {provider_info['domain']}, category: {provider_info['provider']})")

    smtp_host = getattr(settings, "SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(getattr(settings, "SMTP_PORT", 587))
    smtp_user = getattr(settings, "SMTP_USERNAME", "")
    smtp_pass = getattr(settings, "SMTP_PASSWORD", "")
    mail_from = getattr(settings, "SMTP_FROM_EMAIL", getattr(settings, "MAIL_FROM", "ravinderkama14@gmail.com"))
    from_name = getattr(settings, "SMTP_FROM_NAME", "Interview Coach AI")
    resend_key = getattr(settings, "RESEND_API_KEY", getattr(settings, "EMAIL_API_KEY", ""))

    # Try Resend API if configured
    if resend_key:
        try:
            import httpx
            headers = {"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"}
            payload = {
                "from": f"{from_name} <{mail_from}>",
                "to": [to_email],
                "subject": subject,
                "html": body_html,
                "text": body_text
            }
            res = httpx.post("https://api.resend.com/emails", json=payload, headers=headers, timeout=10.0)
            if res.status_code in [200, 201]:
                logger.info(f"Resend email sent successfully to {to_email}, res={res.json()}")
                return True
            else:
                logger.error(f"Resend API error: {res.status_code} - {res.text}")
        except Exception as err:
            logger.error(f"Resend API call exception: {err}")

    if not resend_key and (not smtp_user or not smtp_pass):
        logger.error("Email delivery configuration missing. Please configure SMTP_PASSWORD or EMAIL_API_KEY in backend/.env")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{mail_from}>"
        msg["To"] = to_email

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=12.0) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(mail_from, [to_email], msg.as_string())
        logger.info(f"Email successfully sent via SMTP to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_email_verification_otp(to_email: str, otp: str) -> bool:
    subject = "Verify your email address - Interview Coach AI"
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; background-color: #0f172a; border-radius: 10px;">
        <h2 style="color: #6366f1;">Interview Coach AI</h2>
        <p style="color: #e2e8f0;">Your email verification code is:</p>
        <div style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #38bdf8; padding: 15px 0;">{otp}</div>
        <p style="color: #94a3b8; font-size: 14px;">This code will expire in 10 minutes. If you did not create an account, please ignore this email.</p>
    </div>
    """
    text = f"Your Interview Coach AI verification code is: {otp}. It expires in 10 minutes."
    return send_email(to_email, subject, html, text)

def send_password_reset_otp(to_email: str, otp: str) -> bool:
    subject = "Interview Coach AI - Password Reset OTP"
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; background-color: #0f172a; border-radius: 10px;">
        <h2 style="color: #6366f1;">Interview Coach AI</h2>
        <p style="color: #e2e8f0;">Hello,</p>
        <p style="color: #cbd5e1;">We received a request to reset your Interview Coach AI password.</p>
        <p style="color: #e2e8f0;">Your verification code is:</p>
        <div style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #f43f5e; padding: 15px 0;">{otp}</div>
        <p style="color: #94a3b8; font-size: 14px;">This code expires in 10 minutes.</p>
        <p style="color: #94a3b8; font-size: 14px;">If you did not request this password reset, you can safely ignore this email.</p>
        <br/>
        <p style="color: #cbd5e1;">Regards,<br/>Interview Coach AI Team</p>
    </div>
    """
    text = f"Hello,\n\nWe received a request to reset your Interview Coach AI password.\n\nYour verification code is:\n\n{otp}\n\nThis code expires in 10 minutes.\n\nIf you did not request this password reset, you can safely ignore this email.\n\nRegards,\nInterview Coach AI Team"
    return send_email(to_email, subject, html, text)
