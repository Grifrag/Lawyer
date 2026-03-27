import smtplib
import ssl
import logging
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def _build_html_email(result):
    return f"""
    <html><body>
    <h2>📋 Νέα Απόφαση Δικαστηρίου</h2>
    <table border="1" cellpadding="8" style="border-collapse:collapse;">
      <tr><td><b>Δικαστήριο</b></td><td>{result['court']}</td></tr>
      <tr><td><b>Αριθμός {result['search_type']}</b></td>
          <td>{result['number']}/{result['year']}</td></tr>
      <tr><td><b>Υπόθεση</b></td><td>{result.get('description','')}</td></tr>
      <tr><td><b>Αριθμός Απόφασης</b></td>
          <td>{result['decision_number']}/{result['decision_year']}</td></tr>
      <tr><td><b>Αποτέλεσμα</b></td><td>{result.get('result_text','')}</td></tr>
    </table>
    <br>
    <a href="{result['decision_link']}"
       style="background:#1a73e8;color:white;padding:10px 20px;
              text-decoration:none;border-radius:4px;">
      Άνοιγμα στο Solon
    </a>
    </body></html>
    """


def send_gmail(sender, app_password, recipient, result):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"Απόφαση: {result['court']} - "
        f"{result['search_type']} {result['number']}/{result['year']}"
    )
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(_build_html_email(result), "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())
    logger.info("Gmail notification sent for case %s", result['number'])


def send_telegram(bot_token, chat_id, result):
    text = (
        f"📋 *Νέα Απόφαση Δικαστηρίου*\n\n"
        f"🏛 *Δικαστήριο:* {result['court']}\n"
        f"📁 *{result['search_type']}:* {result['number']}/{result['year']}\n"
        f"📝 *Υπόθεση:* {result.get('description','')}\n"
        f"⚖️ *Απόφαση:* {result['decision_number']}/{result['decision_year']}\n"
        f"✅ *Αποτέλεσμα:* {result.get('result_text','')}\n\n"
        f"[Άνοιγμα στο Solon]({result['decision_link']})"
    )
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )
    response.raise_for_status()
    logger.info("Telegram notification sent for case %s", result['number'])


def send_notification(notification_type, gmail_sender, gmail_app_password,
                      gmail_recipient, telegram_bot_token, telegram_chat_id, result):
    if not notification_type:
        logger.warning("No notification type configured — skipping notification.")
        return

    if notification_type in ("gmail", "both") and gmail_sender:
        try:
            send_gmail(
                sender=gmail_sender,
                app_password=gmail_app_password,
                recipient=gmail_recipient,
                result=result,
            )
        except Exception as e:
            logger.error("Gmail send failed: %s", e)

    if notification_type in ("telegram", "both") and telegram_bot_token:
        try:
            send_telegram(
                bot_token=telegram_bot_token,
                chat_id=telegram_chat_id,
                result=result,
            )
        except Exception as e:
            logger.error("Telegram send failed: %s", e)
