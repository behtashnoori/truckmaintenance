from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
from urllib.parse import quote_plus
from pathlib import Path
import os

db = SQLAlchemy()
migrate = Migrate()
DIST_DIR = Path(__file__).resolve().parents[2] / "src" / "dist"


def create_app():
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
    app = Flask(__name__)
    app.config.from_object("backend.config.Config")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.ensure_ascii = False
    app.config["JSON_SORT_KEYS"] = False

    uri = os.getenv("SQLALCHEMY_DATABASE_URI") or app.config.get("SQLALCHEMY_DATABASE_URI")
    if not uri:
        user = os.getenv("DB_USER","sa")
        pwd  = quote_plus(os.getenv("DB_PASSWORD",""))
        dbn  = os.getenv("DB_NAME","Marketplace")
        host = os.getenv("DB_SERVER","127.0.0.1")
        port = os.getenv("DB_PORT","1433")
        driver = os.getenv("DB_DRIVER","ODBC Driver 17 for SQL Server")
        if host.startswith("tcp:"): host = host[4:]
        host = host.replace(",",":")
        uri = f"mssql+pyodbc://{user}:{pwd}@{host}:{port}/{dbn}?driver={quote_plus(driver)}&Encrypt=no&TrustServerCertificate=yes"
    else:
        uri = uri.replace("tcp:","").replace(",",":")
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    print("DB URI (normalized):", app.config["SQLALCHEMY_DATABASE_URI"], flush=True)

    db.init_app(app); migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    with app.app_context():
        import backend.models  # noqa: F401

    from backend.routes.company import bp as company_bp
    app.register_blueprint(company_bp, url_prefix="/api")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        index_file = DIST_DIR / "index.html"
        if index_file.exists():
            return send_from_directory(DIST_DIR, "index.html")
        return "Build not found. Run: npm run build", 404

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app

