from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import pandas as pd
import io
import os
import tempfile
from ..app import db
from ..models.company import Company, Category
from ..models.provider_application import ProviderApplication
from ..middleware.security import token_required, business_expert_required, validate_input, sanitize_string, validate_phone
from ..middleware.redis_rate_limiting import file_upload_rate_limit
from backend.tasks import process_bulk_upload

bp = Blueprint("business_expert_providers", __name__)


@bp.route("/business-expert/providers", methods=["GET"])
@token_required
@business_expert_required
def get_providers(current_user):
    """Get all providers for business expert management - Business Expert only"""
    try:
        providers = Company.query.filter_by(is_active=True).all()
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
        
        return jsonify({"providers": providers_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/business-expert/providers", methods=["POST"])
@token_required
@business_expert_required
@validate_input(required_fields=[
    "companyName", "representativeFirstName", "representativeLastName",
    "address", "phoneMobile", "serviceDomain", "latitude", "longitude"
], allowed_fields=[
    "companyName", "representativeFirstName", "representativeLastName",
    "address", "phoneMobile", "phoneLandline", "serviceDomain",
    "latitude", "longitude", "isActive"
])
def create_provider(current_user):
    """Create a new provider directly by business expert"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        # Sanitize and basic validate
        company_name = sanitize_string(str(data["companyName"]))
        address = sanitize_string(str(data["address"]))
        phone_mobile = str(data["phoneMobile"]).strip()
        phone_landline = str(data.get("phoneLandline")).strip() if data.get("phoneLandline") else None
        service_domain = sanitize_string(str(data["serviceDomain"]))
        latitude = float(data["latitude"]) 
        longitude = float(data["longitude"]) 

        if not validate_phone(phone_mobile):
            return jsonify({"error": "Invalid mobile phone format"}), 400

        # Check if company with this phone number already exists
        existing_company = Company.query.filter_by(phone_mobile=phone_mobile).first()
        if existing_company:
            return jsonify({"error": "Company with this phone number already exists"}), 400

        # Get or create category
        category = Category.query.filter_by(name=service_domain).first()
        if not category:
            category = Category(name=service_domain)
            db.session.add(category)
            db.session.flush()  # Get the ID

        # Create new company
        new_company = Company(
            name=company_name,
            address=address,
            phone_mobile=phone_mobile,
            phone_landline=phone_landline,
            latitude=latitude,
            longitude=longitude,
            is_active=bool(data.get("isActive", True))
        )
        
        new_company.categories.append(category)
        db.session.add(new_company)
        db.session.commit()

        return jsonify({
            "message": "Provider created successfully",
            "provider_id": new_company.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/business-expert/providers/<int:provider_id>/toggle-status", methods=["PATCH"])
@token_required
@business_expert_required
@validate_input(required_fields=["is_active"], allowed_fields=["is_active"])
def toggle_provider_status(current_user, provider_id):
    """Toggle provider active status"""
    try:
        provider = Company.query.get_or_404(provider_id)
        data = request.get_json()

        if "is_active" in data:
            provider.is_active = data["is_active"]
            db.session.commit()
            
            return jsonify({
                "message": f"Provider {'activated' if provider.is_active else 'deactivated'} successfully"
            }), 200
        else:
            return jsonify({"error": "is_active field is required"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/business-expert/providers/<int:provider_id>", methods=["DELETE"])
@token_required
@business_expert_required
def delete_provider(current_user, provider_id):
    """Delete a provider"""
    try:
        provider = Company.query.get_or_404(provider_id)
        db.session.delete(provider)
        db.session.commit()
        
        return jsonify({"message": "Provider deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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
            df.to_excel(writer, sheet_name='ارائه\u200cدهندگان', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='template_providers.xlsx'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/business-expert/providers/bulk-upload", methods=["POST"])
@token_required
@business_expert_required
@file_upload_rate_limit(max_uploads=5, window_hours=1)
def bulk_upload_providers(current_user):
    """Handle bulk upload of providers from Excel file using background processing"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save file temporarily
        temp_dir = tempfile.gettempdir()
        temp_filename = f'bulk_upload_{current_user.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        temp_file_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_file_path)
        
        # Start background task
        task = process_bulk_upload.delay(temp_file_path, current_user.id, None)
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully. Processing started in background.",
            "task_id": task.id,
            "status_url": f"/api/business-expert/providers/bulk-upload/status/{task.id}"
        }), 202

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error uploading file: {str(e)}"
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
                'state': task.state,
                'status': 'Task is waiting to be processed...',
                'progress': 0
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'status': task.info.get('status', 'Processing...'),
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'result': task.result,
                'status': 'Task completed successfully'
            }
        else:
            response = {
                'state': task.state,
                'result': task.result,
                'status': 'Task failed'
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
