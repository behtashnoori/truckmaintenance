"""
Integration Test for Complete Provider Application Flow
Tests the entire flow from submission to approval and company creation
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
    SECRET_KEY = 'test-secret-key-for-integration'


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
def business_expert_token(app):
    """Create business expert and return token"""
    import jwt
    
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
        user_id = user.id
        
        token = jwt.encode({
            'user_id': user_id,
            'username': 'business_expert',
            'role': 'business_expert',
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return token


def test_complete_provider_application_flow(client, business_expert_token, app):
    """
    Test complete flow:
    1. Provider submits application
    2. Application is saved to database
    3. Business expert retrieves pending applications
    4. Business expert approves application
    5. Company is created with correct data
    6. Application appears in dashboard stats
    """
    
    # Step 1: Provider submits application
    application_data = {
        "companyName": "شرکت حمل و نقل بزرگ",
        "representativeFirstName": "حسین",
        "representativeLastName": "محمدی",
        "address": "تهران، اتوبان آزادگان، کیلومتر 5",
        "phoneMobile": "09121234567",
        "phoneLandline": "02155667788",
        "serviceCategories": ["امداد جاده‌ای", "تعویض لاستیک", "یدک کش"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    submit_response = client.post(
        '/api/provider-applications',
        json=application_data
    )
    
    assert submit_response.status_code == 201
    submit_data = json.loads(submit_response.data)
    assert submit_data['success'] is True
    
    application_id = submit_data['data']['id']
    assert application_id is not None
    
    # Step 2: Verify application is saved to database
    with app.app_context():
        app_record = ProviderApplication.query.get(application_id)
        assert app_record is not None
        assert app_record.company_name == "شرکت حمل و نقل بزرگ"
        assert app_record.phone_mobile == "09121234567"
        assert app_record.status == 'pending'
        assert app_record.is_approved is False
        
        # Verify categories
        assert len(app_record.categories) == 3
        category_names = [cat.name for cat in app_record.categories]
        assert "امداد جاده‌ای" in category_names
        assert "تعویض لاستیک" in category_names
        assert "یدک کش" in category_names
    
    # Step 3: Business expert retrieves pending applications
    list_response = client.get(
        '/api/business-expert/applications',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert list_response.status_code == 200
    list_data = json.loads(list_response.data)
    assert len(list_data['data']) == 1
    assert list_data['data'][0]['id'] == application_id
    assert list_data['data'][0]['company_name'] == "شرکت حمل و نقل بزرگ"
    
    # Step 4: Business expert gets application details
    details_response = client.get(
        f'/api/business-expert/applications/{application_id}',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert details_response.status_code == 200
    details_data = json.loads(details_response.data)
    assert details_data['success'] is True
    assert details_data['data']['company_name'] == "شرکت حمل و نقل بزرگ"
    assert details_data['data']['phone_mobile'] == "09121234567"
    assert len(details_data['data']['service_categories']) == 3
    
    # Step 5: Business expert approves application
    approve_response = client.post(
        f'/api/business-expert/applications/{application_id}/approve',
        headers={'Authorization': f'Bearer {business_expert_token}'},
        json={"notes": "تایید شد. اطلاعات کامل است."}
    )
    
    assert approve_response.status_code == 200
    approve_data = json.loads(approve_response.data)
    assert approve_data['success'] is True
    
    # Step 6: Verify company was created
    with app.app_context():
        company = Company.query.filter_by(phone_mobile="09121234567").first()
        assert company is not None
        assert company.name == "شرکت حمل و نقل بزرگ"
        assert company.address == "تهران، اتوبان آزادگان، کیلومتر 5"
        assert company.phone_landline == "02155667788"
        assert company.latitude == 35.6892
        assert company.longitude == 51.3890
        assert company.is_active is True
        
        # Verify company has all categories
        assert len(company.categories) == 3
        company_category_names = [cat.name for cat in company.categories]
        assert "امداد جاده‌ای" in company_category_names
        assert "تعویض لاستیک" in company_category_names
        assert "یدک کش" in company_category_names
        
        # Verify application is marked as approved
        app_record = ProviderApplication.query.get(application_id)
        assert app_record.status == 'approved'
        assert app_record.is_approved is True
        assert app_record.reviewed_at is not None
        assert app_record.review_notes == "تایید شد. اطلاعات کامل است."
    
    # Step 7: Verify dashboard stats
    dashboard_response = client.get(
        '/api/business-expert/dashboard',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert dashboard_response.status_code == 200
    dashboard_data = json.loads(dashboard_response.data)
    assert dashboard_data['data']['pending_reviews'] == 0  # Application was approved
    assert dashboard_data['data']['approved_today'] == 1
    assert dashboard_data['data']['total_companies'] == 1


def test_multiple_applications_same_phone(client, business_expert_token, app):
    """
    Test that multiple applications with same phone number
    update the same company (not create duplicates)
    """
    
    # First application
    app1_data = {
        "companyName": "شرکت اول",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران، خیابان ولیعصر",
        "phoneMobile": "09123456789",
        "serviceCategories": ["امداد جاده‌ای"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    response1 = client.post('/api/provider-applications', json=app1_data)
    assert response1.status_code == 201
    app1_id = json.loads(response1.data)['data']['id']
    
    # Approve first application
    approve1 = client.post(
        f'/api/business-expert/applications/{app1_id}/approve',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    assert approve1.status_code == 200
    
    # Second application with same phone but additional category
    app2_data = {
        "companyName": "شرکت دوم",  # Different name but same phone
        "representativeFirstName": "محمد",
        "representativeLastName": "رضایی",
        "address": "تهران، خیابان انقلاب",
        "phoneMobile": "09123456789",  # Same phone
        "serviceCategories": ["تعویض لاستیک"],  # Different category
        "latitude": 35.7000,
        "longitude": 51.4000
    }
    
    response2 = client.post('/api/provider-applications', json=app2_data)
    assert response2.status_code == 201
    app2_id = json.loads(response2.data)['data']['id']
    
    # Approve second application
    approve2 = client.post(
        f'/api/business-expert/applications/{app2_id}/approve',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    assert approve2.status_code == 200
    
    # Verify only one company exists with both categories
    with app.app_context():
        companies = Company.query.filter_by(phone_mobile="09123456789").all()
        assert len(companies) == 1  # Only one company
        
        company = companies[0]
        assert len(company.categories) == 2  # Both categories
        
        category_names = [cat.name for cat in company.categories]
        assert "امداد جاده‌ای" in category_names
        assert "تعویض لاستیک" in category_names


def test_rejected_application_does_not_create_company(client, business_expert_token, app):
    """
    Test that rejecting an application does not create a company
    """
    
    # Submit application
    app_data = {
        "companyName": "شرکت رد شده",
        "representativeFirstName": "حسین",
        "representativeLastName": "کریمی",
        "address": "شیراز",
        "phoneMobile": "09171234567",
        "serviceCategories": ["امداد جاده‌ای"],
        "latitude": 29.5918,
        "longitude": 52.5836
    }
    
    response = client.post('/api/provider-applications', json=app_data)
    assert response.status_code == 201
    app_id = json.loads(response.data)['data']['id']
    
    # Reject application
    reject_response = client.post(
        f'/api/business-expert/applications/{app_id}/reject',
        headers={'Authorization': f'Bearer {business_expert_token}'},
        json={"notes": "اطلاعات ناقص است"}
    )
    assert reject_response.status_code == 200
    
    # Verify no company was created
    with app.app_context():
        company = Company.query.filter_by(phone_mobile="09171234567").first()
        assert company is None  # No company created
        
        # Verify application is rejected
        app_record = ProviderApplication.query.get(app_id)
        assert app_record.status == 'rejected'
        assert app_record.is_approved is False


def test_application_with_minimal_data(client, business_expert_token, app):
    """
    Test application with only required fields (no landline)
    """
    
    app_data = {
        "companyName": "شرکت مینیمال",
        "representativeFirstName": "رضا",
        "representativeLastName": "محمدی",
        "address": "مشهد",
        "phoneMobile": "09151234567",
        "serviceCategories": ["یدک کش"],
        "latitude": 36.2605,
        "longitude": 59.6168
    }
    
    response = client.post('/api/provider-applications', json=app_data)
    assert response.status_code == 201
    app_id = json.loads(response.data)['data']['id']
    
    # Approve
    approve_response = client.post(
        f'/api/business-expert/applications/{app_id}/approve',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    assert approve_response.status_code == 200
    
    # Verify company created without landline
    with app.app_context():
        company = Company.query.filter_by(phone_mobile="09151234567").first()
        assert company is not None
        assert company.phone_landline is None


def test_pagination_of_applications(client, business_expert_token, app):
    """
    Test pagination when retrieving applications list
    """
    
    # Create 25 applications
    with app.app_context():
        for i in range(25):
            app_record = ProviderApplication(
                company_name=f"شرکت {i}",
                representative_first_name="علی",
                representative_last_name="احمدی",
                address="تهران",
                phone_mobile=f"091234567{i:02d}",
                latitude=35.6892,
                longitude=51.3890,
                status='pending'
            )
            db.session.add(app_record)
        db.session.commit()
    
    # Get first page (default 20 per page)
    response = client.get(
        '/api/business-expert/applications?page=1&per_page=20',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 20
    assert data['pagination']['total'] == 25
    assert data['pagination']['pages'] == 2
    
    # Get second page
    response2 = client.get(
        '/api/business-expert/applications?page=2&per_page=20',
        headers={'Authorization': f'Bearer {business_expert_token}'}
    )
    
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert len(data2['data']) == 5  # Remaining 5 items


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

