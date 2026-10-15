"""Email service for Aivora YouTube Intelligence.
Dispatches email verification codes and password reset links.
Supports production SMTP as well as clean local development simulation.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@aivora.ai").strip()


def send_email(to_email: str, subject: str, html_content: str, text_content: str) -> bool:
    """Send an email using configured SMTP server, or log cleanly if not configured."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        # Local development / simulation mode
        print(f"\n[EMAIL SIMULATION] To: {to_email} | Subject: {subject}")
        print(f"[EMAIL BODY]: {text_content}\n", flush=True)
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR]: Failed to send email to {to_email}: {e}", flush=True)
        return False


def send_verification_email(to_email: str, full_name: str, code: str) -> bool:
    """Send 6-digit email verification code."""
    subject = f"{code} is your Aivora verification code"
    text = (
        f"Hello {full_name},\n\n"
        f"Welcome to Aivora YouTube Intelligence! Your verification code is:\n\n"
        f"  {code}\n\n"
        f"Enter this code to complete your registration and activate your account.\n"
        f"This code will expire in 24 hours.\n\n"
        f"The Aivora Team"
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #e2e8f0; padding: 30px; border-radius: 12px; max-width: 500px; margin: auto;">
        <h2 style="color: #818cf8; margin-top: 0;">Aivora YouTube Intelligence</h2>
        <p>Hello <strong>{full_name}</strong>,</p>
        <p>Thank you for joining Aivora. Here is your 6-digit account verification code:</p>
        <div style="background-color: #1a2236; border: 1px solid #313f63; padding: 18px; border-radius: 8px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #38bdf8; margin: 20px 0;">
            {code}
        </div>
        <p style="font-size: 13px; color: #94a3b8;">Enter this code into your browser to activate your creator workspace.</p>
        <hr style="border: 0; border-top: 1px solid #232d44; margin: 25px 0;">
        <p style="font-size: 11px; color: #64748b;">If you did not request this, please ignore this email.</p>
    </div>
    """
    return send_email(to_email, subject, html, text)


def send_reset_password_email(to_email: str, token: str) -> bool:
    """Send password reset link."""
    subject = "Reset your Aivora account password"
    text = (
        f"Hello,\n\n"
        f"A password reset was requested for your Aivora account.\n"
        f"Your reset code is:\n\n"
        f"  {token}\n\n"
        f"Use this token in the reset password modal to choose a new password.\n"
        f"This token expires in 1 hour.\n\n"
        f"The Aivora Team"
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #e2e8f0; padding: 30px; border-radius: 12px; max-width: 500px; margin: auto;">
        <h2 style="color: #818cf8; margin-top: 0;">Aivora Password Reset</h2>
        <p>A password reset was requested for your Aivora creator account.</p>
        <p>Your secure reset token is:</p>
        <div style="background-color: #1a2236; border: 1px solid #313f63; padding: 14px; border-radius: 8px; font-family: monospace; font-size: 16px; word-break: break-all; color: #38bdf8; margin: 20px 0;">
            {token}
        </div>
        <p style="font-size: 13px; color: #94a3b8;">Enter this token in the reset password dialog to set a new password. Valid for 1 hour.</p>
        <hr style="border: 0; border-top: 1px solid #232d44; margin: 25px 0;">
        <p style="font-size: 11px; color: #64748b;">If you did not make this request, you can safely ignore this email.</p>
    </div>
    """
    return send_email(to_email, subject, html, text)
