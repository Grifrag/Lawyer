import os
import secrets
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_token(n=32) -> str:
    return secrets.token_urlsafe(n)

def send_email(to: str, subject: str, html: str):
    sender  = os.environ.get("MAIL_SENDER", "")
    password = os.environ.get("MAIL_APP_PASSWORD", "")
    host    = os.environ.get("SMTP_HOST", "smtp-relay.brevo.com")
    port    = int(os.environ.get("SMTP_PORT", "587"))
    user    = os.environ.get("SMTP_USER", sender)   # Brevo uses login email as user

    if not password or not sender:
        return  # email not configured, skip silently

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Solon Checker <{sender}>"
    msg["To"]      = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(user, password)
        server.sendmail(sender, to, msg.as_string())
