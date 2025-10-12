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

def sanitize_phone(phone):
    """Sanitize phone number by removing spaces, dashes, and other non-digit characters"""
    if not isinstance(phone, str):
        return phone
    
    # Remove all non-digit characters
    sanitized = ''.join(filter(str.isdigit, phone))
    
    # Handle +98 country code (convert to 0)
    if sanitized.startswith('98') and len(sanitized) == 12:
        sanitized = '0' + sanitized[2:]
    
    return sanitized

def validate_phone(phone):
    """Validate Iranian phone number format"""
    import re
    
    # First sanitize the phone number
    phone = sanitize_phone(phone)
    
    # Iranian mobile phone format (09XXXXXXXXX)
    pattern = r'^09\d{9}$'
    
    if not re.match(pattern, phone):
        return False
    
    # Additional validation: check for invalid patterns
    # Reject phones with all same digits (e.g., 09111111111)
    if len(set(phone[2:])) == 1:  # All digits after 09 are the same
        return False
    
    # Reject known test/invalid patterns
    invalid_patterns = [
        '09000000000',
        '09999999999',
        '09123456789',  # Common test number
    ]
    
    if phone in invalid_patterns:
        return False
    
    return True

def validate_company_name(company_name):
    """Validate company name for suspicious patterns"""
    if not isinstance(company_name, str):
        return False
    
    name = company_name.strip()
    
    # Check minimum and maximum length
    if len(name) < 2 or len(name) > 255:
        return False
    
    # Check for excessive repeated characters (e.g., "aaaaaaa")
    if len(set(name)) < 3 and len(name) > 5:
        return False
    
    # Check for SQL injection patterns
    sql_patterns = ['--', ';', 'DROP ', 'DELETE ', 'INSERT ', 'UPDATE ', 'SELECT ']
    for pattern in sql_patterns:
        if pattern.lower() in name.lower():
            return False
    
    # Check for excessive special characters
    special_char_count = sum(1 for c in name if not c.isalnum() and not c.isspace() and c not in '-،.')
    if special_char_count > len(name) * 0.3:  # More than 30% special chars
        return False
    
    # Reject if it's just numbers
    if name.replace(' ', '').replace('-', '').isdigit():
        return False
    
    return True

def check_suspicious_patterns(data):
    """Check for suspicious patterns in application data"""
    warnings = []
    
    # Check company name
    company_name = data.get('companyName', '')
    if not validate_company_name(company_name):
        warnings.append('نام شرکت نامعتبر است')
    
    # Check for test data patterns
    test_patterns = ['test', 'تست', 'آزمایش', 'sample', 'نمونه', 'demo']
    for pattern in test_patterns:
        if pattern in company_name.lower():
            warnings.append(f'نام شرکت حاوی کلمه آزمایشی است: {pattern}')
    
    # Check representative names for suspicious patterns
    first_name = data.get('representativeFirstName', '').strip()
    last_name = data.get('representativeLastName', '').strip()
    
    if len(first_name) < 2 or len(last_name) < 2:
        warnings.append('نام یا نام خانوادگی نماینده خیلی کوتاه است')
    
    # Check if first and last names are identical
    if first_name and last_name and first_name == last_name:
        warnings.append('نام و نام خانوادگی نماینده یکسان است')
    
    return warnings
