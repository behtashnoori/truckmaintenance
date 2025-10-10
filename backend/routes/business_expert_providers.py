from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from pydantic import ValidationError
import pandas as pd
import io
import os
import tempfile
from ..app import db
from ..models.company import Company, Category
from ..models.provider_application import ProviderApplication
from ..middleware.security import token_required, business_expert_required, validate_input, sanitize_string, validate_phone
from ..middleware.redis_rate_limiting import file_upload_rate_limit
from ..services.company_service import CompanyService
from ..schemas.company import CompanyCreate, CompanyUpdate
from ..schemas.pagination import PaginationParams, PaginatedResponse
from backend.tasks import process_bulk_upload
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("business_expert_providers", __name__)


@bp.route("/business-expert/dashboard", methods=["GET"])
@token_required
@business_expert_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics for business expert"""
    try:
        # Get real statistics from database
        stats = {
            "pending_reviews": ProviderApplication.query.filter_by(status='pending').count(),
            "approved_today": ProviderApplication.query.filter(
                ProviderApplication.is_approved == True,
                ProviderApplication.reviewed_at >= datetime.now().date()
            ).count(),
            "monthly_revenue": "0",  # This would need a revenue tracking system
            "total_companies": Company.query.count(),
            "review_efficiency": 85,  # This would be calculated based on review times
            "customer_satisfaction": 92  # This would come from feedback system
        }
        
        return jsonify({
            "success": True,
            **stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/activities", methods=["GET"])
@token_required
@business_expert_required
def get_recent_activities(current_user):
    """Get recent activities for business expert"""
    try:
        # Get recent application reviews
        recent_applications = ProviderApplication.query.filter(
            ProviderApplication.reviewed_by == current_user.id
        ).order_by(ProviderApplication.reviewed_at.desc()).limit(10).all()
        
        activities = []
        for app in recent_applications:
            activities.append({
                "id": app.id,
                "company_name": app.company_name,
                "action": "درخواست تایید شد" if app.is_approved else "درخواست رد شد",
                "timestamp": app.reviewed_at.isoformat() if app.reviewed_at else app.created_at.isoformat(),
                "status": "approved" if app.is_approved else "rejected"
            })
        
        return jsonify({
            "success": True,
            "activities": activities
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recent activities: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/applications/<int:app_id>", methods=["GET"])
@token_required
@business_expert_required
def get_application_details(current_user, app_id):
    """Get application details for review"""
    try:
        application = ProviderApplication.query.get(app_id)
        if not application:
            return jsonify({
                "success": False,
                "error": "درخواست یافت نشد"
            }), 404
        
        app_data = {
            "id": application.id,
            "company_name": application.company_name,
            "representative_first_name": application.representative_first_name,
            "representative_last_name": application.representative_last_name,
            "address": application.address,
            "phone_mobile": application.phone_mobile,
            "phone_landline": application.phone_landline,
            "service_domain": application.service_domain,
            "latitude": application.latitude,
            "longitude": application.longitude,
            "status": application.status,
            "created_at": application.created_at.isoformat() if application.created_at else None,
            "is_approved": application.is_approved
        }
        
        return jsonify({
            "success": True,
            **app_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting application details: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/providers", methods=["GET"])
@token_required
@business_expert_required
def get_providers(current_user):
    """Get all providers for business expert management with pagination - Business Expert only"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_active = request.args.get('is_active', None, type=lambda v: v.lower() == 'true' if v else None)
        category_id = request.args.get('category_id', None, type=int)
        search = request.args.get('search', None, type=str)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Get providers from service
        providers, total = CompanyService.get_all_companies(
            pagination=pagination,
            is_active=is_active,
            category_id=category_id,
            search=search
        )
        
        # Build response
        providers_data = []
        for provider in providers:
            providers_data.append({
                "id": provider.id,
                "name": provider.name,
                "address": provider.address,
                "phone_mobile": provider.phone_mobile,
                "phone_landline": provider.phone_landline,
                "latitude": provider.latitude,
                "longitude": provider.longitude,
                "is_active": provider.is_active,
                "categories": [{"id": cat.id, "name": cat.name} for cat in provider.categories]
            })
        
        # Return paginated response
        response = PaginatedResponse.create(
            items=providers_data,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/providers", methods=["POST"])
@token_required
@business_expert_required
def create_provider(current_user):
    """Create a new provider directly by business expert"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400

        # Map fields from frontend format
        mapped_data = {
            "name": data.get("companyName"),
            "phone": data.get("phoneMobile"),
            "phone_landline": data.get("phoneLandline"),
            "address": data.get("address", ""),
            "latitude": data.get("latitude", 0.0),
            "longitude": data.get("longitude", 0.0),
            "is_active": data.get("isActive", True)
        }
        
        # Validate with Pydantic
        try:
            company_data = CompanyCreate(**mapped_data)
        except ValidationError as e:
            logger.warning(f"Validation error in provider creation: {e.errors()}")
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400
        
        # Create company using service
        company, error = CompanyService.create_company(company_data, current_user.id)
        
        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 400
        
        # Add category if provided
        service_domain = data.get("serviceDomain")
        if service_domain:
            CompanyService.add_category_to_company(company.id, service_domain)

        return jsonify({
            "success": True,
            "message": "ارائه‌دهنده با موفقیت ایجاد شد",
            "data": {"provider_id": company.id}
        }), 201

    except Exception as e:
        logger.error(f"Error creating provider: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/providers/<int:provider_id>/toggle-status", methods=["PATCH"])
@token_required
@business_expert_required
def toggle_provider_status(current_user, provider_id):
    """Toggle provider active status"""
    try:
        data = request.get_json(silent=True)
        
        if not data or "is_active" not in data:
            return jsonify({
                "success": False,
                "error": "فیلد is_active الزامی است"
            }), 400

        # Toggle status using service
        provider, error = CompanyService.toggle_company_status(provider_id, data["is_active"])
        
        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 404 if "یافت نشد" in error else 500
        
        return jsonify({
            "success": True,
            "message": f"ارائه‌دهنده با موفقیت {'فعال' if provider.is_active else 'غیرفعال'} شد"
        }), 200

    except Exception as e:
        logger.error(f"Error toggling provider status: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/providers/<int:provider_id>", methods=["DELETE"])
@token_required
@business_expert_required
def delete_provider(current_user, provider_id):
    """Delete a provider"""
    try:
        success, error = CompanyService.delete_company(provider_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": error
            }), 404 if "یافت نشد" in error else 500
        
        return jsonify({
            "success": True,
            "message": "ارائه‌دهنده با موفقیت حذف شد"
        }), 200

    except Exception as e:
        logger.error(f"Error deleting provider: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/business-expert/providers/template", methods=["GET"])
@token_required
@business_expert_required
def download_template(current_user):
    """Download Excel template for bulk upload"""
    try:
        # Create template data
        template_data = {
            'نام مجموعه': ['نام شرکت نمونه'],
            'نام نماینده': ['نام'],
            'نام خانوادگی نماینده': ['نام خانوادگی'],
            'آدرس': ['آدرس کامل شرکت'],
            'شماره موبایل': ['09123456789'],
            'تلفن ثابت': ['02112345678'],
            'حوزه خدمات': ['تعمیرات موتور'],
            'عرض جغرافیایی': [35.6892],
            'طول جغرافیایی': [51.3890],
            'وضعیت فعال': [True]
        }
        
        df = pd.DataFrame(template_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='ارائه‌دهندگان', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='template_providers.xlsx'
        )

    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def process_bulk_upload_sync(file_path, user_id):
    """Synchronous processing of bulk upload (fallback when Redis/Celery not available)"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        results = {
            'total': len(df),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        # Expected columns
        expected_columns = [
            'نام مجموعه', 'نام نماینده', 'نام خانوادگی نماینده',
            'آدرس', 'شماره موبایل', 'تلفن ثابت', 'حوزه خدمات',
            'عرض جغرافیایی', 'طول جغرافیایی', 'وضعیت فعال'
        ]
        
        # Check if all expected columns exist
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            return {
                'success': False,
                'error': f'Missing columns: {missing_columns}'
            }
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Convert phone numbers to string (Excel may read them as numbers)
                phone_mobile = str(int(row['شماره موبایل'])) if pd.notna(row['شماره موبایل']) else None
                phone_landline = str(int(row['تلفن ثابت'])) if pd.notna(row['تلفن ثابت']) else None
                
                # Get or create category
                category = Category.query.filter_by(name=row['حوزه خدمات']).first()
                if not category:
                    category = Category(name=row['حوزه خدمات'])
                    db.session.add(category)
                    db.session.flush()
                
                # Check if company with this phone already exists
                existing_company = Company.query.filter_by(phone_mobile=phone_mobile).first()
                
                if existing_company:
                    # Update existing company
                    if category not in existing_company.categories:
                        existing_company.categories.append(category)
                    results['success'] += 1
                else:
                    # Create new company
                    new_company = Company(
                        name=row['نام مجموعه'],
                        address=row['آدرس'],
                        phone_mobile=phone_mobile,
                        phone_landline=phone_landline,
                        latitude=float(row['عرض جغرافیایی']),
                        longitude=float(row['طول جغرافیایی']),
                        is_active=bool(row['وضعیت فعال']),
                        created_by=user_id
                    )
                    new_company.categories.append(category)
                    db.session.add(new_company)
                    results['success'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Row {index + 2}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            'success': True,
            'results': results
        }
        
    except Exception as e:
        db.session.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            'success': False,
            'error': str(e)
        }


@bp.route("/business-expert/providers/bulk-upload", methods=["POST"])
@token_required
@business_expert_required
def bulk_upload_providers(current_user):
    """Handle bulk upload of providers from Excel file with fallback to sync processing"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "فایلی ارسال نشده است"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "فایلی انتخاب نشده است"
            }), 400
        
        # Validate file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({
                "success": False,
                "error": "فرمت فایل نامعتبر است. لطفاً فایل Excel آپلود کنید (.xlsx یا .xls)"
            }), 400

        # Save file temporarily
        temp_dir = tempfile.gettempdir()
        temp_filename = f'bulk_upload_{current_user.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        temp_file_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_file_path)
        
        # Try to use Celery for background processing
        try:
            from ..celery_app import celery_app
            task = process_bulk_upload.delay(temp_file_path, current_user.id, None)
            
            return jsonify({
                "success": True,
                "message": "فایل با موفقیت آپلود شد. پردازش در پس‌زمینه شروع شد.",
                "data": {
                    "task_id": task.id,
                    "processing_mode": "async",
                    "status_url": f"/api/business-expert/providers/bulk-upload/status/{task.id}"
                }
            }), 202
            
        except Exception as celery_error:
            # Fallback to synchronous processing if Celery/Redis not available
            logger.warning(f"Celery not available, using sync processing: {celery_error}")
            result = process_bulk_upload_sync(temp_file_path, current_user.id)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "message": "فایل با موفقیت پردازش شد (حالت همزمان - Redis در دسترس نیست)",
                    "data": {
                        "processing_mode": "sync",
                        "results": result.get('results', {})
                    }
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": f"خطا در پردازش فایل: {result.get('error', 'خطای ناشناخته')}",
                    "data": {
                        "processing_mode": "sync"
                    }
                }), 500

    except Exception as e:
        # Clean up temp file if exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        logger.error(f"Error in bulk upload: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"خطا در آپلود فایل: {str(e)}"
        }), 500


@bp.route("/business-expert/providers/bulk-upload/status/<task_id>", methods=["GET"])
@token_required
@business_expert_required
def get_bulk_upload_status(current_user, task_id):
    """Get status of bulk upload task"""
    try:
        from ..celery_app import celery_app
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'success': True,
                'data': {
                    'state': task.state,
                    'status': 'در انتظار پردازش...',
                    'progress': 0
                }
            }
        elif task.state == 'PROGRESS':
            response = {
                'success': True,
                'data': {
                    'state': task.state,
                    'status': task.info.get('status', 'در حال پردازش...'),
                    'progress': task.info.get('progress', 0)
                }
            }
        elif task.state == 'SUCCESS':
            response = {
                'success': True,
                'data': {
                    'state': task.state,
                    'result': task.result,
                    'status': 'پردازش با موفقیت انجام شد'
                }
            }
        else:
            response = {
                'success': False,
                'data': {
                    'state': task.state,
                    'result': task.result,
                    'status': 'پردازش با خطا مواجه شد'
                }
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting bulk upload status: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
