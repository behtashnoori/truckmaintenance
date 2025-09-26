"""
Security logging middleware
"""
import logging
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
file_handler = logging.FileHandler('security.log')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
security_logger.addHandler(file_handler)

def log_security_event(event_type, message, user_id=None, ip_address=None, additional_data=None):
    """
    Log security events
    Args:
        event_type: Type of security event (login, logout, failed_login, etc.)
        message: Log message
        user_id: User ID if available
        ip_address: Client IP address
        additional_data: Additional data to log
    """
    log_data = {
        'event_type': event_type,
        'message': message,
        'user_id': user_id,
        'ip_address': ip_address or request.remote_addr,
        'timestamp': datetime.utcnow().isoformat(),
        'user_agent': request.headers.get('User-Agent', ''),
        'additional_data': additional_data
    }
    
    security_logger.info(f"{event_type}: {message} - {log_data}")

def log_authentication_attempts(f):
    """Decorator to log authentication attempts"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            
            # Log successful authentication
            if hasattr(result, 'status_code') and result.status_code == 200:
                log_security_event(
                    'successful_login',
                    'User successfully logged in',
                    additional_data={'endpoint': request.endpoint}
                )
            
            return result
        except Exception as e:
            # Log failed authentication
            log_security_event(
                'failed_login',
                f'Failed login attempt: {str(e)}',
                additional_data={'endpoint': request.endpoint, 'error': str(e)}
            )
            raise e
    
    return decorated

def log_api_access(f):
    """Decorator to log API access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = f(*args, **kwargs)
            
            # Log API access
            log_security_event(
                'api_access',
                f'API endpoint accessed: {request.endpoint}',
                additional_data={
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'response_time': (datetime.utcnow() - start_time).total_seconds(),
                    'status_code': getattr(result, 'status_code', None)
                }
            )
            
            return result
        except Exception as e:
            # Log API errors
            log_security_event(
                'api_error',
                f'API error in {request.endpoint}: {str(e)}',
                additional_data={
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'error': str(e)
                }
            )
            raise e
    
    return decorated

def log_suspicious_activity(f):
    """Decorator to log suspicious activity"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check for suspicious patterns
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        # Log suspicious user agents
        suspicious_agents = ['bot', 'crawler', 'scanner', 'curl', 'wget']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            log_security_event(
                'suspicious_user_agent',
                f'Suspicious user agent detected: {user_agent}',
                ip_address=ip_address
            )
        
        # Log requests with unusual headers
        if 'X-Forwarded-For' in request.headers and len(request.headers['X-Forwarded-For'].split(',')) > 3:
            log_security_event(
                'suspicious_headers',
                'Multiple X-Forwarded-For headers detected',
                ip_address=ip_address
            )
        
        return f(*args, **kwargs)
    
    return decorated
