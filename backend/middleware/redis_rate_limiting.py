"""
Redis-based rate limiting for production use with fallback when Redis unavailable
"""
import os
import redis
from functools import wraps
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

# Redis connection with error handling
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = None
redis_available = False

try:
    redis_client = redis.from_url(redis_url, decode_responses=True)
    # Test connection
    redis_client.ping()
    redis_available = True
    logger.info("Redis connection successful")
except Exception as e:
    logger.warning(f"Redis not available: {e}. Rate limiting will be disabled.")
    redis_available = False

# Initialize Flask-Limiter
limiter = None

def init_limiter(app):
    """Initialize Flask-Limiter with Redis backend"""
    global limiter
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        storage_uri=redis_url,
        default_limits=["1000 per hour", "100 per minute"]
    )
    return limiter

def rate_limit_by_user(max_requests=100, window_seconds=60):
    """Rate limiting decorator based on user ID (for authenticated users)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Skip if Redis not available
            if not redis_available:
                return f(*args, **kwargs)
            
            try:
                # Get user ID from JWT token if available
                user_id = None
                if 'Authorization' in request.headers:
                    try:
                        import jwt
                        from flask import current_app
                        token = request.headers['Authorization'].split(' ')[1]
                        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                        user_id = data.get('user_id')
                    except:
                        pass
                
                # Use user ID or IP for rate limiting
                key = f"rate_limit:{user_id or get_remote_address()}"
                
                # Check current count
                current_count = redis_client.get(key)
                if current_count is None:
                    # First request in window
                    redis_client.setex(key, window_seconds, 1)
                else:
                    current_count = int(current_count)
                    if current_count >= max_requests:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Maximum {max_requests} requests per {window_seconds} seconds'
                        }), 429
                    
                    # Increment counter
                    redis_client.incr(key)
            except Exception as e:
                # If Redis fails, just log and continue
                logger.warning(f"Rate limiting error: {e}")
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def login_rate_limit(max_attempts=5, window_minutes=15):
    """Special rate limiter for login attempts"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Skip if Redis not available
            if not redis_available:
                return f(*args, **kwargs)
            
            try:
                client_ip = get_remote_address()
                key = f"login_attempts:{client_ip}"
                window_seconds = window_minutes * 60
                
                # Get current attempts
                attempts = redis_client.get(key)
                if attempts is None:
                    # First attempt
                    redis_client.setex(key, window_seconds, 1)
                else:
                    attempts = int(attempts)
                    if attempts >= max_attempts:
                        return jsonify({
                            'error': 'Too many login attempts',
                            'message': f'Maximum {max_attempts} login attempts per {window_minutes} minutes'
                        }), 429
                    
                    # Increment attempts
                    redis_client.incr(key)
            except Exception as e:
                # If Redis fails, just log and continue
                logger.warning(f"Login rate limiting error: {e}")
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def file_upload_rate_limit(max_uploads=10, window_hours=1):
    """Rate limiter for file uploads"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Skip if Redis not available
            if not redis_available:
                return f(*args, **kwargs)
            
            try:
                client_ip = get_remote_address()
                key = f"file_uploads:{client_ip}"
                window_seconds = window_hours * 3600
                
                uploads = redis_client.get(key)
                if uploads is None:
                    redis_client.setex(key, window_seconds, 1)
                else:
                    uploads = int(uploads)
                    if uploads >= max_uploads:
                        return jsonify({
                            'error': 'File upload limit exceeded',
                            'message': f'Maximum {max_uploads} uploads per {window_hours} hours'
                        }), 429
                    
                    redis_client.incr(key)
            except Exception as e:
                # If Redis fails, just log and continue
                logger.warning(f"File upload rate limiting error: {e}")
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def clear_rate_limit(key_prefix, identifier):
    """Clear rate limit for specific identifier"""
    if not redis_available:
        return
    
    try:
        pattern = f"{key_prefix}:{identifier}"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        logger.warning(f"Error clearing rate limit: {e}")
