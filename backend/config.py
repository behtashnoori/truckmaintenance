import os

MSSQL_SERVER   = os.getenv("MSSQL_SERVER",   "185.10.75.107")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "Marketplace")
MSSQL_USER     = os.getenv("MSSQL_USER",     "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "Sa123sa")
MSSQL_DRIVER   = os.getenv("MSSQL_DRIVER",   "ODBC Driver 17 for SQL Server")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}"
        f"@{MSSQL_SERVER}/{MSSQL_DATABASE}"
        f"?driver={MSSQL_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
