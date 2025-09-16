from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List

from flask import current_app

DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "companies.json"
_LOCK = Lock()

Record = Dict[str, Any]
Records = List[Record]


def _data_file() -> Path:
    """Return the path to the JSON file used for persisting companies."""

    configured_path: str | None = None
    try:
        configured_path = current_app.config.get("COMPANY_DATA_FILE")  # type: ignore[attr-defined]
    except RuntimeError:
        # No application context; fall back to default path.
        configured_path = None

    if configured_path:
        path = Path(configured_path)
    else:
        path = DEFAULT_DATA_FILE

    if not path.is_absolute():
        # Interpret relative paths relative to this module's directory.
        path = (DEFAULT_DATA_FILE.parent / path).resolve()

    return path


def _read_data() -> Records:
    path = _data_file()
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _write_data(data: Records) -> None:
    path = _data_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def _next_id(data: Records) -> int:
    max_id = 0
    for item in data:
        value = item.get("id")
        try:
            numeric = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        max_id = max(max_id, numeric)
    return max_id + 1


def add_company(*, name: str, phone: str) -> Record:
    """Persist a new company record and return it."""

    clean_name = name.strip()
    clean_phone = phone.strip()

    if not clean_name or not clean_phone:
        raise ValueError("name and phone are required")

    with _LOCK:
        data = _read_data()
        record: Record = {
            "id": _next_id(data),
            "name": clean_name,
            "phone": clean_phone,
        }
        data.append(record)
        _write_data(data)

    return record


def list_companies() -> Records:
    """Return all persisted companies."""

    with _LOCK:
        data = _read_data()
        # Return a shallow copy so callers cannot mutate internal state.
        return [dict(item) for item in data]
