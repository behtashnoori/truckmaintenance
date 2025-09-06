from flask import Blueprint, request, jsonify
from ..app import db
from ..models.company import Company

bp = Blueprint("company", __name__)


@bp.route("/company", methods=["POST"])
def create_company():
    """
    بدنه‌ی ورودی:
    {
        "phone": "09xxxxxxxxx",
        "name": "نام شرکت"
    }
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or data.get("companyName") or "").strip()
    phone = (data.get("phone") or data.get("tel") or "").strip()

    if not name or not phone:
        return jsonify({"error": "name و phone الزامی هستند"}), 400

    try:
        company = Company(Tel=phone, Name=name)
        db.session.add(company)
        db.session.commit()
        return jsonify({"id": company.Id, "message": "company created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
