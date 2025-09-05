from flask import Blueprint, request, jsonify
from .. import db
from ..models.company import Company

bp = Blueprint("company", __name__)

@bp.post("/company")
def create_company():
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()
    name = (data.get("name") or "").strip()

    if not phone or not name:
        return jsonify({"error": "phone و name الزامی است"}), 400

    try:
        c = Company(phone=phone, name=name)
        db.session.add(c)
        db.session.commit()
        return jsonify({"message": "ok", "id": c.id, "company": c.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
