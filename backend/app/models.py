from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    phone = db.Column(db.Text)
    afm = db.Column(db.Text)
    wants_invoice = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.Text)
    stripe_subscription_id = db.Column(db.Text)
    subscription_status = db.Column(db.Text, default="inactive")
    email_verified = db.Column(db.Boolean, default=False)
    email_verify_token = db.Column(db.Text)
    reset_password_token = db.Column(db.Text)
    reset_token_expires = db.Column(db.DateTime)
    trial_ends_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cases = db.relationship("Case", backref="user", lazy=True, cascade="all, delete-orphan")
    settings = db.relationship("Setting", backref="user", lazy=True, cascade="all, delete-orphan")

class Case(db.Model):
    __tablename__ = "cases"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    court = db.Column(db.Text, nullable=False)
    search_type = db.Column(db.Text, nullable=False)  # GAK | EAK
    number = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    consecutive_errors = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked_at = db.Column(db.DateTime)
    results = db.relationship("Result", backref="case", lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint("search_type IN ('GAK', 'EAK')", name="ck_search_type"),
    )

class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    decision_number = db.Column(db.Text)
    decision_year = db.Column(db.Text)
    result_text = db.Column(db.Text)
    decision_link = db.Column(db.Text)
    notified = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint("case_id", "decision_number", "decision_year", name="uq_result"),
    )

class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key = db.Column(db.Text, nullable=False)
    value = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("user_id", "key", name="uq_setting"),
    )
