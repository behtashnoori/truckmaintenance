import os

MSSQL_SERVER   = os.getenv("MSSQL_SERVER",   "185.10.75.107")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "Marketplace")
MSSQL_USER     = os.getenv("MSSQL_USER",     "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "REPLACE_WITH_REAL_PASSWORD")
MSSQL_DRIVER   = os.getenv("MSSQL_DRIVER",   "ODBC Driver 17 for SQL Server")


def _build_default_uri() -> str:
    """Compose the fallback SQLAlchemy connection URI."""

    driver = MSSQL_DRIVER.replace(" ", "+")
    return (
        f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}"
        f"@{MSSQL_SERVER}/{MSSQL_DATABASE}?driver={driver}&TrustServerCertificate=yes"
    )


class Config:
    _uri_from_env = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("MSSQL_URI")
    SQLALCHEMY_DATABASE_URI = _uri_from_env or _build_default_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
