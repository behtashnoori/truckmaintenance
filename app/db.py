from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import MSSQL_URI

engine = create_engine(MSSQL_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    if "db" not in g:
        g.db = SessionLocal()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
