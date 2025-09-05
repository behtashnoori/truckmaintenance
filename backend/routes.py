from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Company

api_bp = Blueprint("api", __name__)


@api_bp.route("/company", methods=["POST"])
def create_company():
    data = request.get_json(silent=True) or {}
    tel  = (data.get("phone") or data.get("tel") or "").strip()
    name = (data.get("name") or "").strip()

    if not tel or not name:
        return jsonify({"error": "tel/phone و name الزامی است"}), 400

    if Company.query.filter_by(Tel=tel).first():
        return jsonify({"error": "tel تکراری است"}), 409

    c = Company(Tel=tel, Name=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.Id, "status": "ok"})
