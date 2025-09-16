from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..storage.company_store import add_company

bp = Blueprint("company", __name__)


@bp.route("/company", methods=["POST"])
def create_company():
    """ثبت اطلاعات شرکت بدون نیاز به پایگاه داده خارجی."""

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or data.get("companyName") or "").strip()
    phone = (data.get("phone") or data.get("tel") or "").strip()

    if not name or not phone:
        return jsonify({"error": "name و phone الزامی هستند"}), 400

    try:
        company = add_company(name=name, phone=phone)
        return jsonify({"id": company["id"], "message": "company created"}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - محافظت در برابر خطاهای غیرمنتظره
        return jsonify({"error": str(exc)}), 500
