from flask import Blueprint, request, jsonify
from ..app import db
from ..models.company import Company
from ..middleware.security import token_required, business_expert_required, validate_input, sanitize_string, validate_phone

bp = Blueprint("company", __name__)


@bp.route("/company", methods=["POST"])
@token_required
@business_expert_required
@validate_input(required_fields=['name', 'phone'], allowed_fields=['name', 'phone', 'companyName', 'tel'])
def create_company(current_user):
    """
    Create company (business expert only)
    بدنه‌ی ورودی:
    {
        "phone": "09xxxxxxxxx",
        "name": "نام شرکت"
    }
    """
    data = request.get_json()
    name = sanitize_string(data.get("name") or data.get("companyName") or "")
    phone = (data.get("phone") or data.get("tel") or "").strip()

    if not name or not phone:
        return jsonify({"error": "name و phone الزامی هستند"}), 400
    
    if not validate_phone(phone):
        return jsonify({"error": "فرمت شماره تلفن نامعتبر است"}), 400

    try:
        # Check if company already exists
        existing_company = Company.query.filter_by(phone_mobile=phone).first()
        if existing_company:
            return jsonify({"error": "شرکت با این شماره تلفن قبلاً ثبت شده است"}), 409
        
        company = Company(
            name=name,
            phone_mobile=phone,
            address="",  # Default empty address
            latitude=0.0,  # Default coordinates
            longitude=0.0,
            is_active=True
        )
        db.session.add(company)
        db.session.commit()
        return jsonify({"id": company.id, "message": "company created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
