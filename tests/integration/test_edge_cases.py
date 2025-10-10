"""
Comprehensive Edge Cases Testing
تست‌های جامع برای موارد استثنایی و حاشیه‌ای

این تست نیاز به سرور در حال اجرا دارد:
python run_backend.py
"""

import requests
import json
from typing import Dict, Any, Optional

# Base URL for API
BASE_URL = "http://127.0.0.1:5000/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# Global variables
admin_token = None
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_test(test_name: str, result: str, details: str = ""):
    """Print test result"""
    test_results["total"] += 1
    status = "✅ PASS" if result == "PASS" else "❌ FAIL"
    
    if result == "PASS":
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {details}")
    
    print(f"{status} - {test_name}")
    if details:
        print(f"    Details: {details}")


def make_request(method: str, endpoint: str, token: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
    """Make HTTP request with optional token"""
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if data is not None:
            headers["Content-Type"] = "application/json"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except Exception as e:
        print(f"    Request error: {str(e)}")
        return None


def get_admin_token():
    """Get admin token for authentication"""
    global admin_token
    
    if admin_token:
        return admin_token
    
    response = make_request("POST", "/auth/login", data=ADMIN_CREDENTIALS)
    if response and response.status_code == 200:
        admin_token = response.json()["token"]
        return admin_token
    return None


# ==========================================
# Authentication Edge Cases
# ==========================================

def test_login_with_empty_username():
    """Test: ورود با نام کاربری خالی"""
    response = make_request("POST", "/auth/login", data={
        "username": "",
        "password": "SomePassword123"
    })
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False:
            print_test("ورود با نام کاربری خالی", "PASS", "Correctly rejected empty username")
            return
    
    print_test("ورود با نام کاربری خالی", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_login_with_empty_password():
    """Test: ورود با رمز عبور خالی"""
    response = make_request("POST", "/auth/login", data={
        "username": "admin",
        "password": ""
    })
    
    if response and response.status_code in [400, 401]:
        data = response.json()
        if data.get('success') is False:
            print_test("ورود با رمز عبور خالی", "PASS", "Correctly rejected empty password")
            return
    
    print_test("ورود با رمز عبور خالی", "FAIL", f"Expected 400/401, got {response.status_code if response else 'No response'}")


def test_login_with_null_values():
    """Test: ورود با مقادیر null"""
    response = make_request("POST", "/auth/login", data={
        "username": None,
        "password": None
    })
    
    if response and response.status_code in [400, 401]:
        data = response.json()
        if data.get('success') is False:
            print_test("ورود با مقادیر null", "PASS", "Correctly rejected null values")
            return
    
    print_test("ورود با مقادیر null", "FAIL", f"Expected 400/401, got {response.status_code if response else 'No response'}")


def test_login_with_missing_fields():
    """Test: ورود بدون فیلدهای اجباری"""
    response = make_request("POST", "/auth/login", data={})
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False:
            print_test("ورود بدون فیلدهای اجباری", "PASS", "Correctly rejected missing fields")
            return
    
    print_test("ورود بدون فیلدهای اجباری", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_login_with_very_long_username():
    """Test: ورود با نام کاربری بسیار طولانی"""
    response = make_request("POST", "/auth/login", data={
        "username": "a" * 1000,
        "password": "Password123"
    })
    
    if response and response.status_code in [400, 401]:
        data = response.json()
        if data.get('success') is False:
            print_test("ورود با نام کاربری بسیار طولانی", "PASS", "Correctly handled very long username")
            return
    
    print_test("ورود با نام کاربری بسیار طولانی", "FAIL", f"Expected 400/401, got {response.status_code if response else 'No response'}")


def test_login_with_sql_injection_attempt():
    """Test: تلاش برای SQL Injection"""
    response = make_request("POST", "/auth/login", data={
        "username": "'; DROP TABLE users; --",
        "password": "Password123"
    })
    
    if response and response.status_code == 401:
        data = response.json()
        if data.get('success') is False:
            print_test("جلوگیری از SQL Injection", "PASS", "SQL injection attempt safely handled")
            return
    
    print_test("جلوگیری از SQL Injection", "FAIL", f"Expected 401, got {response.status_code if response else 'No response'}")


def test_get_current_user_without_token():
    """Test: دریافت اطلاعات کاربر بدون توکن"""
    response = make_request("GET", "/auth/me")
    
    if response and response.status_code == 401:
        data = response.json()
        if data.get('success') is False and 'توکن' in data.get('error', ''):
            print_test("دریافت کاربر بدون توکن", "PASS", "Correctly requires authentication")
            return
    
    print_test("دریافت کاربر بدون توکن", "FAIL", f"Expected 401, got {response.status_code if response else 'No response'}")


def test_get_current_user_with_invalid_token():
    """Test: دریافت اطلاعات کاربر با توکن نامعتبر"""
    response = make_request("GET", "/auth/me", token="invalid_token_12345")
    
    if response and response.status_code == 401:
        data = response.json()
        if data.get('success') is False:
            print_test("دریافت کاربر با توکن نامعتبر", "PASS", "Correctly rejected invalid token")
            return
    
    print_test("دریافت کاربر با توکن نامعتبر", "FAIL", f"Expected 401, got {response.status_code if response else 'No response'}")


# ==========================================
# User Management Edge Cases
# ==========================================

def test_create_user_with_empty_username():
    """Test: ایجاد کاربر با نام کاربری خالی"""
    token = get_admin_token()
    if not token:
        print_test("ایجاد کاربر با نام کاربری خالی", "FAIL", "Could not get admin token")
        return
    
    response = make_request("POST", "/auth/users", token=token, data={
        "username": "",
        "password": "Password@123",
        "email": "test@test.com",
        "full_name": "Test User",
        "role": "user"
    })
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False:
            print_test("ایجاد کاربر با نام کاربری خالی", "PASS", "Correctly rejected empty username")
            return
    
    print_test("ایجاد کاربر با نام کاربری خالی", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_create_user_with_invalid_email():
    """Test: ایجاد کاربر با ایمیل نامعتبر"""
    token = get_admin_token()
    if not token:
        print_test("ایجاد کاربر با ایمیل نامعتبر", "FAIL", "Could not get admin token")
        return
    
    response = make_request("POST", "/auth/users", token=token, data={
        "username": "newuser",
        "password": "Password@123",
        "email": "invalid-email",
        "full_name": "Test User",
        "role": "user"
    })
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False:
            print_test("ایجاد کاربر با ایمیل نامعتبر", "PASS", "Correctly rejected invalid email")
            return
    
    print_test("ایجاد کاربر با ایمیل نامعتبر", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_create_user_with_weak_password():
    """Test: ایجاد کاربر با رمز عبور ضعیف"""
    token = get_admin_token()
    if not token:
        print_test("ایجاد کاربر با رمز عبور ضعیف", "FAIL", "Could not get admin token")
        return
    
    response = make_request("POST", "/auth/users", token=token, data={
        "username": "newuser_weak",
        "password": "123",
        "email": "test@test.com",
        "full_name": "Test User",
        "role": "user"
    })
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False:
            print_test("ایجاد کاربر با رمز عبور ضعیف", "PASS", "Correctly rejected weak password")
            return
    
    print_test("ایجاد کاربر با رمز عبور ضعیف", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_create_user_with_invalid_role():
    """Test: ایجاد کاربر با نقش نامعتبر"""
    token = get_admin_token()
    if not token:
        print_test("ایجاد کاربر با نقش نامعتبر", "FAIL", "Could not get admin token")
        return
    
    response = make_request("POST", "/auth/users", token=token, data={
        "username": "newuser_invalid",
        "password": "Password@123",
        "email": "test@test.com",
        "full_name": "Test User",
        "role": "invalid_role"
    })
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False and 'نقش' in data.get('error', ''):
            print_test("ایجاد کاربر با نقش نامعتبر", "PASS", "Correctly rejected invalid role")
            return
    
    print_test("ایجاد کاربر با نقش نامعتبر", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_update_nonexistent_user():
    """Test: بروزرسانی کاربر غیرموجود"""
    token = get_admin_token()
    if not token:
        print_test("بروزرسانی کاربر غیرموجود", "FAIL", "Could not get admin token")
        return
    
    response = make_request("PUT", "/admin/users/99999", token=token, data={
        "full_name": "Updated Name"
    })
    
    if response and response.status_code == 404:
        data = response.json()
        if data.get('success') is False and 'یافت نشد' in data.get('error', ''):
            print_test("بروزرسانی کاربر غیرموجود", "PASS", "Correctly handled nonexistent user")
            return
    
    print_test("بروزرسانی کاربر غیرموجود", "FAIL", f"Expected 404, got {response.status_code if response else 'No response'}")


def test_delete_nonexistent_user():
    """Test: حذف کاربر غیرموجود"""
    token = get_admin_token()
    if not token:
        print_test("حذف کاربر غیرموجود", "FAIL", "Could not get admin token")
        return
    
    response = make_request("DELETE", "/admin/users/99999", token=token)
    
    if response and response.status_code == 404:
        data = response.json()
        if data.get('success') is False:
            print_test("حذف کاربر غیرموجود", "PASS", "Correctly handled nonexistent user")
            return
    
    print_test("حذف کاربر غیرموجود", "FAIL", f"Expected 404, got {response.status_code if response else 'No response'}")


# ==========================================
# Pagination Edge Cases
# ==========================================

def test_get_users_with_negative_page():
    """Test: دریافت کاربران با شماره صفحه منفی"""
    token = get_admin_token()
    if not token:
        print_test("دریافت کاربران با صفحه منفی", "FAIL", "Could not get admin token")
        return
    
    response = make_request("GET", "/auth/users?page=-1", token=token)
    
    # Should handle gracefully (either error or default to page 1)
    if response and response.status_code in [200, 400]:
        print_test("دریافت کاربران با صفحه منفی", "PASS", "Handled negative page number gracefully")
        return
    
    print_test("دریافت کاربران با صفحه منفی", "FAIL", f"Expected 200/400, got {response.status_code if response else 'No response'}")


def test_get_users_with_zero_page():
    """Test: دریافت کاربران با صفحه صفر"""
    token = get_admin_token()
    if not token:
        print_test("دریافت کاربران با صفحه صفر", "FAIL", "Could not get admin token")
        return
    
    response = make_request("GET", "/auth/users?page=0", token=token)
    
    if response and response.status_code in [200, 400]:
        print_test("دریافت کاربران با صفحه صفر", "PASS", "Handled zero page number gracefully")
        return
    
    print_test("دریافت کاربران با صفحه صفر", "FAIL", f"Expected 200/400, got {response.status_code if response else 'No response'}")


def test_get_users_with_excessive_per_page():
    """Test: دریافت کاربران با تعداد بیش از حد"""
    token = get_admin_token()
    if not token:
        print_test("دریافت کاربران با per_page بیش از حد", "FAIL", "Could not get admin token")
        return
    
    response = make_request("GET", "/auth/users?per_page=10000", token=token)
    
    if response and response.status_code == 200:
        data = response.json()
        # Should limit to reasonable number
        if data.get('success') is not False:
            print_test("دریافت کاربران با per_page بیش از حد", "PASS", "Handled excessive per_page value")
            return
    
    print_test("دریافت کاربران با per_page بیش از حد", "FAIL", f"Expected 200, got {response.status_code if response else 'No response'}")


# ==========================================
# Application Management Edge Cases
# ==========================================

def test_review_nonexistent_application():
    """Test: بررسی درخواست غیرموجود"""
    token = get_admin_token()
    if not token:
        print_test("بررسی درخواست غیرموجود", "FAIL", "Could not get admin token")
        return
    
    response = make_request("POST", "/admin/applications/99999/review", token=token, data={
        "is_approved": True,
        "review_notes": "Test notes"
    })
    
    if response and response.status_code == 404:
        data = response.json()
        if data.get('success') is False:
            print_test("بررسی درخواست غیرموجود", "PASS", "Correctly handled nonexistent application")
            return
    
    print_test("بررسی درخواست غیرموجود", "FAIL", f"Expected 404, got {response.status_code if response else 'No response'}")


def test_review_application_with_missing_data():
    """Test: بررسی درخواست بدون داده‌های لازم"""
    token = get_admin_token()
    if not token:
        print_test("بررسی درخواست بدون داده", "FAIL", "Could not get admin token")
        return
    
    response = make_request("POST", "/admin/applications/1/review", token=token, data={})
    
    if response and response.status_code == 400:
        data = response.json()
        if data.get('success') is False:
            print_test("بررسی درخواست بدون داده", "PASS", "Correctly rejected missing data")
            return
    
    print_test("بررسی درخواست بدون داده", "FAIL", f"Expected 400, got {response.status_code if response else 'No response'}")


def test_delete_nonexistent_application():
    """Test: حذف درخواست غیرموجود"""
    token = get_admin_token()
    if not token:
        print_test("حذف درخواست غیرموجود", "FAIL", "Could not get admin token")
        return
    
    response = make_request("DELETE", "/admin/applications/99999", token=token)
    
    if response and response.status_code == 404:
        data = response.json()
        if data.get('success') is False:
            print_test("حذف درخواست غیرموجود", "PASS", "Correctly handled nonexistent application")
            return
    
    print_test("حذف درخواست غیرموجود", "FAIL", f"Expected 404, got {response.status_code if response else 'No response'}")


# ==========================================
# Authorization Edge Cases
# ==========================================

def test_non_admin_access_admin_endpoint():
    """Test: دسترسی غیرادمین به endpoint ادمین"""
    # First, try to create a regular user and get token
    # For now, we'll just test with no token
    response = make_request("GET", "/auth/users")
    
    if response and response.status_code == 401:
        data = response.json()
        if data.get('success') is False:
            print_test("دسترسی غیرمجاز به endpoint ادمین", "PASS", "Correctly blocked unauthorized access")
            return
    
    print_test("دسترسی غیرمجاز به endpoint ادمین", "FAIL", f"Expected 401, got {response.status_code if response else 'No response'}")


# ==========================================
# Input Validation Edge Cases
# ==========================================

def test_json_with_extra_fields():
    """Test: JSON با فیلدهای اضافی"""
    response = make_request("POST", "/auth/login", data={
        "username": "admin",
        "password": "admin123",
        "extra_field": "should_be_ignored",
        "another_field": 12345
    })
    
    # Should ignore extra fields and process normally
    if response and response.status_code == 200:
        print_test("JSON با فیلدهای اضافی", "PASS", "Correctly ignored extra fields")
        return
    
    print_test("JSON با فیلدهای اضافی", "FAIL", f"Expected 200, got {response.status_code if response else 'No response'}")


# ==========================================
# Main Test Runner
# ==========================================

def run_all_tests():
    """Run all edge case tests"""
    print("\n" + "="*80)
    print("  EDGE CASES COMPREHENSIVE TEST SUITE")
    print("  تست‌های جامع موارد استثنایی")
    print("="*80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/public/health")
        if response.status_code != 200:
            print("\n❌ سرور در دسترس نیست! لطفاً ابتدا سرور را اجرا کنید:")
            print("   python run_backend.py")
            return
    except:
        print("\n❌ سرور در دسترس نیست! لطفاً ابتدا سرور را اجرا کنید:")
        print("   python run_backend.py")
        return
    
    print("\n✅ سرور در حال اجرا است\n")
    
    # Authentication Edge Cases
    print_section("Authentication Edge Cases - موارد استثنایی احراز هویت")
    test_login_with_empty_username()
    test_login_with_empty_password()
    test_login_with_null_values()
    test_login_with_missing_fields()
    test_login_with_very_long_username()
    test_login_with_sql_injection_attempt()
    test_get_current_user_without_token()
    test_get_current_user_with_invalid_token()
    
    # User Management Edge Cases
    print_section("User Management Edge Cases - موارد استثنایی مدیریت کاربران")
    test_create_user_with_empty_username()
    test_create_user_with_invalid_email()
    test_create_user_with_weak_password()
    test_create_user_with_invalid_role()
    test_update_nonexistent_user()
    test_delete_nonexistent_user()
    
    # Pagination Edge Cases
    print_section("Pagination Edge Cases - موارد استثنایی صفحه‌بندی")
    test_get_users_with_negative_page()
    test_get_users_with_zero_page()
    test_get_users_with_excessive_per_page()
    
    # Application Management Edge Cases
    print_section("Application Management Edge Cases - موارد استثنایی مدیریت درخواست‌ها")
    test_review_nonexistent_application()
    test_review_application_with_missing_data()
    test_delete_nonexistent_application()
    
    # Authorization Edge Cases
    print_section("Authorization Edge Cases - موارد استثنایی مجوزدهی")
    test_non_admin_access_admin_endpoint()
    
    # Input Validation Edge Cases
    print_section("Input Validation Edge Cases - موارد استثنایی اعتبارسنجی ورودی")
    test_json_with_extra_fields()
    
    # Print final summary
    print("\n" + "="*80)
    print("  TEST SUMMARY - خلاصه نتایج تست")
    print("="*80)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed']/test_results['total']*100):.1f}%")
    
    if test_results['failed'] > 0:
        print("\n" + "="*80)
        print("  FAILED TESTS - تست‌های ناموفق")
        print("="*80)
        for error in test_results['errors']:
            print(f"  ❌ {error}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    run_all_tests()
