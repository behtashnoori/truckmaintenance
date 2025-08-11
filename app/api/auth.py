from flask import Blueprint, request
import time
import jwt

from ..config import JWT_SECRET

bp = Blueprint("auth", __name__)

# simple in-memory OTP storage for development
OTP_CODE = "123456"
OTP_TTL = 5 * 60  # 5 minutes
_otp_store = {}


@bp.post("/request-otp")
def request_otp():
    data = request.get_json() or {}
    phone = data.get("phone")
    if not phone:
        return {"error": "phone required"}, 400
    expires_at = time.time() + OTP_TTL
    _otp_store[phone] = (OTP_CODE, expires_at)
    # In development we return the code directly
    return {"code": OTP_CODE}


@bp.post("/verify-otp")
def verify_otp():
    data = request.get_json() or {}
    phone = data.get("phone")
    code = data.get("code")
    if not phone or not code:
        return {"error": "phone and code required"}, 400
    record = _otp_store.get(phone)
    if not record:
        return {"error": "code not found"}, 400
    stored_code, expires_at = record
    if stored_code != code or time.time() > expires_at:
        return {"error": "invalid code"}, 400
    token = jwt.encode({"phone": phone}, JWT_SECRET, algorithm="HS256")
    return {"token": token}
