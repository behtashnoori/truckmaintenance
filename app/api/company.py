"""Company creation endpoint."""
from flask import Blueprint, request

from ..db import get_db
from ..models import Company
from ..utils.errors import json_error

bp = Blueprint("company", __name__)


@bp.post("/")
def create_company():
    """Create a new company with phone and name."""
    data = request.get_json() or {}
    phone = data.get("phone")
    name = data.get("name")
    if not phone or not name:
        return json_error("invalid_request", "phone and name required")
    db = get_db()
    company = Company(phone=phone, name=name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return {"message": "company created", "id": company.id}
