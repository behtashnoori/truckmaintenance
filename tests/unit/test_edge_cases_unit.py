"""
Unit Tests for Edge Cases
تست‌های واحد برای موارد استثنایی

این تست نیازی به سرور جداگانه ندارد و مستقیماً از Flask test client استفاده می‌کند.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, db
from models.user import User, Admin, BusinessExpert
import json


class EdgeCasesTest:
    """Test class for edge cases"""
    
    def __init__(self):
        """Initialize test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_users()
        
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def _create_test_users(self):
        """Create test users for authentication"""
        # Admin user
        admin_user = User(
            username="admin",
            email="admin@test.com",
            full_name="Admin Test",
            role="admin",
            is_active=True
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.flush()
        
        admin_record = Admin(user_id=admin_user.id, permissions={"all": True})
        db.session.add(admin_record)
        
        # Business Expert user
        expert_user = User(
            username="expert",
            email="expert@test.com",
            full_name="Expert Test",
            role="business_expert",
            is_active=True
        )
        expert_user.set_password("expert123")
        db.session.add(expert_user)
        db.session.flush()
        
        expert_record = BusinessExpert(user_id=expert_user.id, expertise_area="IT")
        db.session.add(expert_record)
        
        db.session.commit()
    
    def _get_token(self, username, password):
        """Helper to get JWT token"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({"username": username, "password": password}),
            content_type='application/json'
        )
        if response.status_code == 200:
            return response.get_json()['token']
        return None
    
    def print_section(self, title):
        """Print a formatted section header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
    
    def print_test(self, test_name, result, details=""):
        """Print test result"""
        self.test_results["total"] += 1
        status = "✅ PASS" if result == "PASS" else "❌ FAIL"
        
        if result == "PASS":
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
        
        print(f"{status} - {test_name}")
        if details and result == "FAIL":
            print(f"    Details: {details}")
    
    # ==========================================
    # Authentication Edge Cases
    # ==========================================
    
    def test_login_with_empty_username(self):
        """Test: ورود با نام کاربری خالی"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({"username": "", "password": "SomePassword123"}),
            content_type='application/json'
        )
        
        if response.status_code == 400:
            data = response.get_json()
            if data.get('success') is False:
                self.print_test("ورود با نام کاربری خالی", "PASS")
                return
        
        self.print_test("ورود با نام کاربری خالی", "FAIL", 
                       f"Expected 400, got {response.status_code}")
    
    def test_login_with_empty_password(self):
        """Test: ورود با رمز عبور خالی"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({"username": "admin", "password": ""}),
            content_type='application/json'
        )
        
        if response.status_code in [400, 401]:
            data = response.get_json()
            if data.get('success') is False:
                self.print_test("ورود با رمز عبور خالی", "PASS")
                return
        
        self.print_test("ورود با رمز عبور خالی", "FAIL",
                       f"Expected 400/401, got {response.status_code}")
    
    def test_login_with_null_values(self):
        """Test: ورود با مقادیر null"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({"username": None, "password": None}),
            content_type='application/json'
        )
        
        if response.status_code in [400, 401]:
            self.print_test("ورود با مقادیر null", "PASS")
            return
        
        self.print_test("ورود با مقادیر null", "FAIL",
                       f"Expected 400/401, got {response.status_code}")
    
    def test_login_with_missing_fields(self):
        """Test: ورود بدون فیلدهای اجباری"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        if response.status_code == 400:
            self.print_test("ورود بدون فیلدهای اجباری", "PASS")
            return
        
        self.print_test("ورود بدون فیلدهای اجباری", "FAIL",
                       f"Expected 400, got {response.status_code}")
    
    def test_login_with_very_long_username(self):
        """Test: ورود با نام کاربری بسیار طولانی"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({"username": "a" * 1000, "password": "Password123"}),
            content_type='application/json'
        )
        
        if response.status_code in [400, 401]:
            self.print_test("ورود با نام کاربری بسیار طولانی", "PASS")
            return
        
        self.print_test("ورود با نام کاربری بسیار طولانی", "FAIL",
                       f"Expected 400/401, got {response.status_code}")
    
    def test_login_with_sql_injection_attempt(self):
        """Test: تلاش برای SQL Injection"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({"username": "'; DROP TABLE users; --", "password": "Password123"}),
            content_type='application/json'
        )
        
        if response.status_code == 401:
            data = response.get_json()
            if data.get('success') is False:
                self.print_test("جلوگیری از SQL Injection", "PASS")
                return
        
        self.print_test("جلوگیری از SQL Injection", "FAIL",
                       f"Expected 401, got {response.status_code}")
    
    def test_get_current_user_without_token(self):
        """Test: دریافت اطلاعات کاربر بدون توکن"""
        response = self.client.get('/api/auth/me')
        
        if response.status_code == 401:
            data = response.get_json()
            if data.get('success') is False:
                self.print_test("دریافت کاربر بدون توکن", "PASS")
                return
        
        self.print_test("دریافت کاربر بدون توکن", "FAIL",
                       f"Expected 401, got {response.status_code}")
    
    def test_get_current_user_with_invalid_token(self):
        """Test: دریافت اطلاعات کاربر با توکن نامعتبر"""
        response = self.client.get('/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token_12345'}
        )
        
        if response.status_code == 401:
            self.print_test("دریافت کاربر با توکن نامعتبر", "PASS")
            return
        
        self.print_test("دریافت کاربر با توکن نامعتبر", "FAIL",
                       f"Expected 401, got {response.status_code}")
    
    # ==========================================
    # User Management Edge Cases
    # ==========================================
    
    def test_create_user_with_empty_username(self):
        """Test: ایجاد کاربر با نام کاربری خالی"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("ایجاد کاربر با نام کاربری خالی", "FAIL", "Could not get admin token")
            return
        
        response = self.client.post('/api/auth/users',
            data=json.dumps({
                "username": "",
                "password": "Password@123",
                "email": "test@test.com",
                "full_name": "Test User",
                "role": "user"
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 400:
            self.print_test("ایجاد کاربر با نام کاربری خالی", "PASS")
            return
        
        self.print_test("ایجاد کاربر با نام کاربری خالی", "FAIL",
                       f"Expected 400, got {response.status_code}")
    
    def test_create_user_with_invalid_email(self):
        """Test: ایجاد کاربر با ایمیل نامعتبر"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("ایجاد کاربر با ایمیل نامعتبر", "FAIL", "Could not get admin token")
            return
        
        response = self.client.post('/api/auth/users',
            data=json.dumps({
                "username": "newuser_email",
                "password": "Password@123",
                "email": "invalid-email",
                "full_name": "Test User",
                "role": "user"
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 400:
            self.print_test("ایجاد کاربر با ایمیل نامعتبر", "PASS")
            return
        
        self.print_test("ایجاد کاربر با ایمیل نامعتبر", "FAIL",
                       f"Expected 400, got {response.status_code}")
    
    def test_create_user_with_weak_password(self):
        """Test: ایجاد کاربر با رمز عبور ضعیف"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("ایجاد کاربر با رمز عبور ضعیف", "FAIL", "Could not get admin token")
            return
        
        response = self.client.post('/api/auth/users',
            data=json.dumps({
                "username": "newuser_weak",
                "password": "123",
                "email": "test@test.com",
                "full_name": "Test User",
                "role": "user"
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 400:
            self.print_test("ایجاد کاربر با رمز عبور ضعیف", "PASS")
            return
        
        self.print_test("ایجاد کاربر با رمز عبور ضعیف", "FAIL",
                       f"Expected 400, got {response.status_code}")
    
    def test_create_user_with_invalid_role(self):
        """Test: ایجاد کاربر با نقش نامعتبر"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("ایجاد کاربر با نقش نامعتبر", "FAIL", "Could not get admin token")
            return
        
        response = self.client.post('/api/auth/users',
            data=json.dumps({
                "username": "newuser_invalid_role",
                "password": "Password@123",
                "email": "test@test.com",
                "full_name": "Test User",
                "role": "invalid_role"
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 400:
            self.print_test("ایجاد کاربر با نقش نامعتبر", "PASS")
            return
        
        self.print_test("ایجاد کاربر با نقش نامعتبر", "FAIL",
                       f"Expected 400, got {response.status_code}")
    
    def test_update_nonexistent_user(self):
        """Test: بروزرسانی کاربر غیرموجود"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("بروزرسانی کاربر غیرموجود", "FAIL", "Could not get admin token")
            return
        
        response = self.client.put('/api/admin/users/99999',
            data=json.dumps({"full_name": "Updated Name"}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 404:
            self.print_test("بروزرسانی کاربر غیرموجود", "PASS")
            return
        
        self.print_test("بروزرسانی کاربر غیرموجود", "FAIL",
                       f"Expected 404, got {response.status_code}")
    
    def test_delete_nonexistent_user(self):
        """Test: حذف کاربر غیرموجود"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("حذف کاربر غیرموجود", "FAIL", "Could not get admin token")
            return
        
        response = self.client.delete('/api/admin/users/99999',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 404:
            self.print_test("حذف کاربر غیرموجود", "PASS")
            return
        
        self.print_test("حذف کاربر غیرموجود", "FAIL",
                       f"Expected 404, got {response.status_code}")
    
    # ==========================================
    # Pagination Edge Cases
    # ==========================================
    
    def test_get_users_with_negative_page(self):
        """Test: دریافت کاربران با شماره صفحه منفی"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("دریافت کاربران با صفحه منفی", "FAIL", "Could not get admin token")
            return
        
        response = self.client.get('/api/auth/users?page=-1',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code in [200, 400]:
            self.print_test("دریافت کاربران با صفحه منفی", "PASS")
            return
        
        self.print_test("دریافت کاربران با صفحه منفی", "FAIL",
                       f"Expected 200/400, got {response.status_code}")
    
    def test_get_users_with_zero_page(self):
        """Test: دریافت کاربران با صفحه صفر"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("دریافت کاربران با صفحه صفر", "FAIL", "Could not get admin token")
            return
        
        response = self.client.get('/api/auth/users?page=0',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code in [200, 400]:
            self.print_test("دریافت کاربران با صفحه صفر", "PASS")
            return
        
        self.print_test("دریافت کاربران با صفحه صفر", "FAIL",
                       f"Expected 200/400, got {response.status_code}")
    
    def test_get_users_with_excessive_per_page(self):
        """Test: دریافت کاربران با تعداد بیش از حد"""
        token = self._get_token("admin", "admin123")
        if not token:
            self.print_test("دریافت کاربران با per_page بیش از حد", "FAIL", "Could not get admin token")
            return
        
        response = self.client.get('/api/auth/users?per_page=10000',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            self.print_test("دریافت کاربران با per_page بیش از حد", "PASS")
            return
        
        self.print_test("دریافت کاربران با per_page بیش از حد", "FAIL",
                       f"Expected 200, got {response.status_code}")
    
    # ==========================================
    # Authorization Edge Cases
    # ==========================================
    
    def test_non_admin_access_admin_endpoint(self):
        """Test: دسترسی غیرادمین به endpoint ادمین"""
        response = self.client.get('/api/auth/users')
        
        if response.status_code == 401:
            self.print_test("دسترسی غیرمجاز به endpoint ادمین", "PASS")
            return
        
        self.print_test("دسترسی غیرمجاز به endpoint ادمین", "FAIL",
                       f"Expected 401, got {response.status_code}")
    
    # ==========================================
    # Input Validation Edge Cases
    # ==========================================
    
    def test_json_with_extra_fields(self):
        """Test: JSON با فیلدهای اضافی"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                "username": "admin",
                "password": "admin123",
                "extra_field": "should_be_ignored",
                "another_field": 12345
            }),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            self.print_test("JSON با فیلدهای اضافی", "PASS")
            return
        
        self.print_test("JSON با فیلدهای اضافی", "FAIL",
                       f"Expected 200, got {response.status_code}")
    
    def test_malformed_json(self):
        """Test: JSON نامعتبر"""
        response = self.client.post('/api/auth/login',
            data="not a valid json",
            content_type='application/json'
        )
        
        if response.status_code in [400, 500]:
            self.print_test("JSON نامعتبر", "PASS")
            return
        
        self.print_test("JSON نامعتبر", "FAIL",
                       f"Expected 400/500, got {response.status_code}")
    
    # ==========================================
    # Main Test Runner
    # ==========================================
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("\n" + "="*80)
        print("  EDGE CASES COMPREHENSIVE TEST SUITE")
        print("  تست‌های جامع موارد استثنایی")
        print("="*80)
        
        # Authentication Edge Cases
        self.print_section("Authentication Edge Cases - موارد استثنایی احراز هویت")
        self.test_login_with_empty_username()
        self.test_login_with_empty_password()
        self.test_login_with_null_values()
        self.test_login_with_missing_fields()
        self.test_login_with_very_long_username()
        self.test_login_with_sql_injection_attempt()
        self.test_get_current_user_without_token()
        self.test_get_current_user_with_invalid_token()
        
        # User Management Edge Cases
        self.print_section("User Management Edge Cases - موارد استثنایی مدیریت کاربران")
        self.test_create_user_with_empty_username()
        self.test_create_user_with_invalid_email()
        self.test_create_user_with_weak_password()
        self.test_create_user_with_invalid_role()
        self.test_update_nonexistent_user()
        self.test_delete_nonexistent_user()
        
        # Pagination Edge Cases
        self.print_section("Pagination Edge Cases - موارد استثنایی صفحه‌بندی")
        self.test_get_users_with_negative_page()
        self.test_get_users_with_zero_page()
        self.test_get_users_with_excessive_per_page()
        
        # Authorization Edge Cases
        self.print_section("Authorization Edge Cases - موارد استثنایی مجوزدهی")
        self.test_non_admin_access_admin_endpoint()
        
        # Input Validation Edge Cases
        self.print_section("Input Validation Edge Cases - موارد استثنایی اعتبارسنجی ورودی")
        self.test_json_with_extra_fields()
        self.test_malformed_json()
        
        # Print final summary
        print("\n" + "="*80)
        print("  TEST SUMMARY - خلاصه نتایج تست")
        print("="*80)
        print(f"Total Tests: {self.test_results['total']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        if self.test_results['total'] > 0:
            print(f"Success Rate: {(self.test_results['passed']/self.test_results['total']*100):.1f}%")
        
        if self.test_results['failed'] > 0:
            print("\n" + "="*80)
            print("  FAILED TESTS - تست‌های ناموفق")
            print("="*80)
            for error in self.test_results['errors']:
                print(f"  ❌ {error}")
        
        print("\n" + "="*80)
        
        return self.test_results


if __name__ == "__main__":
    tester = EdgeCasesTest()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

