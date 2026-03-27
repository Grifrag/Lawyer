from flask import Blueprint
bp = Blueprint("settings_bp", __name__)
from app.settings_bp import routes  # noqa
