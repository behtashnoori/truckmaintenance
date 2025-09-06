from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from backend.app import db
from backend.models import Company

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"status": "ok"}, 200
    except Exception as e:
        current_app.logger.exception("health check failed")
        return {"status": "error", "detail": str(e)}, 500


@api_bp.route("/company", methods=["POST"])
def create_company():
    data = request.get_json(silent=True) or {}
    tel = (data.get("phone") or data.get("tel") or "").strip()
    name = (data.get("name") or "").strip()

    if not tel or not name:
        return jsonify({"error": "tel/phone و name الزامی است"}), 400

    try:
        # جلوگیری از تکرار
        if Company.query.filter_by(Tel=tel).first():
            return jsonify({"error": "tel تکراری است"}), 409

        c = Company(Tel=tel, Name=name)
        db.session.add(c)
        db.session.commit()
        return jsonify(c.to_dict()), 201
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("DB error on create_company")
        return jsonify({"error": "database error"}), 500


@api_bp.route("/company", methods=["GET"])
def list_companies():
    items = Company.query.order_by(Company.Id.desc()).limit(50).all()
    return jsonify([c.to_dict() for c in items]), 200


@api_bp.route("/company/<int:cid>", methods=["GET"])
def get_company(cid: int):
    c = Company.query.get_or_404(cid)
    return jsonify(c.to_dict()), 200

