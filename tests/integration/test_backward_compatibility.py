"""
Backward Compatibility Tests
تست‌های سازگاری با نسخه‌های قبلی

این فایل شامل تست‌های مربوط به:
1. پشتیبانی از فیلدهای قدیمی (Legacy Field Names)
2. سازگاری با API های قبلی
3. پشتیبانی همزمان از فیلدهای قدیمی و جدید
4. فرمت پاسخ‌های API
"""

import sys
import os
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.app import create_app, db
from backend.models.user import User
from backend.models.company import Company, Category
from backend.models.provider_application import ProviderApplication


class TestBackwardCompatibility:
    """Test backward compatibility for API"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key"
        })
        
        with app.app_context():
            db.create_all()
            
            # Create test admin
            admin = User(
                username="admin",
                email="admin@test.com",
                full_name="ادمین تست",
                role="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.flush()
            
            # Create Admin record
            from backend.models.user import Admin as AdminModel
            admin_record = AdminModel(user_id=admin.id)
            db.session.add(admin_record)
            
            # Create test business expert
            business_expert = User(
                username="business_expert",
                email="expert@test.com",
                full_name="کارشناس تست",
                role="business_expert"
            )
            business_expert.set_password("expert123")
            db.session.add(business_expert)
            db.session.flush()
            
            # Create BusinessExpert record
            from backend.models.user import BusinessExpert as BusinessExpertModel
            expert_record = BusinessExpertModel(user_id=business_expert.id, expertise_area="تست")
            db.session.add(expert_record)
            
            db.session.commit()
            
        yield app
        
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def business_expert_token(self, client):
        """Get business expert auth token"""
        response = client.post('/api/login', json={
            'username': 'business_expert',
            'password': 'expert123'
        })
        assert response.status_code == 200
        data = response.get_json()
        return data['token']
    
    @pytest.fixture
    def admin_token(self, client):
        """Get admin auth token"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 200
        data = response.get_json()
        return data['token']
    
    # =====================================================
    # Test 1: Legacy Field Names for Company Creation
    # =====================================================
    
    def test_company_creation_with_legacy_field_names(self, client, business_expert_token):
        """
        Test 1.1: ایجاد شرکت با استفاده از فیلدهای قدیمی
        Legacy fields: companyName, tel
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'companyName': 'شرکت تست قدیمی',  # Legacy field
                'tel': '09123456789',  # Legacy field
                'address': 'تهران، خیابان آزادی',
                'latitude': 35.6892,
                'longitude': 51.3890
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'id' in data['data']
    
    def test_company_creation_with_new_field_names(self, client, business_expert_token):
        """
        Test 1.2: ایجاد شرکت با استفاده از فیلدهای جدید
        New fields: name, phone
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت تست جدید',  # New field
                'phone': '09123456788',  # New field
                'address': 'تهران، خیابان ولیعصر',
                'latitude': 35.6892,
                'longitude': 51.3890
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'id' in data['data']
    
    def test_company_creation_with_mixed_field_names(self, client, business_expert_token):
        """
        Test 1.3: ایجاد شرکت با ترکیبی از فیلدهای قدیمی و جدید
        اگر هر دو ارائه شوند، فیلد جدید اولویت دارد
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت جدید',  # New field (should take priority)
                'companyName': 'شرکت قدیمی',  # Legacy field
                'phone': '09123456787',  # New field (should take priority)
                'tel': '09123456786',  # Legacy field
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_company_creation_legacy_field_only_companyName(self, client, business_expert_token):
        """
        Test 1.4: ایجاد شرکت فقط با companyName (بدون name)
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'companyName': 'شرکت فقط با نام قدیمی',
                'phone': '09123456785',
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_company_creation_legacy_field_only_tel(self, client, business_expert_token):
        """
        Test 1.5: ایجاد شرکت فقط با tel (بدون phone)
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت فقط با تلفن قدیمی',
                'tel': '09123456784',
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    # =====================================================
    # Test 2: Provider Application Legacy Fields
    # =====================================================
    
    def test_provider_application_with_legacy_fields(self, client):
        """
        Test 2.1: ثبت درخواست ارائه‌دهنده با فیلدهای قدیمی
        Legacy fields: companyName, phoneMobile, phoneLandline
        """
        response = client.post('/api/provider-applications', json={
            'companyName': 'شرکت درخواست قدیمی',
            'representativeFirstName': 'علی',
            'representativeLastName': 'محمدی',
            'address': 'تهران، خیابان انقلاب',
            'phoneMobile': '09123456783',
            'phoneLandline': '02112345678',
            'serviceDomain': 'تعمیرات موتور',
            'latitude': 35.6892,
            'longitude': 51.3890
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['status'] == 'pending'
    
    def test_provider_application_validation_legacy_phone_format(self, client):
        """
        Test 2.2: اعتبارسنجی فرمت شماره تلفن قدیمی
        """
        response = client.post('/api/provider-applications', json={
            'companyName': 'شرکت تست',
            'representativeFirstName': 'علی',
            'representativeLastName': 'محمدی',
            'address': 'تهران',
            'phoneMobile': '0912345678',  # Invalid format (too short)
            'serviceDomain': 'تعمیرات موتور',
            'latitude': 35.6892,
            'longitude': 51.3890
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    # =====================================================
    # Test 3: Response Format Backward Compatibility
    # =====================================================
    
    def test_response_format_has_success_field(self, client, business_expert_token):
        """
        Test 3.1: بررسی وجود فیلد success در پاسخ
        همه پاسخ‌ها باید دارای فیلد success باشند
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت تست',
                'phone': '09123456782',
                'address': 'تهران'
            }
        )
        
        data = response.get_json()
        assert 'success' in data
        assert isinstance(data['success'], bool)
    
    def test_response_format_error_structure(self, client, business_expert_token):
        """
        Test 3.2: بررسی ساختار پاسخ خطا
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                # Missing required fields
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_response_format_pagination_structure(self, client, business_expert_token):
        """
        Test 3.3: بررسی ساختار پاسخ صفحه‌بندی شده
        """
        # First create some applications
        with client.application.app_context():
            app1 = ProviderApplication(
                company_name='شرکت 1',
                representative_first_name='علی',
                representative_last_name='محمدی',
                address='تهران',
                phone_mobile='09123456781',
                service_domain='تعمیرات',
                latitude=35.6892,
                longitude=51.3890,
                status='pending'
            )
            db.session.add(app1)
            db.session.commit()
        
        response = client.get('/api/business-expert/applications?page=1&per_page=10',
            headers={'Authorization': f'Bearer {business_expert_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert 'data' in data
        assert 'pagination' in data
        assert 'page' in data['pagination']
        assert 'per_page' in data['pagination']
        assert 'total' in data['pagination']
    
    # =====================================================
    # Test 4: Field Mapping Consistency
    # =====================================================
    
    def test_field_mapping_companyName_to_name(self, client, business_expert_token, app):
        """
        Test 4.1: بررسی صحت تبدیل companyName به name
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'companyName': 'شرکت تبدیل نام',
                'phone': '09123456780',
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        company_id = data['data']['id']
        
        # Verify in database
        with app.app_context():
            company = db.session.get(Company, company_id)
            assert company is not None
            assert company.name == 'شرکت تبدیل نام'
    
    def test_field_mapping_tel_to_phone(self, client, business_expert_token, app):
        """
        Test 4.2: بررسی صحت تبدیل tel به phone
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت تبدیل تلفن',
                'tel': '09123456779',
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        company_id = data['data']['id']
        
        # Verify in database
        with app.app_context():
            company = db.session.get(Company, company_id)
            assert company is not None
            assert company.phone_mobile == '09123456779'
    
    # =====================================================
    # Test 5: Validation Backward Compatibility
    # =====================================================
    
    def test_validation_works_with_legacy_fields(self, client, business_expert_token):
        """
        Test 5.1: اعتبارسنجی با فیلدهای قدیمی
        """
        # Invalid phone number with legacy field
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت تست',
                'tel': '123456',  # Invalid format
                'address': 'تهران'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_validation_phone_format_legacy(self, client, business_expert_token):
        """
        Test 5.2: اعتبارسنجی فرمت شماره تلفن با فیلد قدیمی
        """
        # Test various invalid formats
        invalid_phones = [
            '912345678',      # Missing 0
            '9123456789',     # Missing 0
            '0812345678',     # Not starting with 09
            '091234567',      # Too short
            '09123456789a',   # Contains letter
        ]
        
        for phone in invalid_phones:
            response = client.post('/api/company', 
                headers={'Authorization': f'Bearer {business_expert_token}'},
                json={
                    'name': 'شرکت تست',
                    'tel': phone,
                    'address': 'تهران'
                }
            )
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
    
    # =====================================================
    # Test 6: Error Message Format Compatibility
    # =====================================================
    
    def test_error_message_format_persian(self, client, business_expert_token):
        """
        Test 6.1: بررسی فرمت پیام‌های خطا به فارسی
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'companyName': '',  # Empty name
                'phone': '09123456778'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # Error message should be in Persian
        assert any(persian_char in data['error'] for persian_char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
    
    def test_error_details_structure(self, client, business_expert_token):
        """
        Test 6.2: بررسی ساختار جزئیات خطا
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'ش',  # Too short
                'phone': '123'  # Invalid format
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # Should have details for validation errors
        if 'details' in data:
            assert isinstance(data['details'], list)
    
    # =====================================================
    # Test 7: Multiple Legacy Fields Combinations
    # =====================================================
    
    def test_all_legacy_fields_together(self, client, business_expert_token):
        """
        Test 7.1: استفاده از همه فیلدهای قدیمی با هم
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'companyName': 'شرکت کامل قدیمی',
                'tel': '09123456777',
                'address': 'تهران، خیابان انقلاب',
                'latitude': 35.6892,
                'longitude': 51.3890,
                'is_active': True
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_all_new_fields_together(self, client, business_expert_token):
        """
        Test 7.2: استفاده از همه فیلدهای جدید با هم
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت کامل جدید',
                'phone': '09123456776',
                'address': 'تهران، خیابان ولیعصر',
                'latitude': 35.6892,
                'longitude': 51.3890,
                'is_active': True
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    # =====================================================
    # Test 8: Endpoint Backward Compatibility
    # =====================================================
    
    def test_endpoint_still_supports_old_routes(self, client):
        """
        Test 8.1: بررسی پشتیبانی از مسیرهای قدیمی API
        """
        # Provider application endpoint should still work
        response = client.post('/api/provider-applications', json={
            'companyName': 'شرکت تست مسیر',
            'representativeFirstName': 'علی',
            'representativeLastName': 'محمدی',
            'address': 'تهران',
            'phoneMobile': '09123456775',
            'serviceDomain': 'تعمیرات',
            'latitude': 35.6892,
            'longitude': 51.3890
        })
        
        assert response.status_code == 201
    
    # =====================================================
    # Test 9: Data Type Compatibility
    # =====================================================
    
    def test_numeric_fields_accept_string_numbers(self, client, business_expert_token):
        """
        Test 9.1: بررسی پذیرش اعداد به صورت رشته
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت تست نوع داده',
                'phone': '09123456774',
                'address': 'تهران',
                'latitude': "35.6892",  # String instead of float
                'longitude': "51.3890"   # String instead of float
            }
        )
        
        # Should work or give clear validation error
        assert response.status_code in [201, 400]
    
    # =====================================================
    # Test 10: Optional Fields Backward Compatibility
    # =====================================================
    
    def test_optional_fields_can_be_omitted(self, client, business_expert_token):
        """
        Test 10.1: بررسی امکان حذف فیلدهای اختیاری
        """
        # Minimal required fields only
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'name': 'شرکت حداقلی',
                'phone': '09123456773'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_optional_legacy_fields_with_defaults(self, client, business_expert_token):
        """
        Test 10.2: بررسی مقادیر پیش‌فرض فیلدهای اختیاری
        """
        response = client.post('/api/company', 
            headers={'Authorization': f'Bearer {business_expert_token}'},
            json={
                'companyName': 'شرکت پیش‌فرض',
                'tel': '09123456772'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True


def print_test_summary():
    """Print test summary in Persian"""
    print("\n" + "="*80)
    print("خلاصه تست‌های Backward Compatibility")
    print("="*80)
    print("\n✅ دسته‌های تست شده:")
    print("1. ایجاد شرکت با فیلدهای قدیمی و جدید")
    print("2. درخواست ارائه‌دهنده با فیلدهای قدیمی")
    print("3. سازگاری فرمت پاسخ‌ها")
    print("4. سازگاری نگاشت فیلدها")
    print("5. سازگاری اعتبارسنجی")
    print("6. سازگاری فرمت پیام‌های خطا")
    print("7. ترکیب‌های مختلف فیلدها")
    print("8. سازگاری endpoint ها")
    print("9. سازگاری نوع داده‌ها")
    print("10. سازگاری فیلدهای اختیاری")
    print("\n" + "="*80)


if __name__ == "__main__":
    print_test_summary()
    print("\nبرای اجرای تست‌ها از دستور زیر استفاده کنید:")
    print("pytest test_backward_compatibility.py -v")
    print("\nبرای اجرای تست خاص:")
    print("pytest test_backward_compatibility.py::TestBackwardCompatibility::test_company_creation_with_legacy_field_names -v")

