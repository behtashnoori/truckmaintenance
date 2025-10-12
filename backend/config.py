import os
from .db_credentials import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)


class Config:
    # Database connection string (PostgreSQL by default, can be overridden for testing)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    TESTING = os.getenv("TESTING", "false").lower() == "true"
    
    # Rate Limiting Configuration
    RATE_LIMIT_APPLICATIONS_PER_HOUR = int(os.getenv("RATE_LIMIT_APPLICATIONS_PER_HOUR", "3"))
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # Duplicate Detection Configuration
    FUZZY_MATCH_THRESHOLD = float(os.getenv("FUZZY_MATCH_THRESHOLD", "0.8"))
    DUPLICATE_CHECK_ENABLED = os.getenv("DUPLICATE_CHECK_ENABLED", "true").lower() == "true"
    
    # Phone Validation Configuration
    PHONE_PATTERN = r'^09\d{9}$'
    
    # Support Contact Information
    SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "021-12345678")