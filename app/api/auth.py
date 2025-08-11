from flask import Blueprint, request
import time
import jwt

from ..config import JWT_SECRET
from ..utils.errors import json_error

bp = Blueprint("auth", __name__)

# simple in-memory OTP storage for development
OTP_CODE = "123456"
OTP_TTL = 5 * 60  # 5 minutes
OTP_RATE_LIMIT = 30  # seconds between requests per phone
_otp_store = {}
_otp_last_request = {}


@bp.post("/request-otp")
def request_otp():
    data = request.get_json() or {}
    phone = data.get("phone")
    if not phone:
        return json_error("phone_required", "phone required")
    now = time.time()
    last = _otp_last_request.get(phone, 0)
    if now - last < OTP_RATE_LIMIT:
        return json_error("rate_limited", "OTP recently requested", 429)
    expires_at = now + OTP_TTL
    _otp_store[phone] = (OTP_CODE, expires_at)
    _otp_last_request[phone] = now
    # In development we return the code directly
    return {"code": OTP_CODE}


@bp.post("/verify-otp")
def verify_otp():
    data = request.get_json() or {}
    phone = data.get("phone")
    code = data.get("code")
    if not phone or not code:
        return json_error("invalid_request", "phone and code required")
    record = _otp_store.get(phone)
    if not record:
        return json_error("code_not_found", "code not found")
    stored_code, expires_at = record
    if stored_code != code or time.time() > expires_at:
        return json_error("invalid_code", "invalid code")
    token = jwt.encode({"phone": phone}, JWT_SECRET, algorithm="HS256")
    return {"token": token}
