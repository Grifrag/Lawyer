from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.settings_bp import bp
from app.extensions import db
from app.models import Setting
from crypto import encrypt, decrypt

SENSITIVE_KEYS = {"gmail_app_password", "telegram_bot_token"}

def _get_setting(user_id, key, default=None):
    s = Setting.query.filter_by(user_id=user_id, key=key).first()
    if not s:
        return default
    if key in SENSITIVE_KEYS:
        try:
            return decrypt(s.value)
        except Exception:
            return ""
    return s.value

def _set_setting(user_id, key, value):
    s = Setting.query.filter_by(user_id=user_id, key=key).first()
    stored = encrypt(value) if key in SENSITIVE_KEYS else value
    if s:
        s.value = stored
    else:
        db.session.add(Setting(user_id=user_id, key=key, value=stored))

@bp.route("", methods=["GET"])
@jwt_required()
def get_settings():
    uid = int(get_jwt_identity())
    keys = ["notification_type", "gmail_sender", "gmail_recipient",
            "telegram_chat_id"]
    result = {k: (_get_setting(uid, k) or "") for k in keys}
    return jsonify(result), 200

@bp.route("", methods=["POST"])
@jwt_required()
def save_settings():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    for key in ["notification_type", "gmail_sender", "gmail_recipient",
                "telegram_chat_id", "gmail_app_password", "telegram_bot_token"]:
        if key in data and data[key]:
            _set_setting(uid, key, data[key])
    db.session.commit()
    return jsonify({"message": "saved"}), 200

@bp.route("/test", methods=["POST"])
@jwt_required()
def test_notification():
    from notifier import send_notification
    uid = int(get_jwt_identity())
    config = {
        "notification_type": _get_setting(uid, "notification_type"),
        "gmail_sender": _get_setting(uid, "gmail_sender"),
        "gmail_app_password": _get_setting(uid, "gmail_app_password"),
        "gmail_recipient": _get_setting(uid, "gmail_recipient"),
        "telegram_bot_token": _get_setting(uid, "telegram_bot_token"),
        "telegram_chat_id": _get_setting(uid, "telegram_chat_id"),
    }
    test_result = {
        "court": "Πρωτοδικείο Αθηνών", "search_type": "GAK",
        "number": "0000", "year": 2024, "description": "Δοκιμαστική",
        "decision_number": "TEST-001", "decision_year": "2024",
        "result_text": "ΔΟΚΙΜΑΣΤΙΚΟ", "decision_link": "https://extapps.solon.gov.gr"
    }
    try:
        send_notification(**config, result=test_result)
        return jsonify({"message": "✅ Εστάλη επιτυχώς!"}), 200
    except Exception as e:
        return jsonify({"message": f"❌ Σφάλμα: {e}"}), 500
