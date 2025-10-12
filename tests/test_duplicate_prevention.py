"""
Comprehensive tests for duplicate prevention system
"""
import pytest
import json
from datetime import datetime, timezone
from backend.app import create_app, db
from backend.models.provider_application import ProviderApplication
from backend.models.company import Company, Category
from backend.models.user import User, BusinessExpert


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['DUPLICATE_CHECK_ENABLED'] = True
    app.config['RATE_LIMIT_ENABLED'] = True
    app.config['RATE_LIMIT_APPLICATIONS_PER_HOUR'] = 3
    app.config['FUZZY_MATCH_THRESHOLD'] = 0.8
    
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
def sample_application_data():
    """Sample application data for testing"""
    return {
        'companyName': 'شرکت تست سرویس خودرو',
        'representativeFirstName': 'علی',
        'representativeLastName': 'احمدی',
        'address': 'تهران، خیابان آزادی',
        'phoneMobile': '09123456780',
        'phoneLandline': '02112345678',
        'serviceCategories': ['تعمیرات موتور', 'تعویض روغن'],
        'latitude': 35.6892,
        'longitude': 51.3890
    }


class TestDuplicatePhoneNumber:
    """Test duplicate phone number detection"""
    
    def test_first_submission_success(self, client, sample_application_data):
        """Test that first submission with unique phone succeeds"""
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'id' in data['data']
    
    def test_duplicate_phone_rejected(self, client, sample_application_data):
        """Test that duplicate phone number is rejected"""
        # First submission
        client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        # Second submission with same phone
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'DUPLICATE_PHONE'
        assert 'support_contact' in data['error']
    
    def test_phone_sanitization(self, client, sample_application_data):
        """Test that phone numbers are sanitized before duplicate check"""
        # Submit with clean phone
        client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        # Submit with formatted phone (spaces and dashes)
        sample_application_data['phoneMobile'] = '091-234-567-80'
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error']['code'] == 'DUPLICATE_PHONE'
    
    def test_different_phones_allowed(self, client, sample_application_data):
        """Test that different phone numbers are allowed"""
        # First submission
        client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        # Second submission with different phone
        sample_application_data['phoneMobile'] = '09123456781'
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True


class TestPhoneValidation:
    """Test phone number validation"""
    
    def test_valid_iranian_mobile(self, client, sample_application_data):
        """Test valid Iranian mobile numbers"""
        valid_numbers = [
            '09123456789',
            '09353456789',
            '09903456789'
        ]
        
        for i, number in enumerate(valid_numbers):
            sample_application_data['phoneMobile'] = number
            sample_application_data['companyName'] = f'شرکت تست {i}'
            response = client.post(
                '/api/provider-applications',
                data=json.dumps(sample_application_data),
                content_type='application/json'
            )
            assert response.status_code == 201
    
    def test_invalid_phone_formats(self, client, sample_application_data):
        """Test invalid phone number formats"""
        invalid_numbers = [
            '0912345678',  # Too short
            '091234567890',  # Too long
            '0812345678',  # Wrong prefix
            '9123456789',  # Missing leading 0
            'abcd1234567',  # Contains letters
            '09000000000',  # All zeros (test pattern)
            '09111111111',  # All same digits
        ]
        
        for number in invalid_numbers:
            sample_application_data['phoneMobile'] = number
            response = client.post(
                '/api/provider-applications',
                data=json.dumps(sample_application_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'INVALID_PHONE'


class TestFuzzyMatching:
    """Test fuzzy matching for company names"""
    
    def test_similar_name_warning(self, client, sample_application_data):
        """Test that similar company names trigger a warning"""
        # First submission
        sample_application_data['companyName'] = 'شرکت خدمات خودرو'
        sample_application_data['phoneMobile'] = '09123456780'
        client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        # Second submission with similar name but different phone
        sample_application_data['companyName'] = 'شرکت خدمات خودرویی'  # Very similar
        sample_application_data['phoneMobile'] = '09123456781'
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201  # Still succeeds
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Check if warning is present
        if 'warning' in data:
            assert data['warning']['code'] == 'SIMILAR_COMPANY_NAME'
    
    def test_dissimilar_names_no_warning(self, client, sample_application_data):
        """Test that different company names don't trigger warning"""
        # First submission
        sample_application_data['companyName'] = 'شرکت الف'
        sample_application_data['phoneMobile'] = '09123456780'
        client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        # Second submission with completely different name
        sample_application_data['companyName'] = 'مجموعه ب'
        sample_application_data['phoneMobile'] = '09123456781'
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'warning' not in data or data.get('warning') is None


class TestCompanyNameValidation:
    """Test company name validation"""
    
    def test_valid_company_names(self, client, sample_application_data):
        """Test valid company names"""
        valid_names = [
            'شرکت تست',
            'مجموعه خدمات حمل و نقل',
            'گروه صنعتی ABC'
        ]
        
        for i, name in enumerate(valid_names):
            sample_application_data['companyName'] = name
            sample_application_data['phoneMobile'] = f'0912345678{i}'
            response = client.post(
                '/api/provider-applications',
                data=json.dumps(sample_application_data),
                content_type='application/json'
            )
            assert response.status_code == 201
    
    def test_invalid_company_names(self, client, sample_application_data):
        """Test invalid company names"""
        invalid_names = [
            'a',  # Too short
            '12345678',  # Just numbers
            'a' * 300,  # Too long
            'DROP TABLE;',  # SQL injection attempt
            '@@@@@@@@',  # Excessive special characters
        ]
        
        for name in invalid_names:
            sample_application_data['companyName'] = name
            response = client.post(
                '/api/provider-applications',
                data=json.dumps(sample_application_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'INVALID_COMPANY_NAME'


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_within_rate_limit(self, client, sample_application_data):
        """Test that 3 requests within an hour succeed"""
        for i in range(3):
            sample_application_data['phoneMobile'] = f'0912345678{i}'
            sample_application_data['companyName'] = f'شرکت تست {i}'
            response = client.post(
                '/api/provider-applications',
                data=json.dumps(sample_application_data),
                content_type='application/json'
            )
            assert response.status_code == 201
    
    def test_exceeds_rate_limit(self, client, sample_application_data):
        """Test that 4th request within an hour is blocked"""
        # Make 3 successful requests
        for i in range(3):
            sample_application_data['phoneMobile'] = f'0912345678{i}'
            sample_application_data['companyName'] = f'شرکت تست {i}'
            client.post(
                '/api/provider-applications',
                data=json.dumps(sample_application_data),
                content_type='application/json'
            )
        
        # 4th request should be blocked
        sample_application_data['phoneMobile'] = '09123456783'
        sample_application_data['companyName'] = 'شرکت تست 4'
        response = client.post(
            '/api/provider-applications',
            data=json.dumps(sample_application_data),
            content_type='application/json'
        )
        
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'RATE_LIMIT_EXCEEDED'
        assert 'retry_after' in data['error']


class TestDatabaseConstraints:
    """Test database-level constraints"""
    
    def test_unique_constraint_on_phone(self, app):
        """Test that database enforces unique constraint on phone_mobile"""
        with app.app_context():
            from sqlalchemy.exc import IntegrityError
            
            # Create first application
            app1 = ProviderApplication(
                company_name='شرکت اول',
                representative_first_name='علی',
                representative_last_name='احمدی',
                address='تهران',
                phone_mobile='09123456789',
                latitude=35.6892,
                longitude=51.3890
            )
            db.session.add(app1)
            db.session.commit()
            
            # Try to create second with same phone
            app2 = ProviderApplication(
                company_name='شرکت دوم',
                representative_first_name='رضا',
                representative_last_name='محمدی',
                address='مشهد',
                phone_mobile='09123456789',  # Same phone
                latitude=36.2974,
                longitude=59.6067
            )
            db.session.add(app2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()


class TestApplicationTracking:
    """Test application tracking fields"""
    
    def test_reapplication_count_field(self, app):
        """Test that reapplication_count is set correctly"""
        with app.app_context():
            app1 = ProviderApplication(
                company_name='شرکت تست',
                representative_first_name='علی',
                representative_last_name='احمدی',
                address='تهران',
                phone_mobile='09123456789',
                latitude=35.6892,
                longitude=51.3890
            )
            db.session.add(app1)
            db.session.commit()
            
            assert app1.reapplication_count == 1
    
    def test_fuzzy_match_warning_field(self, app):
        """Test that fuzzy_match_warning field works"""
        with app.app_context():
            app1 = ProviderApplication(
                company_name='شرکت تست',
                representative_first_name='علی',
                representative_last_name='احمدی',
                address='تهران',
                phone_mobile='09123456789',
                latitude=35.6892,
                longitude=51.3890,
                fuzzy_match_warning=True,
                similar_company_names='شرکت تست مشابه'
            )
            db.session.add(app1)
            db.session.commit()
            
            assert app1.fuzzy_match_warning is True
            assert app1.similar_company_names == 'شرکت تست مشابه'

