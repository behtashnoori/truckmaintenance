"""
Test Company Management Endpoint
Tests for POST /api/company endpoint (Business Expert only)
"""

import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app, db
from backend.models.user import User
from backend.models.company import Company
import jwt
from datetime import datetime, timedelta, timezone


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def business_expert_token(app):
    """Create a business expert user and return auth token."""
    with app.app_context():
        user = User(
            username="business_expert_test",
            email="expert@test.com",
            full_name="Business Expert Test",
            role="business_expert"
        )
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return token


@pytest.fixture
def admin_token(app):
    """Create an admin user and return auth token."""
    with app.app_context():
        user = User(
            username="admin_test",
            email="admin@test.com",
            full_name="Admin Test",
            role="admin"
        )
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return token


class TestCompanyManagement:
    """Test Company Management endpoints."""
    
    def test_create_company_success(self, client, business_expert_token):
        """Test successful company creation by business expert."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست',
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['message'] == 'company created'
        
        # Verify company was created in database
        with client.application.app_context():
            company = Company.query.filter_by(phone_mobile='09123456789').first()
            assert company is not None
            assert company.name == 'شرکت تست'
            assert company.is_active is True
    
    def test_create_company_with_companyName_field(self, client, business_expert_token):
        """Test company creation with alternative field name 'companyName'."""
        response = client.post('/api/company', 
            json={
                'companyName': 'شرکت تست دوم',
                'phone': '09123456788'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
    
    def test_create_company_with_tel_field(self, client, business_expert_token):
        """Test company creation with alternative field name 'tel'."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست سوم',
                'tel': '09123456787'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
    
    def test_create_company_without_token(self, client):
        """Test company creation without authentication token."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست',
                'phone': '09123456789'
            }
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'message' in data
    
    def test_create_company_with_invalid_token(self, client):
        """Test company creation with invalid token."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست',
                'phone': '09123456789'
            },
            headers={'Authorization': 'Bearer invalid_token_here'}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'message' in data
    
    def test_create_company_as_admin(self, client, admin_token):
        """Test that admin can create company (admin has all permissions)."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست',
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Admin is allowed in business_expert_required decorator
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
    
    def test_create_company_missing_name(self, client, business_expert_token):
        """Test company creation with missing name field."""
        response = client.post('/api/company', 
            json={
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_company_missing_phone(self, client, business_expert_token):
        """Test company creation with missing phone field."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_company_empty_name(self, client, business_expert_token):
        """Test company creation with empty name."""
        response = client.post('/api/company', 
            json={
                'name': '',
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_company_empty_phone(self, client, business_expert_token):
        """Test company creation with empty phone."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست',
                'phone': ''
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_company_invalid_phone_format(self, client, business_expert_token):
        """Test company creation with invalid phone format."""
        invalid_phones = [
            '123',  # Too short
            'abcdefghij',  # Not numeric
            '12345678901234567890',  # Too long
            '1234567890',  # Invalid format (not starting with 0)
        ]
        
        for invalid_phone in invalid_phones:
            response = client.post('/api/company', 
                json={
                    'name': 'شرکت تست',
                    'phone': invalid_phone
                },
                headers={'Authorization': f'Bearer {business_expert_token}'}
            )
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_create_company_duplicate_phone(self, client, business_expert_token):
        """Test company creation with duplicate phone number."""
        # Create first company
        response1 = client.post('/api/company', 
            json={
                'name': 'شرکت اول',
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        assert response1.status_code == 201
        
        # Try to create second company with same phone
        response2 = client.post('/api/company', 
            json={
                'name': 'شرکت دوم',
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response2.status_code == 409
        data = response2.get_json()
        assert 'error' in data
        assert 'قبلاً ثبت شده' in data['error']
    
    def test_create_company_extra_fields_rejected(self, client, business_expert_token):
        """Test that extra fields are rejected by validation."""
        response = client.post('/api/company', 
            json={
                'name': 'شرکت تست',
                'phone': '09123456789',
                'extra_field': 'should be rejected'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_company_xss_protection(self, client, business_expert_token):
        """Test that XSS attempts are sanitized."""
        response = client.post('/api/company', 
            json={
                'name': '<script>alert("XSS")</script>شرکت تست',
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 201
        
        # Verify that script tags are removed
        with client.application.app_context():
            company = Company.query.filter_by(phone_mobile='09123456789').first()
            assert '<script>' not in company.name
            assert 'شرکت تست' in company.name
    
    def test_create_company_sql_injection_protection(self, client, business_expert_token):
        """Test SQL injection protection."""
        response = client.post('/api/company', 
            json={
                'name': "'; DROP TABLE company; --",
                'phone': '09123456789'
            },
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        # Should either succeed with sanitized input or fail gracefully
        assert response.status_code in [201, 400, 500]
        
        # Verify table still exists
        with client.application.app_context():
            companies = Company.query.all()
            # Table should still exist (not dropped)
            assert companies is not None


def run_tests():
    """Run all tests and generate report."""
    print("\n" + "="*80)
    print("COMPANY MANAGEMENT API TEST REPORT")
    print("Testing POST /api/company endpoint")
    print("="*80 + "\n")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    return exit_code


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)

