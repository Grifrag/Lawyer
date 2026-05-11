import os
import secrets
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_token(n=32) -> str:
    return secrets.token_urlsafe(n)

def send_email(to: str, subject: str, html: str):
    host     = os.environ.get("SMTP_HOST", "")
    port     = int(os.environ.get("SMTP_PORT", "587"))
    user     = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")
    sender   = os.environ.get("MAIL_FROM", "noreply@solonchecker.gr")

    print(f"[EMAIL] host={host} user={user} pass={'SET' if password else 'MISSING'} to={to}", flush=True)
    if not host or not user or not password:
        print("[EMAIL] SKIPPED - missing config", flush=True)
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
        result = server.sendmail(sender, to, msg.as_string())
        print(f"[EMAIL] SENT OK to={to} result={result}", flush=True)
