"""
Public API Routes - بدون نیاز به احراز هویت
این endpoint ها برای دسترسی عمومی کاربران است
"""

from flask import Blueprint, jsonify, request
from backend.app import db
from backend.models.company import Company, Category
from backend.models.location import Location
from backend.services.company_service import CompanyService
from backend.schemas.pagination import PaginationParams, PaginatedResponse
from sqlalchemy import func, or_
import math
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('public', __name__)


@bp.route('/locations', methods=['GET'])
def get_locations():
    """دریافت لیست استان‌ها و شهرهای اصلی"""
    try:
        # دریافت تمام locations فعال از دیتابیس
        locations = Location.query.filter_by(is_active=True).order_by(Location.name).all()
        
        # تبدیل به فرمت مورد نیاز
        result = [loc.to_dict() for loc in locations]
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت لیست استان‌ها'
        }), 500


@bp.route('/providers', methods=['GET'])
def get_providers():
    """دریافت لیست ارائه‌دهندگان بر اساس موقعیت و فیلترها"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        category = request.args.get('category')
        vehicle = request.args.get('vehicle')
        
        if not lat or not lon:
            return jsonify({
                'success': False,
                'error': 'موقعیت جغرافیایی الزامی است'
            }), 400
        
        # Query companies with location filtering
        query = Company.query.filter(Company.is_active == True)
        
        if category:
            # Filter by category if provided
            query = query.join(Company.categories).filter(Category.name == category)
        
        companies = query.all()
        
        # Calculate distances and filter by radius
        results = []
        for company in companies:
            # Calculate distance (simplified - in production use proper geospatial queries)
            distance_km = CompanyService.calculate_distance(lat, lon, company.latitude, company.longitude)
            
            if distance_km <= company.service_radius_km:
                # Filter by vehicle type if specified
                if vehicle and company.vehicle_types and vehicle not in company.vehicle_types:
                    continue
                    
                results.append({
                    'id': company.id,
                    'name': company.company_name,
                    'phone': company.phone_mobile,
                    'address': company.address,
                    'distance_km': round(distance_km, 1),
                    'is_24_7': company.is_24_7,
                    'vehicle_types': company.vehicle_types or [],
                    'radius_km': company.service_radius_km,
                    'categories': [cat.name for cat in company.categories]
                })
        
        # Sort by distance
        results.sort(key=lambda x: x['distance_km'])
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت ارائه‌دهندگان'
        }), 500


@bp.route('/providers/<int:provider_id>', methods=['GET'])
def get_provider_detail(provider_id):
    """دریافت جزئیات ارائه‌دهنده"""
    try:
        company = Company.query.filter(
            Company.id == provider_id,
            Company.is_active == True
        ).first()
        
        if not company:
            return jsonify({
                'success': False,
                'error': 'ارائه‌دهنده یافت نشد'
            }), 404
        
        result = {
            'id': company.id,
            'name': company.company_name,
            'phone': company.phone_mobile,
            'address': company.address,
            'categories': [cat.name for cat in company.categories],
            'location': {
                'lat': company.latitude,
                'lon': company.longitude
            },
            'radius_km': company.service_radius_km,
            'is_24_7': company.is_24_7,
            'vehicle_types': company.vehicle_types or [],
            'description': company.description or '',
            'services': company.services or '',
            'working_hours': company.working_hours or ''
        }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting provider detail: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت جزئیات ارائه‌دهنده'
        }), 500


@bp.route('/categories', methods=['GET'])
def get_categories():
    """دریافت لیست تمام دسته‌بندی‌های فعال"""
    try:
        categories = Category.query.order_by(Category.name).all()
        
        result = []
        for cat in categories:
            # تعداد شرکت‌های فعال در هر دسته
            company_count = db.session.query(func.count(Company.id)).join(
                Company.categories
            ).filter(
                Category.id == cat.id,
                Company.is_active == True
            ).scalar() or 0
            
            result.append({
                'id': cat.id,
                'name': cat.name,
                'companies_count': company_count
            })
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت دسته‌بندی‌ها'
        }), 500


@bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    """دریافت اطلاعات یک دسته‌بندی با ID"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({
                'success': False,
                'error': 'دسته‌بندی یافت نشد'
            }), 404
        
        # تعداد شرکت‌های فعال
        company_count = db.session.query(func.count(Company.id)).join(
            Company.categories
        ).filter(
            Category.id == category.id,
            Company.is_active == True
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'id': category.id,
                'name': category.name,
                'company_count': company_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting category: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'خطا در دریافت دسته‌بندی'
        }), 500






def calculate_distance(lat1, lon1, lat2, lon2):
    """
    محاسبه فاصله بین دو نقطه با استفاده از فرمول Haversine
    برگشت فاصله به کیلومتر
    """
    # شعاع زمین به کیلومتر
    R = 6371
    
    # تبدیل به رادیان
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # فرمول Haversine
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance


@bp.route('/health', methods=['GET'])
def health():
    """بررسی سلامت API"""
    try:
        # بررسی ارتباط با دیتابیس
        db.session.execute(db.text('SELECT 1'))
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'ok',
                'message': 'API is running',
                'database': 'connected'
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'API health check failed',
            'details': {
                'database': 'disconnected'
            }
        }), 500
