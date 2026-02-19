import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(subject, html_body):
    """Send an HTML email via Gmail SMTP.

    Args:
        subject: Email subject line
        html_body: Full HTML content of the email

    Raises:
        ValueError: If Gmail credentials are not configured
        smtplib.SMTPException: If email sending fails
    """
    if not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD == "your-16-char-app-password-here":
        raise ValueError(
            "Gmail App Password not configured. "
            "Set GMAIL_APP_PASSWORD in your .env file. "
            "See .env.example for instructions."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Daily Digest <{GMAIL_ADDRESS}>"
    msg["To"] = RECIPIENT_EMAIL

    # Attach HTML body
    msg.attach(MIMEText(html_body, "html"))

    logger.info(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

    logger.info(f"Email sent successfully to {RECIPIENT_EMAIL}")
