from flask import Flask
from flask_cors import CORS

from .config import ENV, DEBUG, FRONTEND_ORIGINS
from .db import close_db


def create_app():
    app = Flask(__name__)
    app.config["ENV"] = ENV
    app.config["DEBUG"] = DEBUG

    CORS(app, origins=FRONTEND_ORIGINS)

    from .api.auth import bp as auth_bp
    from .api.providers import bp as providers_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(providers_bp, url_prefix="/providers")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    app.teardown_appcontext(close_db)

    return app


app = create_app()
