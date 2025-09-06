from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("backend.config.Config")

    # JSON فارسی/مرتب‌سازی خاموش
    app.json.ensure_ascii = False
    app.config.setdefault("JSON_SORT_KEYS", False)

    db.init_app(app)
    migrate.init_app(app, db)

    # ایمپورت مدل‌ها برای Alembic
    from backend.models import Company  # noqa: F401

    # ثبت روت‌ها
    from backend.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/")

    return app

