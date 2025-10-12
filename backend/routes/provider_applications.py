from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from ..app import db
from ..models.provider_application import ProviderApplication
from ..models.company import Company, Category
from ..middleware.security import (
    token_required, business_expert_required, validate_input, 
    sanitize_string, validate_phone, sanitize_phone,
    validate_company_name, check_suspicious_patterns
)
from ..middleware.rate_limiting import application_rate_limit
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..schemas.response import ApiResponse, ErrorResponse
from ..utils.fuzzy_match import check_company_name_similarity
import logging
import hashlib

logger = logging.getLogger(__name__)

bp = Blueprint("provider_applications", __name__)


@bp.route("/provider-applications", methods=["POST"])
@application_rate_limit
@validate_input(required_fields=["companyName", "representativeFirstName", "representativeLastName", "address", "phoneMobile", "serviceCategories", "latitude", "longitude"],
                allowed_fields=["companyName", "representativeFirstName", "representativeLastName", "address", "phoneMobile", "phoneLandline", "serviceCategories", "latitude", "longitude"])
def create_provider_application():
    """Create a new provider application (public endpoint) with duplicate prevention"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "داده‌های ورودی نامعتبر است"
                }
            }), 400

        # Get client IP for logging
        client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

        # Sanitize all string inputs
        company_name = sanitize_string(data["companyName"])
        rep_first_name = sanitize_string(data["representativeFirstName"])
        rep_last_name = sanitize_string(data["representativeLastName"])
        address = sanitize_string(data["address"])
        phone_mobile = sanitize_phone(data["phoneMobile"])
        phone_landline = sanitize_phone(data.get("phoneLandline", "")) if data.get("phoneLandline") else None
        
        # Validate company name
        if not validate_company_name(company_name):
            logger.warning(f"Invalid company name attempt: ip={client_ip}")
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_COMPANY_NAME",
                    "message": "نام شرکت نامعتبر است. لطفاً نام معتبر وارد کنید."
                }
            }), 400
        
        # Check for suspicious patterns
        suspicious_warnings = check_suspicious_patterns(data)
        if suspicious_warnings:
            logger.warning(f"Suspicious patterns detected: {suspicious_warnings}, ip={client_ip}")
        
        # Validate and process service categories
        service_categories = data.get("serviceCategories", [])
        if not isinstance(service_categories, list):
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_CATEGORIES",
                    "message": "serviceCategories باید یک آرایه باشد"
                }
            }), 400
        
        if not service_categories:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NO_CATEGORIES",
                    "message": "حداقل یک حوزه خدماتی باید انتخاب شود"
                }
            }), 400
        
        # Sanitize category names
        service_categories = [sanitize_string(cat) for cat in service_categories if cat and cat.strip()]
        
        if not service_categories:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NO_VALID_CATEGORIES",
                    "message": "حداقل یک حوزه خدماتی معتبر باید انتخاب شود"
                }
            }), 400
        
        # Validate phone number
        if not validate_phone(phone_mobile):
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_PHONE",
                    "message": "فرمت شماره موبایل نامعتبر است. شماره موبایل باید 11 رقم و با 09 شروع شود."
                }
            }), 400
        
        # ===== DUPLICATE PHONE NUMBER CHECK =====
        if current_app.config.get('DUPLICATE_CHECK_ENABLED', True):
            existing_app = ProviderApplication.query.filter_by(phone_mobile=phone_mobile).first()
            
            if existing_app:
                # Log duplicate attempt
                phone_hash = hashlib.sha256(phone_mobile.encode()).hexdigest()[:16]
                logger.warning(
                    f"Duplicate phone number attempt: phone_hash={phone_hash}, "
                    f"existing_app_id={existing_app.id}, ip={client_ip}"
                )
                
                # Return detailed error with support contact
                support_phone = current_app.config.get('SUPPORT_PHONE', '021-12345678')
                
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_PHONE",
                        "message": "این شماره موبایل قبلاً در سیستم ثبت شده است.",
                        "action": "لطفاً با شماره دیگری ثبت‌نام کنید یا با پشتیبانی تماس بگیرید.",
                        "support_contact": support_phone,
                        "details": "اگر قبلاً ثبت‌نام کرده‌اید، لطفاً منتظر تماس کارشناس بازرگانی باشید."
                    }
                }), 409  # HTTP 409 Conflict
        
        # ===== FUZZY MATCHING FOR COMPANY NAME =====
        fuzzy_match_warning = False
        similar_companies = []
        
        if current_app.config.get('DUPLICATE_CHECK_ENABLED', True):
            # Get existing company names from applications and companies
            existing_app_names = [app.company_name for app in ProviderApplication.query.all()]
            existing_company_names = [comp.name for comp in Company.query.all()]
            all_existing_names = list(set(existing_app_names + existing_company_names))
            
            # Check for similar names
            threshold = current_app.config.get('FUZZY_MATCH_THRESHOLD', 0.8)
            similarity_result = check_company_name_similarity(company_name, all_existing_names, threshold)
            
            if similarity_result['has_similar']:
                fuzzy_match_warning = True
                similar_companies = similarity_result['similar_names'][:3]  # Top 3 similar names
                
                # Log fuzzy match
                logger.info(
                    f"Fuzzy match detected: new_name='{company_name}', "
                    f"similar_to={similar_companies}, "
                    f"highest_similarity={similarity_result['highest_similarity']:.2f}, "
                    f"ip={client_ip}"
                )
        
        # Validate coordinates
        try:
            latitude = float(data["latitude"])
            longitude = float(data["longitude"])
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_COORDINATES",
                        "message": "مختصات جغرافیایی نامعتبر است"
                    }
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_COORDINATES",
                    "message": "مختصات جغرافیایی باید عدد باشد"
                }
            }), 400

        # Create new application
        new_app = ProviderApplication(
            company_name=company_name,
            representative_first_name=rep_first_name,
            representative_last_name=rep_last_name,
            address=address,
            phone_mobile=phone_mobile,
            phone_landline=phone_landline,
            latitude=latitude,
            longitude=longitude,
            created_at=datetime.now(timezone.utc),
            last_submitted_at=datetime.now(timezone.utc),
            reapplication_count=1,
            fuzzy_match_warning=fuzzy_match_warning,
            similar_company_names=', '.join(similar_companies) if similar_companies else None
        )
        
        # Add categories to the application
        for category_name in service_categories:
            # Find or create category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
            new_app.categories.append(category)
        
        try:
            db.session.add(new_app)
            db.session.commit()
            
            # Log successful submission
            logger.info(
                f"Application submitted successfully: id={new_app.id}, "
                f"company='{company_name}', fuzzy_warning={fuzzy_match_warning}, ip={client_ip}"
            )

            response_data = {
                "success": True,
                "message": "درخواست شما با موفقیت ثبت شد",
                "data": {
                    "id": new_app.id,
                    "status": new_app.status
                }
            }
            
            # Add fuzzy match warning to response if applicable
            if fuzzy_match_warning:
                response_data["warning"] = {
                    "code": "SIMILAR_COMPANY_NAME",
                    "message": f"نام شرکت شما شباهت زیادی به شرکت‌های موجود در سیستم دارد: {', '.join(similar_companies[:2])}",
                    "note": "اگر این شرکت شما نیست، درخواست شما در حال بررسی است."
                }

            return jsonify(response_data), 201
            
        except IntegrityError as e:
            db.session.rollback()
            
            # This catches database-level unique constraint violations
            if 'phone_mobile' in str(e.orig):
                phone_hash = hashlib.sha256(phone_mobile.encode()).hexdigest()[:16]
                logger.error(
                    f"Database constraint violation (duplicate phone): phone_hash={phone_hash}, ip={client_ip}"
                )
                
                support_phone = current_app.config.get('SUPPORT_PHONE', '021-12345678')
                
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_PHONE",
                        "message": "این شماره موبایل قبلاً در سیستم ثبت شده است.",
                        "action": "لطفاً با شماره دیگری ثبت‌نام کنید یا با پشتیبانی تماس بگیرید.",
                        "support_contact": support_phone
                    }
                }), 409
            else:
                logger.error(f"Database integrity error: {str(e)}", exc_info=True)
                raise
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating provider application: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": "خطا در ثبت درخواست. لطفاً دوباره تلاش کنید."
            }
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
        
        # Query applications with eager loading of categories
        query = ProviderApplication.query.options(
            db.joinedload(ProviderApplication.categories)
        ).filter_by(status=status).order_by(
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
        # Use eager loading for categories
        app = ProviderApplication.query.options(
            db.joinedload(ProviderApplication.categories)
        ).get(app_id)
        
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
        # Use eager loading for categories
        app = ProviderApplication.query.options(
            db.joinedload(ProviderApplication.categories)
        ).get(app_id)
        
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

        # Check if company with this phone number already exists
        existing_company = Company.query.filter_by(phone_mobile=app.phone_mobile).first()
        
        if existing_company:
            # Update the existing company and link all categories
            for category in app.categories:
                if category not in existing_company.categories:
                    existing_company.categories.append(category)
        else:
            # Create a new company with all categories
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
            # Add all categories from the application
            for category in app.categories:
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
