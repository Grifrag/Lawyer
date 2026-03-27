from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.cases import bp
from app.extensions import db
from app.models import Case, Result, User

def _active_user():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if not user or user.subscription_status not in ("active", "past_due"):
        return None, (jsonify({"error": "active subscription required"}), 403)
    return user, None

def _case_or_404(case_id, user_id):
    c = Case.query.filter_by(id=case_id, user_id=user_id).first()
    if not c:
        return None, (jsonify({"error": "not found"}), 404)
    return c, None

def _case_dict(c):
    latest = (Result.query
              .filter_by(case_id=c.id)
              .order_by(Result.checked_at.desc())
              .first())
    return {
        "id": c.id, "court": c.court, "search_type": c.search_type,
        "number": c.number, "year": c.year, "description": c.description,
        "active": c.active, "created_at": c.created_at.isoformat(),
        "last_checked_at": c.last_checked_at.isoformat() if c.last_checked_at else None,
        "consecutive_errors": c.consecutive_errors,
        "latest_result": {
            "decision_number": latest.decision_number,
            "result_text": latest.result_text,
            "checked_at": latest.checked_at.isoformat(),
            "decision_link": latest.decision_link,
        } if latest else None
    }

@bp.route("", methods=["GET"])
@jwt_required()
def list_cases():
    user, err = _active_user()
    if err: return err
    return jsonify([_case_dict(c) for c in user.cases]), 200

@bp.route("", methods=["POST"])
@jwt_required()
def add_case():
    user, err = _active_user()
    if err: return err
    data = request.get_json() or {}
    if data.get("search_type") not in ("GAK", "EAK"):
        return jsonify({"error": "search_type must be GAK or EAK"}), 400
    c = Case(user_id=user.id, court=data.get("court", ""),
             search_type=data["search_type"],
             number=str(data.get("number", "")),
             year=int(data.get("year", 0)),
             description=data.get("description"))
    db.session.add(c)
    db.session.commit()
    return jsonify(_case_dict(c)), 201

@bp.route("/<int:case_id>", methods=["PATCH"])
@jwt_required()
def patch_case(case_id):
    user, err = _active_user()
    if err: return err
    c, err = _case_or_404(case_id, user.id)
    if err: return err
    data = request.get_json() or {}
    for field in ("court", "search_type", "number", "description", "active"):
        if field in data:
            if field == "search_type" and data[field] not in ("GAK", "EAK"):
                return jsonify({"error": "invalid search_type"}), 400
            setattr(c, field, data[field])
    if "year" in data:
        c.year = int(data["year"])
    db.session.commit()
    return jsonify(_case_dict(c)), 200

@bp.route("/<int:case_id>", methods=["DELETE"])
@jwt_required()
def delete_case(case_id):
    user, err = _active_user()
    if err: return err
    c, err = _case_or_404(case_id, user.id)
    if err: return err
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200

@bp.route("/<int:case_id>/results", methods=["GET"])
@jwt_required()
def case_results(case_id):
    user, err = _active_user()
    if err: return err
    c, err = _case_or_404(case_id, user.id)
    if err: return err
    results = (Result.query.filter_by(case_id=c.id)
               .order_by(Result.checked_at.desc()).all())
    return jsonify([{
        "id": r.id, "checked_at": r.checked_at.isoformat(),
        "decision_number": r.decision_number, "decision_year": r.decision_year,
        "result_text": r.result_text, "decision_link": r.decision_link,
        "notified": r.notified
    } for r in results]), 200
