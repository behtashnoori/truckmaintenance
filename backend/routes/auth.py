from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from ..app import db
from ..models.user import User, Admin, SupportSpecialist
from ..middleware.security import token_required, admin_required, validate_input, sanitize_string, validate_email
from ..middleware.rate_limiting import rate_limit, login_rate_limit
from ..middleware.logging import log_authentication_attempts, log_security_event
from ..services.user_service import UserService
from ..schemas.user import UserLogin, UserRegister, UserResponse
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..schemas.response import ApiResponse, ErrorResponse
import jwt
import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
@login_rate_limit(max_attempts=5, window_minutes=15)
@log_authentication_attempts
def login():
    """User login with JWT token"""
    try:
        data = request.get_json(silent=True)
        
        # Check if JSON is valid
        if data is None:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400
        
        # Validate with Pydantic
        try:
            login_data = UserLogin(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400
        
        # Authenticate user using service
        user = UserService.authenticate(login_data.username, login_data.password)
        
        if not user:
            return jsonify({
                "success": False,
                "error": "نام کاربری یا رمز عبور نادرست است"
            }), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "success": True,
            "message": "ورود موفقیت‌آمیز بود",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطای سرور"
        }), 500


@bp.route("/logout", methods=["POST"])
def logout():
    """User logout (client should remove token)"""
    return jsonify({
        "success": True,
        "message": "خروج موفقیت‌آمیز بود"
    }), 200


@bp.route("/me", methods=["GET"])
def get_current_user():
    """Get current user info - requires JWT token"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]  # Bearer <token>
        except IndexError:
            return jsonify({
                'success': False,
                'error': 'فرمت توکن نامعتبر است'
            }), 401
    
    if not token:
        return jsonify({
            'success': False,
            'error': 'توکن وجود ندارد'
        }), 401
    
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = UserService.get_user_by_id(data['user_id'])
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'error': 'کاربر یافت نشد یا غیرفعال است'
            }), 401
        
        return jsonify({
            "success": True,
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            'success': False,
            'error': 'توکن منقضی شده است'
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            'success': False,
            'error': 'توکن نامعتبر است'
        }), 401
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطای سرور"
        }), 500


@bp.route("/users", methods=["GET"])
@token_required
@admin_required
def get_users(current_user):
    """Get all users with pagination (admin only)"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role', None, type=str)
        is_active = request.args.get('is_active', None, type=lambda v: v.lower() == 'true' if v else None)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Get users from service
        users, total = UserService.get_all_users(
            pagination=pagination,
            role=role,
            is_active=is_active
        )
        
        # Build response
        users_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "additional_info": None
            }
            
            # Add role-specific information
            if user.role == 'admin' and user.admin:
                user_data["additional_info"] = {"permissions": user.admin.permissions}
            elif user.role == 'support' and user.support_specialist:
                user_data["additional_info"] = {
                    "department": user.support_specialist.department,
                    "max_applications": user.support_specialist.max_applications
                }
            
            users_list.append(user_data)
        
        # Return paginated response
        response = PaginatedResponse.create(
            items=users_list,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        # Add 'users' key for compatibility with tests
        response['users'] = response['data']
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Get users error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/users", methods=["POST"])
@token_required
@admin_required
def create_user(current_user):
    """Create new user (admin only)"""
    try:
        data = request.get_json(silent=True)
        
        # Check if JSON is valid
        if data is None:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400
        
        role = data.get("role", "").strip()
        
        if role not in ['admin', 'business_expert', 'support', 'user']:
            return jsonify({
                "success": False,
                "error": "نقش نامعتبر است"
            }), 400
        
        # Validate with Pydantic
        try:
            user_data = UserRegister(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400
        
        # Create user using service
        user, error = UserService.create_user(user_data, role)
        
        if error:
            status_code = 409 if "قبلاً استفاده شده" in error else 500
            return jsonify({
                "success": False,
                "error": error
            }), status_code
        
        # Create role-specific record
        try:
            if role == 'admin':
                admin = Admin(user_id=user.id, permissions={"all": True})
                db.session.add(admin)
            elif role == 'support':
                department = data.get("department", "")
                max_applications = data.get("max_applications", 50)
                support = SupportSpecialist(
                    user_id=user.id,
                    department=department,
                    max_applications=max_applications
                )
                db.session.add(support)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating role-specific record: {str(e)}", exc_info=True)
        
        return jsonify({
            "success": True,
            "message": "کاربر با موفقیت ایجاد شد",
            "data": {"user_id": user.id}
        }), 201
        
    except Exception as e:
        logger.error(f"Create user error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطای سرور"
        }), 500
