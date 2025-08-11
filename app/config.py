import os
from dotenv import load_dotenv

load_dotenv()

MSSQL_URI = os.getenv(
    "MSSQL_URI",
    "mssql+pyodbc://user:pass@HOST/DB?driver=ODBC+Driver+17+for+SQL+Server",
)
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t")
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in FRONTEND_ORIGINS.split(",")
    if origin.strip()
]
