from datetime import date as date_cls, datetime

from flask import Blueprint, request, jsonify

from ..app import db
from ..models.company import Company

bp = Blueprint("company", __name__, url_prefix="/api/signup")


def _prepare_company_details(data, *, include_default_date: bool) -> dict:
    type_of_service = (
        (data.get("type_of_service") or data.get("Type_Of_Service") or "")
        .strip()
        or None
    )

    radius_of_activity = data.get("radius_of_activity") or data.get("Radius_Of_Activity")
    if isinstance(radius_of_activity, str):
        radius_of_activity = radius_of_activity.strip()
        radius_of_activity = int(radius_of_activity) if radius_of_activity else None
    elif radius_of_activity is not None:
        try:
            radius_of_activity = int(radius_of_activity)
        except (TypeError, ValueError):
            radius_of_activity = None

    working_hours = (
        (data.get("working_hours") or data.get("Working_Hours") or "")
        .strip()
        or None
    )

    vehicle_type = data.get("vehicle_type") or data.get("Vehicle_Type")
    if isinstance(vehicle_type, (list, tuple)):
        vehicle_type = ", ".join(str(item) for item in vehicle_type if str(item).strip()) or None
    elif isinstance(vehicle_type, str):
        vehicle_type = vehicle_type.strip() or None
    else:
        vehicle_type = None

    raw_date = data.get("date") or data.get("Date")
    parsed_date = None
    if isinstance(raw_date, datetime):
        parsed_date = raw_date
    elif isinstance(raw_date, date_cls):
        parsed_date = datetime.combine(raw_date, datetime.min.time())
    elif isinstance(raw_date, str) and raw_date.strip():
        cleaned = raw_date.strip()
        cleaned = cleaned.replace("Z", "+00:00") if cleaned.endswith("Z") else cleaned
        try:
            parsed_date = datetime.fromisoformat(cleaned)
        except ValueError:
            parsed_date = None

    if parsed_date is None and include_default_date:
        parsed_date = datetime.utcnow()

    return {
        "type_of_service": type_of_service,
        "radius_of_activity": radius_of_activity,
        "working_hours": working_hours,
        "vehicle_type": vehicle_type,
        "date_value": parsed_date,
    }


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
        details = _prepare_company_details(data, include_default_date=False)
        company = Company(Tel=phone, Name=name)
        company.update_details(**details)
        db.session.add(company)
        db.session.commit()
        return (
            jsonify(
                {
                    "id": company.Id,
                    "message": "company created",
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/company/<int:company_id>", methods=["PUT"])
def update_company(company_id: int):
    data = request.get_json(silent=True) or {}
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "company not found"}), 404

    details = _prepare_company_details(data, include_default_date=True)

    try:
        company.update_details(**details)
        db.session.commit()
        return jsonify({"id": company.Id, "message": "company updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
