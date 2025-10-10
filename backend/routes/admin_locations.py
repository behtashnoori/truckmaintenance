"""
Admin Routes for Location Management
مدیریت استان‌ها، شهرستان‌ها و شهرها توسط ادمین
"""

from flask import Blueprint, jsonify, request
from backend.app import db
from backend.models.location import Location
from backend.middleware.security import token_required, admin_required
from backend.schemas.pagination import PaginationParams, PaginatedResponse
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin_locations', __name__)


@bp.route('/locations', methods=['GET'])
@token_required
@admin_required
def get_locations(current_user):
    """دریافت لیست تمام locations با pagination"""
    try:
        # Parse parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        location_type = request.args.get('type', None, type=str)
        parent_id = request.args.get('parent_id', None, type=int)
        search = request.args.get('search', None, type=str)
        include_inactive = request.args.get('include_inactive', 'false', type=str).lower() == 'true'
        
        # Build query
        query = Location.query
        
        # Filter by type
        if location_type:
            query = query.filter(Location.type == location_type)
        
        # Filter by parent
        if parent_id is not None:
            query = query.filter(Location.parent_id == parent_id)
        
        # Filter by active status
        if not include_inactive:
            query = query.filter(Location.is_active == True)
        
        # Search
        if search:
            query = query.filter(Location.name.ilike(f'%{search}%'))
        
        # Order by type and name
        query = query.order_by(Location.type, Location.name)
        
        # Pagination
        total = query.count()
        locations = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict
        result = [loc.to_dict(include_children=True) for loc in locations]
        
        # Create paginated response
        response = PaginatedResponse.create(
            items=result,
            page=page,
            per_page=per_page,
            total=total
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت لیست مکان‌ها'
        }), 500


@bp.route('/locations/<int:location_id>', methods=['GET'])
@token_required
@admin_required
def get_location(current_user, location_id):
    """دریافت جزئیات یک location"""
    try:
        location = Location.query.get(location_id)
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'مکان یافت نشد'
            }), 404
        
        return jsonify({
            'success': True,
            'data': location.to_dict(include_children=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting location: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت اطلاعات مکان'
        }), 500


@bp.route('/locations', methods=['POST'])
@token_required
@admin_required
def create_location(current_user):
    """ایجاد location جدید"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'نام مکان الزامی است'
            }), 400
        
        if not data.get('type'):
            return jsonify({
                'success': False,
                'error': 'نوع مکان الزامی است'
            }), 400
        
        if data['type'] not in ['province', 'county', 'city']:
            return jsonify({
                'success': False,
                'error': 'نوع مکان باید یکی از province، county یا city باشد'
            }), 400
        
        if data.get('latitude') is None or data.get('longitude') is None:
            return jsonify({
                'success': False,
                'error': 'مختصات جغرافیایی الزامی است'
            }), 400
        
        # Check for duplicate name
        existing = Location.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'مکانی با این نام قبلاً ثبت شده است'
            }), 400
        
        # Create location
        location = Location(
            name=data['name'],
            type=data['type'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            parent_id=data.get('parent_id'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(location)
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} created location: {location.name}")
        
        return jsonify({
            'success': True,
            'data': location.to_dict(),
            'message': 'مکان با موفقیت ایجاد شد'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating location: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در ایجاد مکان'
        }), 500


@bp.route('/locations/<int:location_id>', methods=['PUT'])
@token_required
@admin_required
def update_location(current_user, location_id):
    """بروزرسانی location"""
    try:
        location = Location.query.get(location_id)
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'مکان یافت نشد'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            # Check for duplicate name
            existing = Location.query.filter(
                Location.name == data['name'],
                Location.id != location_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'مکانی با این نام قبلاً ثبت شده است'
                }), 400
            location.name = data['name']
        
        if 'type' in data:
            if data['type'] not in ['province', 'county', 'city']:
                return jsonify({
                    'success': False,
                    'error': 'نوع مکان باید یکی از province، county یا city باشد'
                }), 400
            location.type = data['type']
        
        if 'latitude' in data:
            location.latitude = float(data['latitude'])
        
        if 'longitude' in data:
            location.longitude = float(data['longitude'])
        
        if 'parent_id' in data:
            location.parent_id = data['parent_id']
        
        if 'is_active' in data:
            location.is_active = data['is_active']
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} updated location: {location.name}")
        
        return jsonify({
            'success': True,
            'data': location.to_dict(),
            'message': 'مکان با موفقیت بروزرسانی شد'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating location: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در بروزرسانی مکان'
        }), 500


@bp.route('/locations/<int:location_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_location(current_user, location_id):
    """حذف (غیرفعال کردن) location"""
    try:
        location = Location.query.get(location_id)
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'مکان یافت نشد'
            }), 404
        
        # Soft delete - just deactivate
        location.is_active = False
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} deleted location: {location.name}")
        
        return jsonify({
            'success': True,
            'message': 'مکان با موفقیت حذف شد'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting location: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در حذف مکان'
        }), 500


@bp.route('/locations/hierarchy', methods=['GET'])
@token_required
@admin_required
def get_locations_hierarchy(current_user):
    """دریافت ساختار سلسله‌مراتبی locations (استان → شهرستان → شهر)"""
    try:
        # Get all provinces (top level)
        provinces = Location.query.filter_by(type='province', parent_id=None, is_active=True).order_by(Location.name).all()
        
        result = []
        for province in provinces:
            province_data = province.to_dict(include_children=False)
            
            # Get counties for this province
            counties = Location.query.filter_by(type='county', parent_id=province.id, is_active=True).order_by(Location.name).all()
            province_data['counties'] = []
            
            for county in counties:
                county_data = county.to_dict(include_children=False)
                
                # Get cities for this county
                cities = Location.query.filter_by(type='city', parent_id=county.id, is_active=True).order_by(Location.name).all()
                county_data['cities'] = [city.to_dict(include_children=False) for city in cities]
                
                province_data['counties'].append(county_data)
            
            result.append(province_data)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting location hierarchy: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت ساختار سلسله‌مراتبی'
        }), 500

