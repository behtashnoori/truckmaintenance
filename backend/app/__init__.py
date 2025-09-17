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

    # DB & migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # JSON فارسی و عدم مرتب‌سازی کلیدها
    app.json.ensure_ascii = False
    app.config["JSON_SORT_KEYS"] = False

    # CORS فقط برای مسیرهای API
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},  # اگر خواستی به IP خودت محدود کن
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
    )

    # --- Health ---
    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    # --- Blueprints ---
    from backend.routes.company import bp as company_bp
    # چون داخل company.py prefix ندارد، اینجا می‌دهیم:
    app.register_blueprint(company_bp, url_prefix="/api")

    return app
