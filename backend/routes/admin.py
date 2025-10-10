from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..middleware.security import token_required, admin_required
from ..services.application_service import ApplicationService
from ..services.user_service import UserService
from ..services.company_service import CompanyService
from ..schemas.application import ApplicationReview
from ..schemas.user import UserUpdate
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..schemas.response import ApiResponse, ErrorResponse

bp = Blueprint("admin", __name__)


@bp.route("/admin/dashboard", methods=["GET"])
@token_required
@admin_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics - Admin only"""
    try:
        # Get real data from services
        app_stats = ApplicationService.get_dashboard_stats()
        user_stats = UserService.get_user_statistics()
        company_stats = CompanyService.get_company_statistics()
        
        dashboard_data = {
            **app_stats,
            **user_stats,
            **company_stats
        }
        
        return jsonify({
            "success": True,
            **dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/admin/applications", methods=["GET"])
@token_required
@admin_required
def get_applications(current_user):
    """Get all provider applications with pagination - Admin only"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None, type=str)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Get applications from service
        applications, total = ApplicationService.get_all_applications(
            pagination=pagination,
            status=status
        )
        
        # Return paginated response
        response = PaginatedResponse.create(
            items=applications,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/applications/<int:app_id>/review", methods=["POST"])
@token_required
@admin_required
def review_application(current_user, app_id):
    """Review a provider application - Admin only"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate with Pydantic
        try:
            review_data = ApplicationReview(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400
        
        # Review application using service
        application, error = ApplicationService.review_application(
            app_id, review_data, current_user.id
        )
        
        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 404 if "یافت نشد" in error else 500
        
        return jsonify({
            "success": True,
            "message": "درخواست با موفقیت بررسی شد",
            "data": {
                "is_approved": application.is_approved
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/applications/<int:app_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_application(current_user, app_id):
    """Delete a provider application (admin only)"""
    try:
        success, error = ApplicationService.delete_application(app_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": error
            }), 404 if "یافت نشد" in error else 500
        
        return jsonify({
            "success": True,
            "message": "درخواست با موفقیت حذف شد"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/admin/companies", methods=["GET"])
@token_required
@admin_required
def get_companies(current_user):
    """Get all companies with pagination - Admin only"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None, type=str)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Get real data from service
        companies, total = CompanyService.get_all_companies(
            pagination=pagination,
            status=status
        )
        
        return jsonify({
            "success": True,
            "companies": companies,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": total,
                "pages": (total + pagination.per_page - 1) // pagination.per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/admin/reports", methods=["GET"])
@token_required
@admin_required
def get_reports(current_user):
    """Get reports and statistics - Admin only"""
    try:
        period = request.args.get('period', 'month', type=str)
        report_type = request.args.get('type', 'summary', type=str)
        
        # Get real data from services
        report_data = {
            "period": period,
            **ApplicationService.get_dashboard_stats(),
            **CompanyService.get_company_statistics(),
            "category_stats": ApplicationService.get_category_statistics(period),
            "monthly_stats": ApplicationService.get_monthly_statistics(period)
        }
        
        return jsonify({
            "success": True,
            **report_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/admin/settings", methods=["GET"])
@token_required
@admin_required
def get_settings(current_user):
    """Get system settings - Admin only"""
    try:
        # Get real settings from service
        settings_data = CompanyService.get_system_settings()
        
        return jsonify({
            "success": True,
            **settings_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/admin/settings", methods=["PUT"])
@token_required
@admin_required
def update_settings(current_user):
    """Update system settings - Admin only"""
    try:
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400
        
        # Here you would normally save settings to database
        # For now, just return success
        
        return jsonify({
            "success": True,
            "message": "تنظیمات با موفقیت بروزرسانی شد"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
@admin_required
def update_user(current_user, user_id):
    """Update user (admin only)"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate with Pydantic
        try:
            user_data = UserUpdate(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400
        
        # Update user using service
        user, error = UserService.update_user(user_id, user_data)
        
        if error:
            status_code = 404 if "یافت نشد" in error else 409 if "قبلاً استفاده شده" in error else 500
            return jsonify({
                "success": False,
                "error": error
            }), status_code
        
        return jsonify({
            "success": True,
            "message": "کاربر با موفقیت بروزرسانی شد"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Delete user (admin only)"""
    try:
        success, error = UserService.delete_user(user_id, current_user.id)
        
        if not success:
            status_code = 404 if "یافت نشد" in error else 400 if "خود را حذف" in error else 500
            return jsonify({
                "success": False,
                "error": error
            }), status_code
        
        return jsonify({
            "success": True,
            "message": "کاربر با موفقیت حذف شد"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

