from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STORAGE_DIR = BASE_DIR / "storage"
DEFAULT_COMPANY_FILE = DEFAULT_STORAGE_DIR / "companies.json"


class Config:
    """Basic Flask configuration for file-based storage."""

    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    COMPANY_DATA_FILE = os.getenv("COMPANY_DATA_FILE", str(DEFAULT_COMPANY_FILE))
