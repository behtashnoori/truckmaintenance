"""
Rate limiting middleware to prevent abuse
"""
from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict, deque

# Simple in-memory rate limiter (use Redis in production)
rate_limit_storage = defaultdict(lambda: deque())

def rate_limit(max_requests=100, window_seconds=60):
    """
    Rate limiting decorator
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Disable rate limiting in testing mode
            from flask import current_app
            if current_app.config.get('TESTING'):
                return f(*args, **kwargs)
            
            # Get client IP
            client_ip = request.remote_addr
            
            # Get current time
            current_time = time.time()
            
            # Clean old requests outside the window
            window_start = current_time - window_seconds
            client_requests = rate_limit_storage[client_ip]
            
            # Remove old requests
            while client_requests and client_requests[0] < window_start:
                client_requests.popleft()
            
            # Check if limit exceeded
            if len(client_requests) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.'
                }), 429
            
            # Add current request
            client_requests.append(current_time)
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def login_rate_limit(max_attempts=5, window_minutes=15):
    """
    Special rate limiter for login attempts
    Args:
        max_attempts: Maximum login attempts allowed
        window_minutes: Time window in minutes
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Disable rate limiting in testing mode
            from flask import current_app
            if current_app.config.get('TESTING'):
                return f(*args, **kwargs)
            
            client_ip = request.remote_addr
            current_time = time.time()
            window_start = current_time - (window_minutes * 60)
            
            # Use a separate storage for login attempts
            login_attempts_key = f"login_attempts_{client_ip}"
            client_attempts = rate_limit_storage[login_attempts_key]
            
            # Clean old attempts
            while client_attempts and client_attempts[0] < window_start:
                client_attempts.popleft()
            
            # Check if limit exceeded
            if len(client_attempts) >= max_attempts:
                return jsonify({
                    'error': 'Too many login attempts',
                    'message': f'Maximum {max_attempts} login attempts per {window_minutes} minutes. Please try again later.'
                }), 429
            
            # Add current attempt
            client_attempts.append(current_time)
            
            return f(*args, **kwargs)
        return decorated
    return decorator
