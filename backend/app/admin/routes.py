from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.admin import bp
from app.models import User, Case, Result
from app.extensions import db
from sqlalchemy import func
from datetime import date

def _admin_required():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if not user or not user.is_admin:
        return None, (jsonify({"error": "admin required"}), 403)
    return user, None

@bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    _, err = _admin_required()
    if err: return err
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        "id": u.id, "email": u.email, "name": u.name,
        "subscription_status": u.subscription_status,
        "case_count": len(u.cases),
        "created_at": u.created_at.isoformat(),
    } for u in users]), 200

@bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    _, err = _admin_required()
    if err: return err
    total = User.query.count()
    active = User.query.filter_by(subscription_status="active").count()
    today_checks = (Result.query
                    .filter(func.date(Result.checked_at) == date.today())
                    .count())
    today_errors = (Result.query
                    .filter(func.date(Result.checked_at) == date.today(),
                            Result.decision_number == None)
                    .count())
    return jsonify({
        "total_users": total,
        "active_subscriptions": active,
        "checks_today": today_checks,
        "errors_today": today_errors,
    }), 200
