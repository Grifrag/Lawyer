import os
import logging
import bcrypt
from datetime import datetime, timedelta
from flask import request, jsonify

logger = logging.getLogger(__name__)
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app.auth import bp
from app.auth.utils import generate_token, send_email
from app.extensions import db, limiter
from app.models import User

@bp.route("/register", methods=["POST"])
@limiter.limit("20/hour")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    token = generate_token()
    trial_end = datetime.utcnow() + timedelta(days=30)
    user = User(email=email, password_hash=pw_hash,
                name=data.get("name"), email_verify_token=token,
                subscription_status="trial", trial_ends_at=trial_end)
    db.session.add(user)
    db.session.commit()
    base_url = os.environ.get("APP_BASE_URL", "https://solonchecker.gr")
    verify_url = f"{base_url}/verify-email?token={token}"
    try:
      send_email(email, "Καλώς ήρθατε στο Solon Checker! Επαληθεύστε το email σας",
               f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a4fa0;">⚖️ Καλώς ήρθατε στο Solon Checker!</h2>
      <p>Σας ευχαριστούμε που επιλέξατε το Solon Checker για την παρακολούθηση
      των δικαστικών αποφάσεών σας.</p>
      <p>Έχετε <strong>30 μέρες δωρεάν</strong> για να δοκιμάσετε όλες τις δυνατότητες.</p>
      <p>Για να ξεκινήσετε, επαληθεύστε το email σας:</p>
      <a href="{verify_url}"
         style="background:#1a4fa0;color:white;padding:14px 28px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-size:16px;font-weight:bold;">
        ✅ Επαλήθευση Email
      </a>
      <p style="margin-top:24px;color:#555;">Τι μπορείτε να κάνετε:</p>
      <ul style="color:#555;">
        <li>🔍 Προσθέστε τις υποθέσεις σας</li>
        <li>📧 Λάβετε άμεση ειδοποίηση όταν βγει απόφαση</li>
        <li>⚖️ Αυτόματος έλεγχος καθημερινά</li>
      </ul>
      <p style="color:#888;font-size:12px;margin-top:32px;">
        Solon Checker · <a href="https://solonchecker.gr">solonchecker.gr</a><br>
        OptiGrid Technical Solutions
      </p>
    </div>
               """)
    except Exception as e:
        logger.error("Failed to send welcome email to %s: %s", email, e)
    return jsonify({"message": "registered"}), 201

@bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password", "")
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "invalid credentials"}), 401
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    resp = jsonify({"access_token": access_token,
                    "email_verified": user.email_verified,
                    "subscription_status": user.subscription_status,
                    "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None})
    resp.set_cookie("refresh_token", refresh_token,
                    httponly=True, secure=True, samesite="Strict",
                    max_age=2592000)
    return resp, 200

@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    uid = get_jwt_identity()
    access_token = create_access_token(identity=uid)
    return jsonify({"access_token": access_token}), 200

@bp.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"message": "logged out"})
    resp.delete_cookie("refresh_token")
    return resp, 200

@bp.route("/verify-email", methods=["POST"])
def verify_email():
    token = (request.get_json() or {}).get("token")
    if not token:
        return jsonify({"error": "token required"}), 400
    user = User.query.filter_by(email_verify_token=token).first()
    if not user:
        return jsonify({"error": "invalid token"}), 400
    user.email_verified = True
    user.email_verify_token = None
    db.session.commit()
    send_email(user.email, "Είστε έτοιμοι! — Solon Checker",
               f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a4fa0;">✅ Ο λογαριασμός σας είναι ενεργός!</h2>
      <p>Το email σας επαληθεύτηκε. Έχετε <strong>30 μέρες δωρεάν</strong>
      πρόσβαση σε όλες τις λειτουργίες.</p>
      <h3 style="color:#333;">Πώς να ξεκινήσετε:</h3>
      <ol style="color:#555;line-height:1.8;">
        <li>Συνδεθείτε στο <a href="https://solonchecker.gr">solonchecker.gr</a></li>
        <li>Κλικ <strong>"+ Νέα Υπόθεση"</strong></li>
        <li>Βάλτε το δικαστήριο, τον αριθμό και το έτος</li>
        <li>Αφήστε το Solon Checker να κάνει τη δουλειά!</li>
      </ol>
      <a href="https://solonchecker.gr/dashboard"
         style="background:#1a4fa0;color:white;padding:14px 28px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-size:16px;font-weight:bold;">
        🚀 Ξεκινήστε τώρα
      </a>
      <p style="margin-top:24px;color:#555;">
        Για οποιαδήποτε απορία, απαντήστε σε αυτό το email.
      </p>
      <p style="color:#888;font-size:12px;margin-top:32px;">
        Solon Checker · <a href="https://solonchecker.gr">solonchecker.gr</a><br>
        OptiGrid Technical Solutions
      </p>
    </div>
               """)
    return jsonify({"message": "email verified"}), 200

@bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5/hour")
def forgot_password():
    email = ((request.get_json() or {}).get("email") or "").lower().strip()
    user = User.query.filter_by(email=email).first()
    if user:
        token = generate_token()
        user.reset_password_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        base_url = os.environ.get("APP_BASE_URL", "http://localhost:5173")
        send_email(email, "Επαναφορά κωδικού — Solon Checker",
                   f"<p>Επαναφορά: <a href='{base_url}/reset-password?token={token}'>κλικ</a></p>")
    return jsonify({"message": "if email exists, reset link sent"}), 200

@bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "token required"}), 400
    password = data.get("password", "")
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400
    user = User.query.filter_by(reset_password_token=token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        return jsonify({"error": "invalid or expired token"}), 400
    user.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    user.reset_password_token = None
    user.reset_token_expires = None
    db.session.commit()
    return jsonify({"message": "password reset"}), 200
