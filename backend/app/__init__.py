import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv


db = SQLAlchemy()
migrate = None


def create_app():
    load_dotenv()  # .env را لود کن
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    global migrate
    migrate = Migrate(app, db)

    # ثبت بلوپرینت ها
    from .routes.company import bp as company_bp
    app.register_blueprint(company_bp, url_prefix="/")

    # ساخت جداول در صورت نبود (برای Dev)
    with app.app_context():
        from .models.company import Company  # اطمینان از import مدل
        db.create_all()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
