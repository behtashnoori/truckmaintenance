from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
from pathlib import Path


db = SQLAlchemy()
migrate = Migrate()

DIST_DIR = Path(__file__).resolve().parent.parent / "src" / "dist"


def create_app():
    load_dotenv()
    app = Flask(
        __name__,
        static_folder=str(DIST_DIR),
        static_url_path="/"
    )
    app.config.from_object("backend.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    # JSON فارسی و مرتب‌سازی کلیدها خاموش
    app.json.ensure_ascii = False
    app.config["JSON_SORT_KEYS"] = False

    # CORS برای فرانت‌اند در حالت توسعه
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from backend.routes.company import bp as company_bp
    app.register_blueprint(company_bp, url_prefix="/api")

    # Catch-all برای SPA در حالت تولید
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        index_file = DIST_DIR / "index.html"
        if index_file.exists():
            return send_from_directory(DIST_DIR, "index.html")
        return "Build not found. Run: npm run build", 404

    return app
