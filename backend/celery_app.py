import os
import sys
sys.path.insert(0, '/app')
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "solon_saas",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_app"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="Europe/Athens",
    enable_utc=True,
    task_routes={
        "celery_app.check_all_active_cases": {"queue": "default"},
        "celery_app.run_check_for_user": {"queue": "short"},
    },
    beat_schedule={
        "morning-check": {
            "task": "celery_app.check_all_active_cases",
            "schedule": crontab(hour=7, minute=0),
        },
        "midday-check": {
            "task": "celery_app.check_all_active_cases",
            "schedule": crontab(hour=12, minute=0),
        },
        "afternoon-check": {
            "task": "celery_app.check_all_active_cases",
            "schedule": crontab(hour=17, minute=0),
        },
        "trial-reminders": {
            "task": "celery_app.send_trial_reminders",
            "schedule": crontab(hour=10, minute=0),  # κάθε μέρα 10:00
        },
        "expire-accounts": {
            "task": "celery_app.expire_accounts",
            "schedule": crontab(hour=10, minute=30),  # κάθε μέρα 10:30
        },
    },
)


def _get_app():
    from app import create_app
    return create_app("production")


def _get_notification_config_for_user(uid, db_session):
    from app.models import Setting
    from crypto import decrypt

    SENSITIVE = {"gmail_app_password", "telegram_bot_token"}

    def _get(key):
        s = db_session.query(Setting).filter_by(user_id=uid, key=key).first()
        if not s:
            return None
        if key in SENSITIVE:
            try:
                return decrypt(s.value)
            except Exception:
                return None
        return s.value

    return {
        "notification_type": _get("notification_type"),
        "gmail_sender": _get("gmail_sender"),
        "gmail_app_password": _get("gmail_app_password"),
        "gmail_recipient": _get("gmail_recipient"),
        "telegram_bot_token": _get("telegram_bot_token"),
        "telegram_chat_id": _get("telegram_chat_id"),
    }


def _send_decision_email(to_email, result, send_email_fn):
    """Send a decision notification email to the user's registered email."""
    subject = (
        f"⚖️ Νέα Απόφαση: {result['court']} — "
        f"{result['search_type']} {result['number']}/{result['year']}"
    )
    desc = result.get('description', '')
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a4fa0;">⚖️ Βρέθηκε Νέα Απόφαση</h2>
      <table style="border-collapse:collapse;width:100%;">
        <tr><td style="padding:8px;border:1px solid #ddd;background:#f5f5f5;"><b>Δικαστήριο</b></td>
            <td style="padding:8px;border:1px solid #ddd;">{result['court']}</td></tr>
        <tr><td style="padding:8px;border:1px solid #ddd;background:#f5f5f5;"><b>Αριθμός {result['search_type']}</b></td>
            <td style="padding:8px;border:1px solid #ddd;">{result['number']}/{result['year']}</td></tr>
        {'<tr><td style="padding:8px;border:1px solid #ddd;background:#f5f5f5;"><b>Περιγραφή</b></td><td style="padding:8px;border:1px solid #ddd;">' + desc + '</td></tr>' if desc else ''}
        <tr><td style="padding:8px;border:1px solid #ddd;background:#f5f5f5;"><b>Αριθμός Απόφασης</b></td>
            <td style="padding:8px;border:1px solid #ddd;"><b>{result['decision_number']}/{result['decision_year']}</b></td></tr>
        <tr><td style="padding:8px;border:1px solid #ddd;background:#f5f5f5;"><b>Αποτέλεσμα</b></td>
            <td style="padding:8px;border:1px solid #ddd;">{result.get('result_text','')}</td></tr>
      </table>
      <br>
      <a href="{result['decision_link']}"
         style="background:#1a4fa0;color:white;padding:12px 24px;
                text-decoration:none;border-radius:4px;display:inline-block;">
        Άνοιγμα στο Solon
      </a>
      <p style="color:#888;font-size:12px;margin-top:24px;">
        Solon Checker · <a href="https://solonchecker.gr">solonchecker.gr</a>
      </p>
    </div>
    """
    try:
        send_email_fn(to_email, subject, html)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Failed to send decision email to %s: %s", to_email, e)


def _run_cases(cases, db_session):
    """Core check loop: single browser, all cases."""
    import logging
    import time
    from datetime import datetime, timedelta
    from app.models import Result, User
    from notifier import send_notification
    from app.auth.utils import send_email
    logger = logging.getLogger(__name__)
    admin_email = os.environ.get("ADMIN_EMAIL", "")

    from checker import _scrape_case
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
    BLOCKED = {"image", "media"}  # Do NOT block font/stylesheet — ADF needs CSS to render form elements

    total_cases = len(cases)
    total_errors = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.route("**/*", lambda r: r.abort()
                   if r.request.resource_type in BLOCKED else r.continue_())

        for case in cases:
            # Smart frequency: skip old cases checked recently, except Mon/Wed/Fri
            if case.last_checked_at:
                recent_check = case.last_checked_at > datetime.utcnow() - timedelta(days=3)
                age = (datetime.utcnow() - case.created_at).days
                if age > 365 and recent_check:
                    weekday = datetime.utcnow().weekday()
                    if weekday not in (0, 2, 4):  # Mon=0, Wed=2, Fri=4
                        continue

            config = _get_notification_config_for_user(case.user_id, db_session)
            result = None
            scrape_error = None

            # Retry up to 3 times on TimeoutError; abort immediately on other exceptions
            for attempt in range(3):
                try:
                    result = _scrape_case(case.__dict__, page)
                    break
                except PWTimeoutError as e:
                    if attempt < 2:
                        time.sleep(10)
                    else:
                        scrape_error = f"TimeoutError after 3 attempts: {e}"
                except Exception as e:
                    scrape_error = f"Unexpected error: {e}"
                    logger.exception("Unexpected error scraping case %s", case.id)
                    break

            case.last_checked_at = datetime.utcnow()

            if scrape_error:
                r = Result(case_id=case.id, result_text=f"ERROR: {scrape_error}")
                db_session.add(r)
                case.consecutive_errors += 1
                # Send warning email exactly once when threshold is first reached
                if case.consecutive_errors == 3:
                    user = db_session.get(User, case.user_id)
                    if user:
                        send_email(
                            user.email,
                            "Solon Checker — Προειδοποίηση επαναλαμβανόμενων σφαλμάτων",
                            f"<p>Η υπόθεση {case.number}/{case.year} ({case.court}) "
                            f"αντιμετωπίζει 3 συνεχόμενα σφάλματα ελέγχου. "
                            f"Παρακαλώ ελέγξτε τη σύνδεσή σας.</p>"
                        )
                total_errors += 1
            elif result:
                # Try insert; skip if duplicate (UNIQUE constraint)
                from sqlalchemy.exc import IntegrityError
                try:
                    nested = db_session.begin_nested()
                    r = Result(
                        case_id=case.id,
                        decision_number=result["decision_number"],
                        decision_year=result["decision_year"],
                        result_text=result["result_text"],
                        decision_link=result["decision_link"],
                    )
                    db_session.add(r)
                    db_session.flush()
                    case.consecutive_errors = 0
                    full_result = {**result, "court": case.court,
                                   "search_type": case.search_type,
                                   "number": case.number, "year": case.year,
                                   "description": case.description or ""}
                    # Send email to user's registered email via SES
                    user = db_session.get(User, case.user_id)
                    if user:
                        _send_decision_email(user.email, full_result, send_email)
                    # Also send via user-configured channel (Telegram etc.) if set
                    send_notification(**config, result=full_result)
                    r.notified = True
                    nested.commit()
                except IntegrityError:
                    nested.rollback()
                    logger.info("Duplicate result for case %s — skip", case.id)
            else:
                # No decision found — save a pending record so dashboard shows "Εκκρεμεί"
                r = Result(case_id=case.id, result_text="Εκκρεμεί")
                db_session.add(r)
                case.consecutive_errors = 0

            db_session.commit()
            time.sleep(2)  # Pause between cases to avoid rate-limiting from solon.gov.gr

        browser.close()

    # Alert admin if solon.gov.gr appears unreachable (all cases failed)
    if total_cases > 0 and total_errors == total_cases and admin_email:
        send_email(
            admin_email,
            "Solon Checker — Αποτυχία ΟΛΩΝ των ελέγχων",
            f"<p>Όλοι οι έλεγχοι ({total_cases}/{total_cases}) απέτυχαν. "
            f"Πιθανόν το solon.gov.gr να μην είναι διαθέσιμο.</p>"
        )


@celery.task(name="celery_app.check_all_active_cases")
def check_all_active_cases():
    import redis as redis_lib
    import logging
    logger = logging.getLogger(__name__)
    r = redis_lib.from_url(REDIS_URL)
    if not r.set("check_all_lock", "1", nx=True, ex=3600):
        logger.warning("check_all_active_cases already running — skip")
        return
    try:
        flask_app = _get_app()
        with flask_app.app_context():
            from app.extensions import db
            from app.models import Case, User
            cases = (db.session.query(Case)
                     .join(User)
                     .filter(Case.active == True,
                             User.subscription_status == "active")
                     .all())
            logger.info("Checking %d cases", len(cases))
            _run_cases(cases, db.session)
    finally:
        r.delete("check_all_lock")


@celery.task(name="celery_app.run_check_for_user")
def run_check_for_user(user_id: int):
    import redis as redis_lib
    r = redis_lib.from_url(REDIS_URL)
    # Don't run if the global scheduled check is already processing cases
    if r.exists("check_all_lock"):
        return
    lock_key = f"check_lock:user:{user_id}"
    if not r.set(lock_key, "1", nx=True, ex=1800):
        return
    try:
        flask_app = _get_app()
        with flask_app.app_context():
            from app.extensions import db
            from app.models import Case
            cases = db.session.query(Case).filter_by(
                user_id=user_id, active=True).all()
            _run_cases(cases, db.session)
    finally:
        r.delete(lock_key)


@celery.task(name="celery_app.send_trial_reminders")
def send_trial_reminders():
    """Στέλνει reminder emails σε users που το trial λήγει σε 7 ή 1 μέρα."""
    from datetime import datetime, timedelta
    flask_app = _get_app()
    with flask_app.app_context():
        from app.extensions import db
        from app.models import User
        from app.auth.utils import send_email

        now = datetime.utcnow()

        for days_left, subject, body in [
            (7,
             "⏰ Απομένουν 7 μέρες στο δωρεάν trial σας — Solon Checker",
             """
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a4fa0;">⏰ Το trial σας λήγει σε 7 μέρες</h2>
      <p>Σας υπενθυμίζουμε ότι η δωρεάν δοκιμαστική περίοδος σας στο
      <strong>Solon Checker</strong> λήγει σε <strong>7 μέρες</strong>.</p>
      <p>Για να συνεχίσετε να λαμβάνετε ειδοποιήσεις για τις δικαστικές
      αποφάσεις σας, ενεργοποιήστε τη συνδρομή σας.</p>
      <a href="https://solonchecker.gr/billing"
         style="background:#1a4fa0;color:white;padding:14px 28px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-size:16px;font-weight:bold;">
        💳 Ενεργοποίηση Συνδρομής — €4.99/μήνα
      </a>
      <p style="margin-top:20px;color:#555;">
        Μόνο <strong>€4.99/μήνα</strong> · Ακύρωση οποιαδήποτε στιγμή.
      </p>
      <p style="color:#888;font-size:12px;margin-top:32px;">
        Solon Checker · <a href="https://solonchecker.gr">solonchecker.gr</a>
      </p>
    </div>
             """),
            (1,
             "🚨 Αύριο λήγει το trial σας — Solon Checker",
             """
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#c0392b;">🚨 Το trial σας λήγει αύριο!</h2>
      <p>Η δωρεάν δοκιμαστική περίοδος σας στο <strong>Solon Checker</strong>
      λήγει <strong>αύριο</strong>.</p>
      <p>Μην χάσετε τις ειδοποιήσεις για τις δικαστικές αποφάσεις σας.
      Ενεργοποιήστε τη συνδρομή σας σήμερα:</p>
      <a href="https://solonchecker.gr/billing"
         style="background:#c0392b;color:white;padding:14px 28px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-size:16px;font-weight:bold;">
        💳 Ενεργοποίηση Συνδρομής — €4.99/μήνα
      </a>
      <p style="margin-top:20px;color:#555;">
        Μόνο <strong>€4.99/μήνα</strong> · Ακύρωση οποιαδήποτε στιγμή.
      </p>
      <p style="color:#888;font-size:12px;margin-top:32px;">
        Solon Checker · <a href="https://solonchecker.gr">solonchecker.gr</a>
      </p>
    </div>
             """),
        ]:
            target_date = now + timedelta(days=days_left)
            users = db.session.query(User).filter(
                User.subscription_status == "trial",
                User.trial_ends_at >= target_date.replace(hour=0, minute=0, second=0),
                User.trial_ends_at < target_date.replace(hour=23, minute=59, second=59),
            ).all()

            for user in users:
                try:
                    send_email(user.email, subject, body)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(
                        "Failed trial reminder to %s: %s", user.email, e
                    )


@celery.task(name="celery_app.expire_accounts")
def expire_accounts():
    """Κόβει access σε trial users που πέρασαν το 2-ήμερο grace period."""
    from datetime import datetime, timedelta
    import logging
    logger = logging.getLogger(__name__)
    flask_app = _get_app()
    with flask_app.app_context():
        from app.extensions import db
        from app.models import User
        from app.auth.utils import send_email

        now = datetime.utcnow()
        grace_deadline = now - timedelta(days=2)

        # Users whose trial + 2 days grace έχει περάσει
        expired_users = db.session.query(User).filter(
            User.subscription_status == "trial",
            User.trial_ends_at < grace_deadline,
        ).all()

        for user in expired_users:
            user.subscription_status = "cancelled"
            db.session.commit()
            logger.info("Expired account for user %s", user.email)
            try:
                send_email(
                    user.email,
                    "Ο λογαριασμός σας απενεργοποιήθηκε — Solon Checker",
                    f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#c0392b;">❌ Ο λογαριασμός σας απενεργοποιήθηκε</h2>
      <p>Η δωρεάν δοκιμαστική περίοδος σας έληξε και ο λογαριασμός σας
      στο <strong>Solon Checker</strong> έχει απενεργοποιηθεί.</p>
      <p>Για να επαναφέρετε την πρόσβασή σας και να συνεχίσετε να
      παρακολουθείτε τις υποθέσεις σας, ενεργοποιήστε τη συνδρομή σας:</p>
      <a href="https://solonchecker.gr/billing"
         style="background:#1a4fa0;color:white;padding:14px 28px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-size:16px;font-weight:bold;">
        💳 Ενεργοποίηση Συνδρομής — €4.99/μήνα
      </a>
      <p style="margin-top:20px;color:#555;">
        Τα δεδομένα σας (υποθέσεις κλπ) <strong>διατηρούνται</strong> —
        μόλις ενεργοποιήσετε συνδρομή, όλα επαναφέρονται κανονικά.
      </p>
      <p style="color:#888;font-size:12px;margin-top:32px;">
        Solon Checker · <a href="https://solonchecker.gr">solonchecker.gr</a>
      </p>
    </div>
                    """
                )
            except Exception as e:
                logger.error("Failed expiry email to %s: %s", user.email, e)
