import os
import secrets
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_token(n=32) -> str:
    return secrets.token_urlsafe(n)

def send_email(to: str, subject: str, html: str):
    sender = os.environ.get("MAIL_SENDER", "noreply@example.com")
    password = os.environ.get("MAIL_APP_PASSWORD", "")
    if not password:
        return  # skip in test/dev
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender, password)
        server.sendmail(sender, to, msg.as_string())
