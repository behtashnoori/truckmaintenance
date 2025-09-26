from flask import Blueprint, request, jsonify
from datetime import datetime
from ..app import db
from ..models.provider_application import ProviderApplication
from ..models.company import Company, Category
from ..middleware.security import token_required, business_expert_required, validate_input, sanitize_string, validate_phone

bp = Blueprint("provider_applications", __name__)


@bp.route("/provider-applications", methods=["POST"])
@validate_input(required_fields=["companyName", "representativeFirstName", "representativeLastName", "address", "phoneMobile", "serviceDomain", "latitude", "longitude"],
                allowed_fields=["companyName", "representativeFirstName", "representativeLastName", "address", "phoneMobile", "phoneLandline", "serviceDomain", "latitude", "longitude"])
def create_provider_application():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    # Sanitize all string inputs
    company_name = sanitize_string(data["companyName"])
    rep_first_name = sanitize_string(data["representativeFirstName"])
    rep_last_name = sanitize_string(data["representativeLastName"])
    address = sanitize_string(data["address"])
    phone_mobile = data["phoneMobile"].strip()
    phone_landline = data.get("phoneLandline", "").strip() if data.get("phoneLandline") else None
    service_domain = sanitize_string(data["serviceDomain"])
    
    # Validate phone number
    if not validate_phone(phone_mobile):
        return jsonify({"error": "فرمت شماره موبایل نامعتبر است"}), 400
    
    # Validate coordinates
    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "مختصات جغرافیایی نامعتبر است"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "مختصات جغرافیایی باید عدد باشد"}), 400

    new_app = ProviderApplication(
        company_name=company_name,
        representative_first_name=rep_first_name,
        representative_last_name=rep_last_name,
        address=address,
        phone_mobile=phone_mobile,
        phone_landline=phone_landline,
        service_domain=service_domain,
        latitude=latitude,
        longitude=longitude,
        created_at=datetime.utcnow()
    )
    db.session.add(new_app)
    db.session.commit()

    return jsonify({"id": new_app.id, "status": new_app.status, "message": "Application received."}), 201


@bp.route("/business-expert/applications", methods=["GET"])
@token_required
@business_expert_required
def get_pending_applications(current_user):
    apps = ProviderApplication.query.filter_by(status='pending').order_by(ProviderApplication.created_at.desc()).all()
    return jsonify({"applications": [app.to_dict() for app in apps]}), 200


@bp.route("/business-expert/applications/<int:app_id>", methods=["GET"])
@token_required
@business_expert_required
def get_application_details(current_user, app_id):
    app = ProviderApplication.query.get_or_404(app_id)
    return jsonify(app.to_dict()), 200


@bp.route("/business-expert/applications/<int:app_id>/approve", methods=["POST"])
@token_required
@business_expert_required
@validate_input(allowed_fields=["notes"]) 
def approve_application(current_user, app_id):
    app = ProviderApplication.query.get_or_404(app_id)
    if app.status != 'pending':
        return jsonify({"error": "Application already processed"}), 400

    data = request.get_json() or {}
    app.status = 'approved'
    app.is_approved = True
    app.reviewed_at = datetime.utcnow()
    app.review_notes = sanitize_string(data.get("notes", "")) if data.get("notes") else None
    # app.reviewed_by = current_user.id

    # Create a new company from the application
    # Check if a category with the given service domain exists, or create it
    category = Category.query.filter_by(name=app.service_domain).first()
    if not category:
        category = Category(name=app.service_domain)
        db.session.add(category)
        # We need to commit here so the category gets an ID
        db.session.commit()

    # Check if company with this phone number already exists
    existing_company = Company.query.filter_by(phone_mobile=app.phone_mobile).first()
    if existing_company:
        # Potentially update the existing company, for now we will just link the category
        if category not in existing_company.categories:
            existing_company.categories.append(category)
    else:
        # Create a new company
        new_company = Company(
            name=app.company_name,
            address=app.address,
            phone_mobile=app.phone_mobile,
            phone_landline=app.phone_landline,
            latitude=app.latitude,
            longitude=app.longitude,
            is_active=True
        )
        new_company.categories.append(category)
        db.session.add(new_company)

    db.session.commit()

    return jsonify({"message": "Application approved and company created/updated.", "status": "approved"}), 200


@bp.route("/business-expert/applications/<int:app_id>/reject", methods=["POST"])
@token_required
@business_expert_required
@validate_input(required_fields=["notes"], allowed_fields=["notes"]) 
def reject_application(current_user, app_id):
    app = ProviderApplication.query.get_or_404(app_id)
    if app.status != 'pending':
        return jsonify({"error": "Application already processed"}), 400

    data = request.get_json()
    if not data or not data.get("notes"):
        return jsonify({"error": "Review notes are required for rejection"}), 400

    app.status = 'rejected'
    app.is_approved = False
    app.reviewed_at = datetime.utcnow()
    app.review_notes = sanitize_string(data.get("notes"))
    # app.reviewed_by = current_user.id
    
    db.session.commit()

    return jsonify({"message": "Application rejected.", "status": "rejected"}), 200

@bp.route("/business-expert/dashboard", methods=["GET"])
@token_required
@business_expert_required
def get_business_expert_dashboard(current_user):
    pending_reviews = ProviderApplication.query.filter_by(status='pending').count()
    approved_today = ProviderApplication.query.filter(
        ProviderApplication.status == 'approved',
        db.func.date(ProviderApplication.reviewed_at) == datetime.utcnow().date()
    ).count()
    total_companies = Company.query.filter_by(is_active=True).count()
    
    stats = {
        "pending_reviews": pending_reviews,
        "approved_today": approved_today,
        "total_companies": total_companies,
        # Mock data for fields not in db
        "monthly_revenue": "12.5M",
        "review_efficiency": 85,
        "customer_satisfaction": 92
    }
    
    return jsonify(stats), 200


