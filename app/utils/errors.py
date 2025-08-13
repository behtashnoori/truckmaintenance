"""Utilities for consistent JSON error responses and handlers."""
from typing import Tuple, Dict
from flask import Flask
from werkzeug.exceptions import HTTPException


def json_error(code: str, message: str, status: int = 400) -> Tuple[Dict, int]:
    """Return an error response matching {error:{code,message}}."""
    return {"error": {"code": code, "message": message}}, status


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers producing uniform JSON errors."""

    @app.errorhandler(HTTPException)
    def handle_http_exc(err: HTTPException):  # pragma: no cover - simple wrapper
        code = err.name.lower().replace(" ", "_")
        message = err.description or err.name
        return json_error(code, message, err.code)

    @app.errorhandler(Exception)
    def handle_exc(err: Exception):  # pragma: no cover - simple wrapper
        app.logger.exception("Unhandled exception", exc_info=err)
        return json_error("internal_server_error", "Internal Server Error", 500)
