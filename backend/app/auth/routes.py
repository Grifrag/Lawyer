import os
import bcrypt
from datetime import datetime, timedelta
from flask import request, jsonify
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
    base_url = os.environ.get("APP_BASE_URL", "http://localhost:5173")
    send_email(email, "Επαλήθευση email — Solon Checker",
               f"<p>Επαληθεύστε: <a href='{base_url}/verify-email?token={token}'>κλικ</a></p>")
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
