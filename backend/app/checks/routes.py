import os
import redis as redis_lib
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.checks import bp
from app.extensions import limiter

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Module-level placeholder so tests can patch app.checks.routes.run_check_for_user
run_check_for_user = None

def _redis():
    return redis_lib.from_url(REDIS_URL)

@bp.route("/run-now", methods=["POST"])
@jwt_required()
@limiter.limit("3/hour")
def run_now():
    global run_check_for_user
    uid = int(get_jwt_identity())
    r = _redis()
    if r.exists("check_all_lock"):
        return jsonify({"status": "scheduled_check_running",
                        "message": "Έλεγχος σε εξέλιξη, δοκιμάστε σε λίγα λεπτά"}), 200
    if r.exists(f"check_lock:user:{uid}"):
        return jsonify({"status": "already_running"}), 200
    if run_check_for_user is None:
        from celery_app import run_check_for_user as _task
        run_check_for_user = _task
    run_check_for_user.apply_async(args=[uid], queue="short")
    return jsonify({"status": "started"}), 200

@bp.route("/status", methods=["GET"])
@jwt_required()
def check_status():
    uid = int(get_jwt_identity())
    r = _redis()
    running = bool(r.exists(f"check_lock:user:{uid}") or r.exists("check_all_lock"))
    return jsonify({"running": running}), 200
