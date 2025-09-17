import os
from typing import Optional

MSSQL_SERVER   = os.getenv("MSSQL_SERVER",   "185.10.75.107")
MSSQL_PORT     = os.getenv("MSSQL_PORT")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "Marketplace")
MSSQL_USER     = os.getenv("MSSQL_USER",     "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "REPLACE_WITH_REAL_PASSWORD")
MSSQL_DRIVER   = os.getenv("MSSQL_DRIVER",   "ODBC Driver 17 for SQL Server")


def _normalize_server(server: str, port: Optional[str] = None) -> str:
    """Ensure the server section of the URI uses ``host:port`` when needed."""

    server = server.strip()

    # SQL Server connection strings sometimes include the ``tcp:`` prefix
    # (e.g. ``tcp:127.0.0.1,1433``). SQLAlchemy does not understand this
    # prefix in the URI host section, so we strip it before any further
    # normalization so that the usual ``host:port`` conversion below can run.
    if server.lower().startswith("tcp:"):
        server = server[4:]

    # Explicit port from env has the highest priority.
    if port:
        return f"{server}:{port.strip()}"

    # SQL Server connection strings often specify the port with a comma
    # (e.g. ``127.0.0.1,1433``). SQLAlchemy expects the URI format with
    # a colon, so we convert the first comma to a colon when no colon is present.
    if "," in server and ":" not in server:
        host, port_part = server.split(",", 1)
        return f"{host}:{port_part}"

    return server


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}"
        f"@{_normalize_server(MSSQL_SERVER, MSSQL_PORT)}/{MSSQL_DATABASE}"
        f"?driver={MSSQL_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
