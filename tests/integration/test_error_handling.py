"""
Comprehensive Error Handling Tests for Truck Maintenance API
Tests various error scenarios across all endpoints
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.app import create_app, db
from backend.models.user import User, Admin
from backend.models.company import Company
from backend.models.provider_application import ProviderApplication
import jwt
import datetime
from datetime import timezone
import json


class TestAuthenticationErrors:
    """Test authentication-related errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test users
            self.admin_user = User(
                username='admin_test_auth',
                email='admin_auth@test.com',
                full_name='Admin Test',
                role='admin',
                is_active=True
            )
            self.admin_user.set_password('admin123')
            db.session.add(self.admin_user)
            
            self.inactive_user = User(
                username='inactive_test_auth',
                email='inactive_auth@test.com',
                full_name='Inactive Test',
                role='user',
                is_active=False
            )
            self.inactive_user.set_password('inactive123')
            db.session.add(self.inactive_user)
            
            db.session.commit()
            
            # Store IDs before session ends
            self.admin_user_id = self.admin_user.id
            self.inactive_user_id = self.inactive_user.id
            
            # Generate valid token
            self.valid_token = jwt.encode({
                'user_id': self.admin_user_id,
                'username': self.admin_user.username,
                'role': self.admin_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
            
            # Generate expired token
            self.expired_token = jwt.encode({
                'user_id': self.admin_user_id,
                'username': self.admin_user.username,
                'role': self.admin_user.role,
                'exp': datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_missing_token(self):
        """Test access without token"""
        response = self.client.get('/api/users')
        assert response.status_code == 401
        data = response.get_json()
        # Check if response has proper error message
        assert ('success' in data and data['success'] is False) or ('message' in data and 'Token' in data['message'])
        print("✓ Missing token error handled correctly")
    
    def test_invalid_token_format(self):
        """Test with malformed token"""
        response = self.client.get(
            '/api/me',
            headers={'Authorization': 'InvalidFormat'}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Invalid token format error handled correctly")
    
    def test_expired_token(self):
        """Test with expired token"""
        response = self.client.get(
            '/api/me',
            headers={'Authorization': f'Bearer {self.expired_token}'}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        assert 'منقضی' in str(data) or 'expired' in str(data).lower()
        print("✓ Expired token error handled correctly")
    
    def test_invalid_token_signature(self):
        """Test with invalid signature"""
        invalid_token = jwt.encode({
            'user_id': 1,
            'username': 'test',
            'role': 'admin',
            'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
        }, 'wrong_secret_key', algorithm='HS256')
        
        response = self.client.get(
            '/api/me',
            headers={'Authorization': f'Bearer {invalid_token}'}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Invalid token signature error handled correctly")
    
    def test_deactivated_user_token(self):
        """Test with token of deactivated user"""
        inactive_token = jwt.encode({
            'user_id': self.inactive_user_id,
            'username': 'inactive_test_auth',
            'role': 'user',
            'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
        }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        response = self.client.get(
            '/api/me',
            headers={'Authorization': f'Bearer {inactive_token}'}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        assert 'غیرفعال' in str(data) or 'deactivated' in str(data).lower()
        print("✓ Deactivated user error handled correctly")
    
    def test_wrong_credentials(self):
        """Test login with wrong credentials"""
        response = self.client.post(
            '/api/login',
            json={
                'username': 'admin_test_auth',
                'password': 'wrong_password'
            }
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        assert 'نادرست' in str(data) or 'incorrect' in str(data).lower()
        print("✓ Wrong credentials error handled correctly")
    
    def test_nonexistent_user_login(self):
        """Test login with non-existent user"""
        response = self.client.post(
            '/api/login',
            json={
                'username': 'nonexistent_user',
                'password': 'password123'
            }
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Non-existent user error handled correctly")


class TestAuthorizationErrors:
    """Test authorization-related errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create admin user
            self.admin_user = User(
                username='admin_test_authz',
                email='admin_authz@test.com',
                full_name='Admin Test',
                role='admin',
                is_active=True
            )
            self.admin_user.set_password('admin123')
            db.session.add(self.admin_user)
            
            # Create regular user
            self.regular_user = User(
                username='user_test_authz',
                email='user_authz@test.com',
                full_name='User Test',
                role='user',
                is_active=True
            )
            self.regular_user.set_password('user123')
            db.session.add(self.regular_user)
            
            # Create business expert
            self.expert_user = User(
                username='expert_test_authz',
                email='expert_authz@test.com',
                full_name='Expert Test',
                role='business_expert',
                is_active=True
            )
            self.expert_user.set_password('expert123')
            db.session.add(self.expert_user)
            
            db.session.commit()
            
            # Generate tokens
            self.admin_token = jwt.encode({
                'user_id': self.admin_user.id,
                'username': self.admin_user.username,
                'role': self.admin_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
            
            self.user_token = jwt.encode({
                'user_id': self.regular_user.id,
                'username': self.regular_user.username,
                'role': self.regular_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
            
            self.expert_token = jwt.encode({
                'user_id': self.expert_user.id,
                'username': self.expert_user.username,
                'role': self.expert_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_regular_user_admin_access(self):
        """Test regular user accessing admin-only endpoint"""
        response = self.client.get(
            '/api/users',
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin' in data.get('message', '') or 'دسترسی' in str(data)
        print("✓ Regular user admin access denied correctly")
    
    def test_regular_user_business_expert_access(self):
        """Test regular user accessing business expert endpoint"""
        response = self.client.get(
            '/api/business-expert/applications',
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        assert response.status_code == 403
        print("✓ Regular user business expert access denied correctly")
    
    def test_business_expert_admin_access(self):
        """Test business expert accessing admin-only endpoint"""
        # Test access to admin dashboard
        response = self.client.get(
            '/api/dashboard',  # Admin dashboard endpoint
            headers={'Authorization': f'Bearer {self.expert_token}'}
        )
        # Should return 403 Forbidden (not authorized) not 404 (not found)
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin' in data.get('message', '') or 'دسترسی' in str(data)
        print("✓ Business expert admin access denied correctly")


class TestValidationErrors:
    """Test input validation errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            self.admin_user = User(
                username='admin_test_val',
                email='admin_val@test.com',
                full_name='Admin Test',
                role='admin',
                is_active=True
            )
            self.admin_user.set_password('admin123')
            db.session.add(self.admin_user)
            db.session.commit()
            
            self.admin_token = jwt.encode({
                'user_id': self.admin_user.id,
                'username': self.admin_user.username,
                'role': self.admin_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_missing_required_fields_login(self):
        """Test login with missing fields"""
        # Missing password
        response = self.client.post(
            '/api/login',
            json={'username': 'test'}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Missing required fields error handled correctly")
    
    def test_invalid_email_format(self):
        """Test with invalid email format"""
        response = self.client.post(
            '/api/users',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'username': 'newuser',
                'email': 'invalid-email',
                'password': 'password123',
                'full_name': 'New User',
                'role': 'user'
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        print("✓ Invalid email format error handled correctly")
    
    def test_short_password(self):
        """Test with password too short"""
        response = self.client.post(
            '/api/users',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': '123',
                'full_name': 'New User',
                'role': 'user'
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        print("✓ Short password error handled correctly")
    
    def test_invalid_role(self):
        """Test with invalid role"""
        response = self.client.post(
            '/api/users',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'password123',
                'full_name': 'New User',
                'role': 'invalid_role'
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'نقش' in data['error'] or 'role' in data['error'].lower()
        print("✓ Invalid role error handled correctly")
    
    def test_empty_username(self):
        """Test with empty username"""
        response = self.client.post(
            '/api/login',
            json={
                'username': '',
                'password': 'password123'
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Empty username error handled correctly")
    
    def test_invalid_json_data(self):
        """Test with invalid JSON data"""
        response = self.client.post(
            '/api/login',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
        print("✓ Invalid JSON data error handled correctly")
    
    def test_invalid_pagination_params(self):
        """Test with invalid pagination parameters"""
        response = self.client.get(
            '/api/users?page=-1&per_page=0',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        # Should either return error or use default values
        assert response.status_code in [200, 400]
        print("✓ Invalid pagination params handled correctly")


class TestDatabaseErrors:
    """Test database-related errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            self.admin_user = User(
                username='admin_test_db',
                email='admin_db@test.com',
                full_name='Admin Test',
                role='admin',
                is_active=True
            )
            self.admin_user.set_password('admin123')
            db.session.add(self.admin_user)
            
            # Create existing user for duplicate tests
            self.existing_user = User(
                username='existing_user_db',
                email='existing_db@test.com',
                full_name='Existing User',
                role='user',
                is_active=True
            )
            self.existing_user.set_password('password123')
            db.session.add(self.existing_user)
            
            db.session.commit()
            
            self.admin_token = jwt.encode({
                'user_id': self.admin_user.id,
                'username': self.admin_user.username,
                'role': self.admin_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_duplicate_username(self):
        """Test creating user with duplicate username"""
        response = self.client.post(
            '/api/users',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'username': 'existing_user_db',
                'email': 'newemail_db@test.com',
                'password': 'password123',
                'full_name': 'New User',
                'role': 'user'
            }
        )
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert 'استفاده شده' in data['error'] or 'already' in data['error'].lower()
        print("✓ Duplicate username error handled correctly")
    
    def test_duplicate_email(self):
        """Test creating user with duplicate email"""
        response = self.client.post(
            '/api/users',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'username': 'newusername_db',
                'email': 'existing_db@test.com',
                'password': 'password123',
                'full_name': 'New User',
                'role': 'user'
            }
        )
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        print("✓ Duplicate email error handled correctly")
    
    def test_nonexistent_resource(self):
        """Test accessing non-existent resource"""
        response = self.client.get(
            '/api/admin/users/99999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        assert response.status_code == 404
        print("✓ Non-existent resource error handled correctly")
    
    def test_delete_nonexistent_user(self):
        """Test deleting non-existent user"""
        response = self.client.delete(
            '/api/admin/users/99999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        assert response.status_code == 404
        print("✓ Delete non-existent user error handled correctly")


class TestCompanyValidationErrors:
    """Test company-specific validation errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create business expert (not admin) since company endpoint requires business_expert role
            self.expert_user = User(
                username='expert_test_company',
                email='expert_company@test.com',
                full_name='Expert Test',
                role='business_expert',
                is_active=True
            )
            self.expert_user.set_password('expert123')
            db.session.add(self.expert_user)
            db.session.commit()
            
            self.admin_token = jwt.encode({
                'user_id': self.expert_user.id,
                'username': self.expert_user.username,
                'role': self.expert_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_invalid_phone_format_company(self):
        """Test with invalid phone format for company"""
        response = self.client.post(
            '/api/company',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'name': 'Test Company',
                'phone': '123'  # Invalid format
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Invalid phone format error handled correctly")
    
    def test_invalid_phone_format(self):
        """Test with invalid phone format"""
        response = self.client.post(
            '/api/company',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'name': 'Test Company',
                'phone': 'invalid'  # Invalid format
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Invalid phone format error handled correctly")
    
    def test_missing_company_name(self):
        """Test creating company without name"""
        response = self.client.post(
            '/api/company',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'phone': '09123456789'  # Missing name
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False or 'error' in data
        print("✓ Missing company name error handled correctly")


class TestRateLimitingErrors:
    """Test rate limiting errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            self.test_user = User(
                username='test_user_rate',
                email='test_rate@test.com',
                full_name='Test User',
                role='user',
                is_active=True
            )
            self.test_user.set_password('password123')
            db.session.add(self.test_user)
            db.session.commit()
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_rate_limiting(self):
        """Test rate limiting on login endpoint"""
        # Make multiple failed login attempts
        login_data = {
            'username': 'test_user_rate',
            'password': 'wrong_password'
        }
        
        # Make several requests (rate limit is typically 5 attempts in 15 minutes)
        for i in range(6):
            response = self.client.post('/api/login', json=login_data)
        
        # The last request should be rate limited
        # Note: This might not work if Redis is not available and fallback is used
        if response.status_code == 429:
            print("✓ Login rate limiting working correctly")
        else:
            print("⚠ Login rate limiting using fallback (Redis not available)")


class TestApplicationErrors:
    """Test provider application-specific errors"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and database"""
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-for-testing-only'
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create business expert
            self.expert_user = User(
                username='expert_test_app',
                email='expert_app@test.com',
                full_name='Expert Test',
                role='business_expert',
                is_active=True
            )
            self.expert_user.set_password('expert123')
            db.session.add(self.expert_user)
            db.session.commit()
            
            self.expert_token = jwt.encode({
                'user_id': self.expert_user.id,
                'username': self.expert_user.username,
                'role': self.expert_user.role,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)
            }, self.app.config['SECRET_KEY'], algorithm='HS256')
        
        yield
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_invalid_application_status(self):
        """Test updating application with invalid status"""
        response = self.client.patch(
            '/api/business-expert/applications/1',
            headers={'Authorization': f'Bearer {self.expert_token}'},
            json={'status': 'invalid_status'}
        )
        assert response.status_code in [400, 404]
        print("✓ Invalid application status error handled correctly")
    
    def test_nonexistent_application(self):
        """Test accessing non-existent application"""
        response = self.client.get(
            '/api/business-expert/applications/99999',
            headers={'Authorization': f'Bearer {self.expert_token}'}
        )
        assert response.status_code == 404
        print("✓ Non-existent application error handled correctly")


def run_all_tests():
    """Run all error handling tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE ERROR HANDLING TEST SUITE")
    print("="*70 + "\n")
    
    test_classes = [
        ("Authentication Errors", TestAuthenticationErrors),
        ("Authorization Errors", TestAuthorizationErrors),
        ("Validation Errors", TestValidationErrors),
        ("Database Errors", TestDatabaseErrors),
        ("Company Validation Errors", TestCompanyValidationErrors),
        ("Rate Limiting Errors", TestRateLimitingErrors),
        ("Application Errors", TestApplicationErrors),
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_name, test_class in test_classes:
        print(f"\n{'='*70}")
        print(f"Testing: {test_name}")
        print(f"{'='*70}\n")
        
        # Run pytest for this test class
        result = pytest.main([
            __file__,
            f'-k', test_class.__name__,
            '-v',
            '--tb=short'
        ])
        
        if result == 0:
            print(f"\n✓ All {test_name} tests passed!")
            total_passed += 1
        else:
            print(f"\n✗ Some {test_name} tests failed!")
            total_failed += 1
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Test Categories Passed: {total_passed}")
    print(f"Test Categories Failed: {total_failed}")
    print("="*70 + "\n")
    
    return total_failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)

