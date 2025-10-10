from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os


db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_object("backend.config.Config")
    else:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # JSON فارسی و مرتب‌سازی کلیدها خاموش
    app.json.ensure_ascii = False
    app.config["JSON_SORT_KEYS"] = False

    # CORS configuration based on environment
    allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    # For development, allow all origins
    if os.getenv('FLASK_ENV') != 'production':
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
    else:
        CORS(app, resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
    
    # Security headers
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # More permissive CSP for development, stricter for production
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.mapbox.com; "
                "frame-src 'none'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests;"
            )
        else:
            # Development CSP - more permissive
            response.headers['Content-Security-Policy'] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
                "connect-src 'self' https://api.mapbox.com ws: wss:; "
                "img-src 'self' data: blob: https:; "
                "font-src 'self' https://fonts.gstatic.com;"
            )
        
        return response

    with app.app_context():
        from backend.models import company, provider_application, user
    
        # Import all route blueprints
        from backend.routes.company import bp as company_bp
        from backend.routes.provider_applications import bp as provider_applications_bp
        from backend.routes.auth import bp as auth_bp
        from backend.routes.admin import bp as admin_bp
        from backend.routes.business_expert_providers import bp as business_expert_providers_bp
        from backend.routes.admin_categories import bp as admin_categories_bp
        from backend.routes.admin_locations import bp as admin_locations_bp
        from backend.routes.admin_vehicle_types import bp as admin_vehicle_types_bp
        from backend.routes.public import bp as public_bp
        
        # Register all blueprints
        app.register_blueprint(company_bp, url_prefix='/api')
        app.register_blueprint(provider_applications_bp, url_prefix='/api')
        app.register_blueprint(auth_bp, url_prefix='/api')
        app.register_blueprint(admin_bp, url_prefix='/api')
        app.register_blueprint(business_expert_providers_bp, url_prefix='/api')
        app.register_blueprint(admin_categories_bp, url_prefix='/api/admin')
        app.register_blueprint(admin_locations_bp, url_prefix='/api/admin')
        app.register_blueprint(admin_vehicle_types_bp, url_prefix='/api/admin')
        app.register_blueprint(public_bp, url_prefix='/api/public')

    @app.route('/')
    def health():
        return {"status": "ok"}

    return app
