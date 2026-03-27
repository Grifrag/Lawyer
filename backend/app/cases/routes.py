# app/cases/routes.py  — placeholder
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.cases import bp

@bp.route("", methods=["GET"])
@jwt_required()
def list_cases():
    uid = get_jwt_identity()
    return jsonify([]), 200
