"""
Test Session Management Endpoints
Tests for session validation and management functionality
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
import jwt
from backend.app import create_app, db
from backend.models.user import User
from backend.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-for-session-management'


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            role='business_expert',
            is_active=True
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        
        # Refresh to get ID
        db.session.refresh(user)
        user_id = user.id
        
        return user_id


@pytest.fixture
def auth_token(app, test_user):
    """Generate a valid auth token"""
    with app.app_context():
        token = jwt.encode({
            'user_id': test_user,
            'username': 'testuser',
            'role': 'business_expert',
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return token


@pytest.fixture
def expired_token(app, test_user):
    """Generate an expired auth token"""
    with app.app_context():
        token = jwt.encode({
            'user_id': test_user,
            'username': 'testuser',
            'role': 'business_expert',
            'exp': datetime.now(timezone.utc) - timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return token


def test_validate_session_success(client, auth_token):
    """Test successful session validation"""
    response = client.post(
        '/api/validate-session',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['valid'] is True
    assert data['message'] == 'جلسه معتبر است'
    assert 'user' in data
    assert 'session' in data
    assert 'expires_in' in data['session']
    assert 'expires_at' in data['session']
    
    # Check user data
    assert data['user']['username'] == 'testuser'
    assert data['user']['role'] == 'business_expert'


def test_validate_session_no_token(client):
    """Test session validation without token"""
    response = client.post('/api/validate-session')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['valid'] is False
    assert 'توکن وجود ندارد' in data['error']


def test_validate_session_invalid_token_format(client):
    """Test session validation with invalid token format"""
    response = client.post(
        '/api/validate-session',
        headers={'Authorization': 'InvalidFormat'}
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['valid'] is False
    assert 'فرمت توکن نامعتبر است' in data['error']


def test_validate_session_expired_token(client, expired_token):
    """Test session validation with expired token"""
    response = client.post(
        '/api/validate-session',
        headers={'Authorization': f'Bearer {expired_token}'}
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['valid'] is False
    assert 'توکن منقضی شده است' in data['error']


def test_validate_session_invalid_token(client):
    """Test session validation with completely invalid token"""
    response = client.post(
        '/api/validate-session',
        headers={'Authorization': 'Bearer invalid.token.here'}
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['valid'] is False


def test_validate_session_inactive_user(client, app):
    """Test session validation for inactive user"""
    with app.app_context():
        # Create inactive user
        user = User(
            username='inactiveuser',
            email='inactive@example.com',
            full_name='Inactive User',
            role='business_expert',
            is_active=False
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Generate token for inactive user
        token = jwt.encode({
            'user_id': user_id,
            'username': 'inactiveuser',
            'role': 'business_expert',
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
    
    response = client.post(
        '/api/validate-session',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['valid'] is False
    assert 'کاربر یافت نشد یا غیرفعال است' in data['error']


def test_validate_session_token_expiry_calculation(client, auth_token, app):
    """Test that session validation correctly calculates time until expiry"""
    response = client.post(
        '/api/validate-session',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that expires_in is a reasonable value (close to 24 hours)
    expires_in = data['session']['expires_in']
    
    # Should be close to 24 hours (86400 seconds), with some tolerance
    assert 86000 < expires_in < 87000, f"Expected ~86400, got {expires_in}"


def test_login_and_validate_session_flow(client, app):
    """Test complete flow: login -> validate session"""
    with app.app_context():
        # Create user
        user = User(
            username='flowtest',
            email='flowtest@example.com',
            full_name='Flow Test User',
            role='business_expert',
            is_active=True
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
    
    # Step 1: Login
    login_response = client.post(
        '/api/login',
        json={
            'username': 'flowtest',
            'password': 'testpassword'
        }
    )
    
    assert login_response.status_code == 200
    login_data = json.loads(login_response.data)
    token = login_data['token']
    
    # Step 2: Validate session
    validate_response = client.post(
        '/api/validate-session',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert validate_response.status_code == 200
    validate_data = json.loads(validate_response.data)
    
    assert validate_data['success'] is True
    assert validate_data['valid'] is True
    assert validate_data['user']['username'] == 'flowtest'


def test_me_endpoint_still_works(client, auth_token):
    """Test that /api/me endpoint still works (backward compatibility)"""
    response = client.get(
        '/api/me',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['username'] == 'testuser'
    assert data['role'] == 'business_expert'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

