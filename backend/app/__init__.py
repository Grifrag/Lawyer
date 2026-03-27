import os
from flask import Flask
from app.extensions import db, jwt, migrate, limiter
from app.config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if config_name == "production":
        for var in ["DATABASE_URL", "JWT_SECRET_KEY", "FLASK_SECRET_KEY", "FERNET_KEY"]:
            if not os.environ.get(var):
                raise RuntimeError(f"Required env var {var!r} is not set")

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    from app.auth import bp as auth_bp
    from app.cases import bp as cases_bp
    from app.billing import bp as billing_bp
    from app.settings_bp import bp as settings_bp
    from app.checks import bp as checks_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(cases_bp, url_prefix="/api/cases")
    app.register_blueprint(billing_bp, url_prefix="/api/billing")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(checks_bp, url_prefix="/api/checks")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Add email_verified guard
    from flask import jsonify, request as flask_request
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

    UNGUARDED_PREFIXES = ["/api/auth/", "/api/billing/webhook"]

    @app.before_request
    def enforce_email_verified():
        path = flask_request.path
        if any(path.startswith(p) for p in UNGUARDED_PREFIXES):
            return
        if flask_request.method == "OPTIONS":
            return
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            return  # no valid token — let JWT handle the 401 downstream
        uid = get_jwt_identity()
        if uid:
            from app.models import User
            user = db.session.get(User, int(uid))
            if user and not user.email_verified:
                return jsonify({"error": "email_not_verified"}), 403

    # Seed admin on startup
    _seed_admin(app)

    return app

def _seed_admin(app):
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    with app.app_context():
        from app.models import User
        user = User.query.filter_by(email=admin_email).first()
        if user and not user.is_admin:
            user.is_admin = True
            db.session.commit()
