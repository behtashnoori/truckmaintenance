from __future__ import annotations

from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("backend.config.Config")

    # JSON فارسی و مرتب‌سازی کلیدها خاموش
    app.json.ensure_ascii = False
    app.config["JSON_SORT_KEYS"] = False

    # CORS برای فرانت‌اند
    CORS(app, resources={r"*": {"origins": "*"}})

    from backend.routes.company import bp as company_bp

    app.register_blueprint(company_bp)

    return app
