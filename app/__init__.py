import logging
import json
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import ENV, DEBUG, FRONTEND_ORIGINS
from .db import close_db
from .utils.errors import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config["ENV"] = ENV
    app.config["DEBUG"] = DEBUG

    CORS(app, origins=FRONTEND_ORIGINS)

    if ENV == "production":
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                data = {
                    "level": record.levelname,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    data["exc_info"] = self.formatException(record.exc_info)
                return json.dumps(data)

        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        app.logger.handlers = [handler]
        app.logger.setLevel(logging.INFO)

    from .api.auth import bp as auth_bp
    from .api.providers import bp as providers_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(providers_bp, url_prefix="/providers")

    dist_dir = Path(__file__).resolve().parent.parent / "dist"

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def index(path: str):
        """Serve the built frontend for root and client-side routes."""
        if dist_dir.exists():
            file_path = dist_dir / path
            if path and file_path.exists():
                return send_from_directory(dist_dir, path)
            return send_from_directory(dist_dir, "index.html")
        return {"status": "ok"}

    @app.route("/health")
    def health():
        return {"status": "ok"}

    register_error_handlers(app)
    app.teardown_appcontext(close_db)

    return app


app = create_app()
