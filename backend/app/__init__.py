from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("backend.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    # JSON فارسی و مرتب‌سازی کلیدها خاموش
    app.json.ensure_ascii = False
    app.config["JSON_SORT_KEYS"] = False

    # CORS برای فرانت‌اند
    CORS(app, resources={r"*": {"origins": "*"}})

    from backend.routes.company import bp as company_bp
    app.register_blueprint(company_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
