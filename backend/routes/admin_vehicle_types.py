"""
Admin Routes for Vehicle Type Management
مدیریت انواع وسایل نقلیه توسط ادمین
"""

from flask import Blueprint, jsonify, request
from backend.app import db
from backend.models.vehicle_type import VehicleType
from backend.middleware.security import token_required, admin_required
from backend.schemas.pagination import PaginationParams, PaginatedResponse
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin_vehicle_types', __name__, url_prefix='/vehicle-types')


@bp.route('/vehicle-types', methods=['GET'])
@token_required
@admin_required
def get_vehicle_types(current_user):
    """دریافت لیست تمام انواع وسایل نقلیه"""
    try:
        # Parse parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', None, type=str)
        include_inactive = request.args.get('include_inactive', 'false', type=str).lower() == 'true'
        
        # Build query
        query = VehicleType.query
        
        # Filter by active status
        if not include_inactive:
            query = query.filter(VehicleType.is_active == True)
        
        # Search
        if search:
            query = query.filter(
                or_(
                    VehicleType.name.ilike(f'%{search}%'),
                    VehicleType.name_en.ilike(f'%{search}%')
                )
            )
        
        # Order by name
        query = query.order_by(VehicleType.name)
        
        # Pagination
        total = query.count()
        vehicle_types = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict
        result = [vt.to_dict() for vt in vehicle_types]
        
        # Create paginated response
        response = PaginatedResponse.create(
            items=result,
            page=page,
            per_page=per_page,
            total=total
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting vehicle types: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت لیست انواع وسایل نقلیه'
        }), 500


@bp.route('/<int:vehicle_type_id>', methods=['GET'])
@token_required
@admin_required
def get_vehicle_type(current_user, vehicle_type_id):
    """دریافت جزئیات یک نوع وسیله نقلیه"""
    try:
        vehicle_type = VehicleType.query.get(vehicle_type_id)
        
        if not vehicle_type:
            return jsonify({
                'success': False,
                'error': 'نوع وسیله نقلیه یافت نشد'
            }), 404
        
        return jsonify({
            'success': True,
            'data': vehicle_type.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting vehicle type: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت اطلاعات نوع وسیله نقلیه'
        }), 500


@bp.route('', methods=['POST'])
@token_required
@admin_required
def create_vehicle_type(current_user):
    """ایجاد نوع وسیله نقلیه جدید"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'نام فارسی الزامی است'
            }), 400
        
        if not data.get('name_en'):
            return jsonify({
                'success': False,
                'error': 'نام انگلیسی الزامی است'
            }), 400
        
        # Check for duplicates
        existing = VehicleType.query.filter(
            or_(
                VehicleType.name == data['name'],
                VehicleType.name_en == data['name_en']
            )
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'نوع وسیله نقلیه با این نام قبلاً ثبت شده است'
            }), 400
        
        # Create vehicle type
        vehicle_type = VehicleType(
            name=data['name'],
            name_en=data['name_en'],
            description=data.get('description'),
            icon=data.get('icon'),
            capacity_min=data.get('capacity_min'),
            capacity_max=data.get('capacity_max'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(vehicle_type)
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} created vehicle type: {vehicle_type.name}")
        
        return jsonify({
            'success': True,
            'data': vehicle_type.to_dict(),
            'message': 'نوع وسیله نقلیه با موفقیت ایجاد شد'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating vehicle type: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در ایجاد نوع وسیله نقلیه'
        }), 500


@bp.route('/<int:vehicle_type_id>', methods=['PUT'])
@token_required
@admin_required
def update_vehicle_type(current_user, vehicle_type_id):
    """بروزرسانی نوع وسیله نقلیه"""
    try:
        vehicle_type = VehicleType.query.get(vehicle_type_id)
        
        if not vehicle_type:
            return jsonify({
                'success': False,
                'error': 'نوع وسیله نقلیه یافت نشد'
            }), 404
        
        data = request.get_json()
        
        # Check for duplicate names
        if 'name' in data or 'name_en' in data:
            query = VehicleType.query.filter(VehicleType.id != vehicle_type_id)
            if 'name' in data:
                query = query.filter(VehicleType.name == data['name'])
            if 'name_en' in data:
                query = query.filter(VehicleType.name_en == data['name_en'])
            
            if query.first():
                return jsonify({
                    'success': False,
                    'error': 'نوع وسیله نقلیه با این نام قبلاً ثبت شده است'
                }), 400
        
        # Update fields
        if 'name' in data:
            vehicle_type.name = data['name']
        if 'name_en' in data:
            vehicle_type.name_en = data['name_en']
        if 'description' in data:
            vehicle_type.description = data['description']
        if 'icon' in data:
            vehicle_type.icon = data['icon']
        if 'capacity_min' in data:
            vehicle_type.capacity_min = data['capacity_min']
        if 'capacity_max' in data:
            vehicle_type.capacity_max = data['capacity_max']
        if 'is_active' in data:
            vehicle_type.is_active = data['is_active']
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} updated vehicle type: {vehicle_type.name}")
        
        return jsonify({
            'success': True,
            'data': vehicle_type.to_dict(),
            'message': 'نوع وسیله نقلیه با موفقیت بروزرسانی شد'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating vehicle type: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در بروزرسانی نوع وسیله نقلیه'
        }), 500


@bp.route('/<int:vehicle_type_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_vehicle_type(current_user, vehicle_type_id):
    """حذف (غیرفعال کردن) نوع وسیله نقلیه"""
    try:
        vehicle_type = VehicleType.query.get(vehicle_type_id)
        
        if not vehicle_type:
            return jsonify({
                'success': False,
                'error': 'نوع وسیله نقلیه یافت نشد'
            }), 404
        
        # Soft delete
        vehicle_type.is_active = False
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} deleted vehicle type: {vehicle_type.name}")
        
        return jsonify({
            'success': True,
            'message': 'نوع وسیله نقلیه با موفقیت حذف شد'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting vehicle type: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در حذف نوع وسیله نقلیه'
        }), 500

