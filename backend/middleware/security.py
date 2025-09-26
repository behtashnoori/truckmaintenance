"""
Security middleware for authentication and authorization
"""
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import datetime
from ..models.user import User

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
            if not current_user.is_active:
                return jsonify({'message': 'Account is deactivated'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def business_expert_required(f):
    """Decorator to require business expert role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role not in ['admin', 'business_expert']:
            return jsonify({'message': 'Business expert access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def validate_input(required_fields=None, allowed_fields=None):
    """Decorator to validate input data"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                
                # Check required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
                
                # Check allowed fields (prevent extra fields)
                if allowed_fields:
                    extra_fields = [field for field in data.keys() if field not in allowed_fields]
                    if extra_fields:
                        return jsonify({'error': f'Extra fields not allowed: {extra_fields}'}), 400
                
                # Basic XSS protection
                for key, value in data.items():
                    if isinstance(value, str):
                        # Remove potentially dangerous characters
                        data[key] = value.replace('<', '&lt;').replace('>', '&gt;')
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def sanitize_string(value):
    """Sanitize string input to prevent XSS"""
    if not isinstance(value, str):
        return value
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', 'script', 'javascript', 'onload', 'onerror']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value.strip()

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    import re
    # Iranian phone number format
    pattern = r'^09\d{9}$'
    return re.match(pattern, phone) is not None
