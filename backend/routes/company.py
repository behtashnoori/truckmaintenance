from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..middleware.security import token_required, business_expert_required
from ..middleware.logging import log_security_event
from ..services.company_service import CompanyService
from ..schemas.company import CompanyCreate
from ..schemas.response import ApiResponse, ErrorResponse
import logging

# Configure logger
logger = logging.getLogger(__name__)

bp = Blueprint("company", __name__)


@bp.route("/company", methods=["POST"])
@token_required
@business_expert_required
def create_company(current_user):
    """
    Create company (business expert only)
    Request body (with validation):
    {
        "phone": "09xxxxxxxxx",  // or "tel"
        "name": "نام شرکت"  // or "companyName"
    }
    """
    try:
        data = request.get_json(silent=True)
        
        # Check if JSON is valid
        if data is None:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400
        
        # Log company creation attempt
        logger.info(f"Company creation attempt by user {current_user.id} ({current_user.username})")
        
        # Handle legacy field names
        if 'companyName' in data and 'name' not in data:
            data['name'] = data['companyName']
        if 'tel' in data and 'phone' not in data:
            data['phone'] = data['tel']
        
        # Validate with Pydantic
        try:
            company_data = CompanyCreate(**data)
        except ValidationError as e:
            logger.warning(f"Validation error in company creation: {e.errors()}")
            # Convert Pydantic errors to JSON-serializable format
            errors = []
            for error in e.errors():
                errors.append({
                    'field': error.get('loc', [''])[0] if error.get('loc') else '',
                    'message': str(error.get('msg', '')),
                    'type': error.get('type', '')
                })
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": errors
            }), 400
        
        # Create company using service
        company, error = CompanyService.create_company(company_data, current_user.id)
        
        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 409 if "قبلاً ثبت شده" in error else 500
        
        # Log successful creation
        log_security_event(
            'company_created',
            f'Company created: {company.name}',
            user_id=current_user.id,
            additional_data={'company_id': company.id, 'company_name': company.name}
        )
        
        return jsonify({
            "success": True,
            "message": "شرکت با موفقیت ایجاد شد",
            "data": {"id": company.id}
        }), 201
        
    except Exception as e:
        logger.error(f"Unexpected error creating company: {str(e)}", exc_info=True)
        log_security_event(
            'company_creation_error',
            f'Error creating company: {str(e)}',
            user_id=current_user.id,
            additional_data={'error': str(e)}
        )
        return jsonify({
            "success": False,
            "error": "خطای سرور در ایجاد شرکت"
        }), 500
