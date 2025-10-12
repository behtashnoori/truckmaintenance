"""
Test Provider Application Endpoints
Tests for provider application submission and management
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from backend.app import create_app, db
from backend.models.user import User
from backend.models.provider_application import ProviderApplication
from backend.models.company import Company, Category
from backend.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-for-provider-applications'


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
def business_expert_user(app):
    """Create a business expert user"""
    with app.app_context():
        user = User(
            username='business_expert',
            email='expert@example.com',
            full_name='Business Expert',
            role='business_expert',
            is_active=True
        )
        user.set_password('expert123')
        db.session.add(user)
        db.session.commit()
        
        db.session.refresh(user)
        user_id = user.id
        
        return user_id


@pytest.fixture
def business_expert_token(app, business_expert_user):
    """Generate auth token for business expert"""
    import jwt
    
    with app.app_context():
        token = jwt.encode({
            'user_id': business_expert_user,
            'username': 'business_expert',
            'role': 'business_expert',
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return token


def test_create_provider_application_success(client):
    """Test successful provider application submission"""
    data = {
        "companyName": "شرکت حمل و نقل تست",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران، خیابان ولیعصر، پلاک 123",
        "phoneMobile": "09123456789",
        "phoneLandline": "02112345678",
        "serviceCategories": ["امداد جاده‌ای", "تعویض لاستیک"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    response = client.post(
        '/api/provider-applications',
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    
    assert response_data['success'] is True
    assert 'data' in response_data
    assert 'id' in response_data['data']
    assert response_data['data']['status'] == 'pending'


def test_create_provider_application_saves_to_database(client, app):
    """Test that application is saved correctly to database"""
    data = {
        "companyName": "شرکت تست دیتابیس",
        "representativeFirstName": "محمد",
        "representativeLastName": "رضایی",
        "address": "اصفهان، خیابان چهارباغ",
        "phoneMobile": "09131234567",
        "serviceCategories": ["تعمیرات موتور", "برق خودرو"],
        "latitude": 32.6546,
        "longitude": 51.6680
    }
    
    response = client.post('/api/provider-applications', json=data)
    assert response.status_code == 201
    
    response_data = json.loads(response.data)
    app_id = response_data['data']['id']
    
    # Check database
    with app.app_context():
        app_record = ProviderApplication.query.get(app_id)
        assert app_record is not None
        assert app_record.company_name == "شرکت تست دیتابیس"
        assert app_record.representative_first_name == "محمد"
        assert app_record.representative_last_name == "رضایی"
        assert app_record.phone_mobile == "09131234567"
        assert app_record.latitude == 32.6546
        assert app_record.longitude == 51.6680
        assert app_record.status == 'pending'
        assert app_record.is_approved is False


def test_create_provider_application_saves_categories(client, app):
    """Test that categories are saved in many-to-many relationship"""
    data = {
        "companyName": "شرکت تست کتگوری",
        "representativeFirstName": "حسین",
        "representativeLastName": "کریمی",
        "address": "مشهد، بلوار وکیل آباد",
        "phoneMobile": "09151234567",
        "serviceCategories": ["امداد جاده‌ای", "تعویض لاستیک", "یدک کش"],
        "latitude": 36.2605,
        "longitude": 59.6168
    }
    
    response = client.post('/api/provider-applications', json=data)
    assert response.status_code == 201
    
    response_data = json.loads(response.data)
    app_id = response_data['data']['id']
    
    # Check categories in database
    with app.app_context():
        app_record = ProviderApplication.query.get(app_id)
        assert len(app_record.categories) == 3
        
        category_names = [cat.name for cat in app_record.categories]
        assert "امداد جاده‌ای" in category_names
        assert "تعویض لاستیک" in category_names
        assert "یدک کش" in category_names


def test_create_provider_application_missing_required_field(client):
    """Test validation for missing required fields"""
    data = {
        "companyName": "شرکت ناقص",
        "representativeFirstName": "علی",
        # Missing representativeLastName
        "address": "تهران",
        "phoneMobile": "09123456789",
        "serviceCategories": ["امداد جاده‌ای"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    response = client.post('/api/provider-applications', json=data)
    assert response.status_code == 400


def test_create_provider_application_invalid_phone(client):
    """Test validation for invalid phone number"""
    data = {
        "companyName": "شرکت تست",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران",
        "phoneMobile": "123",  # Invalid phone
        "serviceCategories": ["امداد جاده‌ای"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    response = client.post('/api/provider-applications', json=data)
    assert response.status_code == 400
    
    response_data = json.loads(response.data)
    assert 'شماره موبایل' in response_data['error']


def test_create_provider_application_invalid_coordinates(client):
    """Test validation for invalid coordinates"""
    data = {
        "companyName": "شرکت تست",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران",
        "phoneMobile": "09123456789",
        "serviceCategories": ["امداد جاده‌ای"],
        "latitude": 999,  # Invalid latitude
        "longitude": 51.3890
    }
    
    response = client.post('/api/provider-applications', json=data)
    assert response.status_code == 400
    
    response_data = json.loads(response.data)
    assert 'مختصات' in response_data['error']


def test_create_provider_application_no_categories(client):
    """Test validation when no service categories provided"""
    data = {
        "companyName": "شرکت تست",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران",
        "phoneMobile": "09123456789",
        "serviceCategories": [],  # Empty array
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    response = client.post('/api/provider-applications', json=data)
    assert response.status_code == 400
    
    response_data = json.loads(response.data)
    assert 'حوزه خدماتی' in response_data['error']


def test_get_pending_applications_requires_auth(client):
    """Test that getting applications requires authentication"""
    response = client.get('/api/business-expert/applications')
    assert response.status_code == 401


def test_get_pending_applications_business_expert(client, business_expert_token, app):
    """Test getting pending applications as business expert"""
    # Create some test applications
    with app.app_context():
        for i in range(3):
            app_record = ProviderApplication(
                company_name=f"شرکت تست {i}",
                representative_first_name="علی",
                representative_last_name="احمدی",
                address="تهران",
                phone_mobile=f"0912345678{i}",
                latitude=35.6892,
                longitude=51.3890,
                status='pending'
            )
            db.session.add(app_record)
        db.session.commit()
    
    response = client.get(
        '/api/business-expert/applications',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert 'data' in response_data
    assert len(response_data['data']) == 3


def test_get_application_details(client, business_expert_token, app):
    """Test getting application details"""
    # Create test application
    with app.app_context():
        app_record = ProviderApplication(
            company_name="شرکت جزئیات",
            representative_first_name="محمد",
            representative_last_name="رضایی",
            address="تهران",
            phone_mobile="09123456789",
            latitude=35.6892,
            longitude=51.3890,
            status='pending'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id
    
    response = client.get(
        f'/api/business-expert/applications/{app_id}',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['success'] is True
    assert response_data['data']['company_name'] == "شرکت جزئیات"
    assert response_data['data']['phone_mobile'] == "09123456789"


def test_approve_application_creates_company(client, business_expert_token, app):
    """Test that approving application creates a company"""
    # Create test application with categories
    with app.app_context():
        app_record = ProviderApplication(
            company_name="شرکت تایید",
            representative_first_name="حسین",
            representative_last_name="کریمی",
            address="اصفهان، خیابان چهارباغ",
            phone_mobile="09131234567",
            latitude=32.6546,
            longitude=51.6680,
            status='pending'
        )
        
        # Add categories
        cat1 = Category(name="امداد جاده‌ای")
        cat2 = Category(name="تعویض لاستیک")
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.flush()
        
        app_record.categories.append(cat1)
        app_record.categories.append(cat2)
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id
    
    # Approve application
    response = client.post(
        f'/api/business-expert/applications/{app_id}/approve',
        headers={'Authorization': f'Bearer {business_expert_token}'},
        json={"notes": "تایید شد"}
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['success'] is True
    
    # Check that company was created
    with app.app_context():
        company = Company.query.filter_by(phone_mobile="09131234567").first()
        assert company is not None
        assert company.name == "شرکت تایید"
        assert company.address == "اصفهان، خیابان چهارباغ"
        assert len(company.categories) == 2
        
        # Check application status
        app_record = ProviderApplication.query.get(app_id)
        assert app_record.status == 'approved'
        assert app_record.is_approved is True
        assert app_record.reviewed_at is not None


def test_reject_application(client, business_expert_token, app):
    """Test rejecting an application"""
    # Create test application
    with app.app_context():
        app_record = ProviderApplication(
            company_name="شرکت رد شده",
            representative_first_name="رضا",
            representative_last_name="محمدی",
            address="شیراز",
            phone_mobile="09171234567",
            latitude=29.5918,
            longitude=52.5836,
            status='pending'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id
    
    # Reject application
    response = client.post(
        f'/api/business-expert/applications/{app_id}/reject',
        headers={'Authorization': f'Bearer {business_expert_token}'},
        json={"notes": "اطلاعات ناقص است"}
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['success'] is True
    
    # Check application status
    with app.app_context():
        app_record = ProviderApplication.query.get(app_id)
        assert app_record.status == 'rejected'
        assert app_record.is_approved is False
        assert app_record.review_notes == "اطلاعات ناقص است"
        assert app_record.reviewed_at is not None


def test_reject_application_requires_notes(client, business_expert_token, app):
    """Test that rejecting requires notes"""
    # Create test application
    with app.app_context():
        app_record = ProviderApplication(
            company_name="شرکت تست",
            representative_first_name="علی",
            representative_last_name="احمدی",
            address="تهران",
            phone_mobile="09123456789",
            latitude=35.6892,
            longitude=51.3890,
            status='pending'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id
    
    # Try to reject without notes
    response = client.post(
        f'/api/business-expert/applications/{app_id}/reject',
        headers={'Authorization': f'Bearer {business_expert_token}'},
        json={}
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'توضیحات' in response_data['error']


def test_cannot_approve_already_processed_application(client, business_expert_token, app):
    """Test that already processed applications cannot be approved again"""
    # Create approved application
    with app.app_context():
        app_record = ProviderApplication(
            company_name="شرکت تایید شده",
            representative_first_name="علی",
            representative_last_name="احمدی",
            address="تهران",
            phone_mobile="09123456789",
            latitude=35.6892,
            longitude=51.3890,
            status='approved',
            is_approved=True
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id
    
    # Try to approve again
    response = client.post(
        f'/api/business-expert/applications/{app_id}/approve',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'قبلاً پردازش شده' in response_data['error']


def test_dashboard_stats(client, business_expert_token, app):
    """Test business expert dashboard statistics"""
    # Create test data
    with app.app_context():
        # Pending applications
        for i in range(5):
            app_record = ProviderApplication(
                company_name=f"شرکت {i}",
                representative_first_name="علی",
                representative_last_name="احمدی",
                address="تهران",
                phone_mobile=f"0912345678{i}",
                latitude=35.6892,
                longitude=51.3890,
                status='pending'
            )
            db.session.add(app_record)
        
        # Approved today
        for i in range(3):
            app_record = ProviderApplication(
                company_name=f"شرکت تایید {i}",
                representative_first_name="محمد",
                representative_last_name="رضایی",
                address="اصفهان",
                phone_mobile=f"0913123456{i}",
                latitude=32.6546,
                longitude=51.6680,
                status='approved',
                is_approved=True,
                reviewed_at=datetime.now(timezone.utc)
            )
            db.session.add(app_record)
        
        # Active companies
        for i in range(7):
            company = Company(
                name=f"شرکت فعال {i}",
                address="تهران",
                phone_mobile=f"0914123456{i}",
                latitude=35.6892,
                longitude=51.3890,
                is_active=True
            )
            db.session.add(company)
        
        db.session.commit()
    
    response = client.get(
        '/api/business-expert/dashboard',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['success'] is True
    assert response_data['data']['pending_reviews'] == 5
    assert response_data['data']['approved_today'] == 3
    assert response_data['data']['total_companies'] == 7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

