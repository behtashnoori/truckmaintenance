from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from pydantic import ValidationError
from ..app import db
from ..models.provider_application import ProviderApplication
from ..models.company import Company, Category
from ..middleware.security import token_required, business_expert_required, validate_input, sanitize_string, validate_phone
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..schemas.response import ApiResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("provider_applications", __name__)


@bp.route("/provider-applications", methods=["POST"])
@validate_input(required_fields=["companyName", "representativeFirstName", "representativeLastName", "address", "phoneMobile", "serviceDomain", "latitude", "longitude"],
                allowed_fields=["companyName", "representativeFirstName", "representativeLastName", "address", "phoneMobile", "phoneLandline", "serviceDomain", "latitude", "longitude"])
def create_provider_application():
    """Create a new provider application (public endpoint)"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400

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
            return jsonify({
                "success": False,
                "error": "فرمت شماره موبایل نامعتبر است"
            }), 400
        
        # Validate coordinates
        try:
            latitude = float(data["latitude"])
            longitude = float(data["longitude"])
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return jsonify({
                    "success": False,
                    "error": "مختصات جغرافیایی نامعتبر است"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "مختصات جغرافیایی باید عدد باشد"
            }), 400

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
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(new_app)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "درخواست شما با موفقیت ثبت شد",
            "data": {
                "id": new_app.id,
                "status": new_app.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating provider application: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در ثبت درخواست"
        }), 500


@bp.route("/business-expert/applications", methods=["GET"])
@token_required
@business_expert_required
def get_pending_applications(current_user):
    """Get pending applications with pagination - Business Expert only"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', 'pending', type=str)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Query applications
        query = ProviderApplication.query.filter_by(status=status).order_by(
            ProviderApplication.created_at.desc()
        )
        
        total = query.count()
        apps = query.offset(pagination.offset).limit(pagination.limit).all()
        
        # Build response
        applications_list = [app.to_dict() for app in apps]
        
        # Return paginated response
        response = PaginatedResponse.create(
            items=applications_list,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting applications: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در دریافت درخواست‌ها"
        }), 500


@bp.route("/business-expert/applications/<int:app_id>", methods=["GET"])
@token_required
@business_expert_required
def get_application_details(current_user, app_id):
    """Get application details - Business Expert only"""
    try:
        app = ProviderApplication.query.get(app_id)
        
        if not app:
            return jsonify({
                "success": False,
                "error": "درخواست یافت نشد"
            }), 404
        
        return jsonify({
            "success": True,
            "data": app.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting application details: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در دریافت جزئیات درخواست"
        }), 500


@bp.route("/business-expert/applications/<int:app_id>/approve", methods=["POST"])
@token_required
@business_expert_required
def approve_application(current_user, app_id):
    """Approve an application and create/update company - Business Expert only"""
    try:
        app = ProviderApplication.query.get(app_id)
        
        if not app:
            return jsonify({
                "success": False,
                "error": "درخواست یافت نشد"
            }), 404
        
        if app.status != 'pending':
            return jsonify({
                "success": False,
                "error": "درخواست قبلاً پردازش شده است"
            }), 400

        data = request.get_json() or {}
        app.status = 'approved'
        app.is_approved = True
        app.reviewed_at = datetime.now(timezone.utc)
        app.review_notes = sanitize_string(data.get("notes", "")) if data.get("notes") else None
        app.reviewed_by = current_user.id

        # Create a new company from the application
        # Check if a category with the given service domain exists, or create it
        category = Category.query.filter_by(name=app.service_domain).first()
        if not category:
            category = Category(name=app.service_domain)
            db.session.add(category)
            db.session.flush()

        # Check if company with this phone number already exists
        existing_company = Company.query.filter_by(phone_mobile=app.phone_mobile).first()
        if existing_company:
            # Update the existing company and link the category
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
                is_active=True,
                created_by=current_user.id
            )
            new_company.categories.append(category)
            db.session.add(new_company)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "درخواست تأیید شد و شرکت ایجاد/بروزرسانی شد",
            "data": {"status": "approved"}
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving application: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در تأیید درخواست"
        }), 500


@bp.route("/business-expert/applications/<int:app_id>/reject", methods=["POST"])
@token_required
@business_expert_required
def reject_application(current_user, app_id):
    """Reject an application - Business Expert only"""
    try:
        app = ProviderApplication.query.get(app_id)
        
        if not app:
            return jsonify({
                "success": False,
                "error": "درخواست یافت نشد"
            }), 404
        
        if app.status != 'pending':
            return jsonify({
                "success": False,
                "error": "درخواست قبلاً پردازش شده است"
            }), 400

        data = request.get_json()
        if not data or not data.get("notes"):
            return jsonify({
                "success": False,
                "error": "توضیحات رد درخواست الزامی است"
            }), 400

        app.status = 'rejected'
        app.is_approved = False
        app.reviewed_at = datetime.now(timezone.utc)
        app.review_notes = sanitize_string(data.get("notes"))
        app.reviewed_by = current_user.id
        
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "درخواست رد شد",
            "data": {"status": "rejected"}
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting application: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در رد درخواست"
        }), 500


@bp.route("/business-expert/applications/<int:app_id>", methods=["PATCH"])
@token_required
@business_expert_required
def update_application_status(current_user, app_id):
    """Update application status - Business Expert only"""
    try:
        app = ProviderApplication.query.get(app_id)
        
        if not app:
            return jsonify({
                "success": False,
                "error": "درخواست یافت نشد"
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "داده نامعتبر است"
            }), 400
        
        # Validate status
        new_status = data.get('status')
        if new_status and new_status not in ['pending', 'approved', 'rejected']:
            return jsonify({
                "success": False,
                "error": "وضعیت نامعتبر است. مقادیر مجاز: pending, approved, rejected"
            }), 400
        
        # Update status
        if new_status:
            app.status = new_status
            app.is_approved = (new_status == 'approved')
            app.reviewed_by = current_user.id
            app.reviewed_at = datetime.now(timezone.utc)
        
        # Update review notes if provided
        if 'review_notes' in data:
            app.review_notes = sanitize_string(data['review_notes'])
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "درخواست با موفقیت بروزرسانی شد",
            "data": app.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating application: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در بروزرسانی درخواست"
        }), 500


@bp.route("/business-expert/dashboard", methods=["GET"])
@token_required
@business_expert_required
def get_business_expert_dashboard(current_user):
    """Get business expert dashboard statistics"""
    try:
        pending_reviews = ProviderApplication.query.filter_by(status='pending').count()
        approved_today = ProviderApplication.query.filter(
            ProviderApplication.status == 'approved',
            db.func.date(ProviderApplication.reviewed_at) == datetime.now(timezone.utc).date()
        ).count()
        total_companies = Company.query.filter_by(is_active=True).count()
        
        stats = {
            "pending_reviews": pending_reviews,
            "approved_today": approved_today,
            "total_companies": total_companies
        }
        
        return jsonify({
            "success": True,
            "data": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در دریافت آمار داشبورد"
        }), 500
