#!/usr/bin/env python3
"""
Test script for Authentication & User Management APIs
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

# Test results
test_results = []
admin_token = None
business_expert_token = None
support_token = None


def print_test(name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if message:
        print(f"   {message}")
    test_results.append({"name": name, "passed": passed, "message": message})


def test_1_login_invalid_credentials():
    """Test 1: POST /login with invalid credentials"""
    print("\n🧪 Test 1: Login with invalid credentials")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "invalid_user", "password": "wrong_password"},
            headers=HEADERS
        )
        passed = response.status_code == 401
        print_test(
            "Login with invalid credentials should return 401",
            passed,
            f"Status: {response.status_code}, Response: {response.json()}"
        )
    except Exception as e:
        print_test("Login with invalid credentials", False, str(e))


def test_2_login_missing_fields():
    """Test 2: POST /login with missing fields"""
    print("\n🧪 Test 2: Login with missing fields")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "admin"},
            headers=HEADERS
        )
        passed = response.status_code == 400
        print_test(
            "Login with missing password should return 400",
            passed,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_test("Login with missing fields", False, str(e))


def test_3_login_valid_admin():
    """Test 3: POST /login with valid admin credentials"""
    global admin_token
    print("\n🧪 Test 3: Login with valid admin credentials")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "admin", "password": "admin123"},
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                admin_token = data["token"]
                passed = data["user"]["role"] == "admin"
                print_test(
                    "Login with valid admin credentials",
                    passed,
                    f"Token received, User role: {data['user']['role']}"
                )
            else:
                print_test("Login with valid admin credentials", False, "Missing token or user in response")
        else:
            print_test(
                "Login with valid admin credentials",
                False,
                f"Status: {response.status_code}, Response: {response.json()}"
            )
    except Exception as e:
        print_test("Login with valid admin credentials", False, str(e))


def test_4_get_me_without_token():
    """Test 4: GET /me without token"""
    print("\n🧪 Test 4: Get current user without token")
    try:
        response = requests.get(f"{BASE_URL}/me")
        passed = response.status_code == 401
        print_test(
            "Get current user without token should return 401",
            passed,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_test("Get current user without token", False, str(e))


def test_5_get_me_with_token():
    """Test 5: GET /me with valid token"""
    print("\n🧪 Test 5: Get current user with valid token")
    if not admin_token:
        print_test("Get current user with token", False, "No admin token available")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = "username" in data and "role" in data
            print_test(
                "Get current user with valid token",
                passed,
                f"User: {data.get('username')}, Role: {data.get('role')}"
            )
        else:
            print_test(
                "Get current user with valid token",
                False,
                f"Status: {response.status_code}"
            )
    except Exception as e:
        print_test("Get current user with valid token", False, str(e))


def test_6_get_users_without_token():
    """Test 6: GET /users without token"""
    print("\n🧪 Test 6: Get all users without token")
    try:
        response = requests.get(f"{BASE_URL}/users")
        passed = response.status_code == 401
        print_test(
            "Get all users without token should return 401",
            passed,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_test("Get all users without token", False, str(e))


def test_7_get_users_with_admin_token():
    """Test 7: GET /users with admin token"""
    print("\n🧪 Test 7: Get all users with admin token")
    if not admin_token:
        print_test("Get all users with admin token", False, "No admin token available")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = "users" in data and isinstance(data["users"], list)
            print_test(
                "Get all users with admin token",
                passed,
                f"Found {len(data.get('users', []))} users"
            )
        else:
            print_test(
                "Get all users with admin token",
                False,
                f"Status: {response.status_code}, Response: {response.json()}"
            )
    except Exception as e:
        print_test("Get all users with admin token", False, str(e))


def test_8_create_user_without_token():
    """Test 8: POST /users without token"""
    print("\n🧪 Test 8: Create user without token")
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "username": "test_user",
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User",
                "role": "support"
            },
            headers=HEADERS
        )
        passed = response.status_code == 401
        print_test(
            "Create user without token should return 401",
            passed,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_test("Create user without token", False, str(e))


def test_9_create_user_with_admin_token():
    """Test 9: POST /users with admin token"""
    print("\n🧪 Test 9: Create new user with admin token")
    if not admin_token:
        print_test("Create user with admin token", False, "No admin token available")
        return
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "username": f"test_user_{timestamp}",
                "email": f"test_{timestamp}@example.com",
                "password": "password123",
                "full_name": "Test User",
                "role": "support",
                "department": "IT Support"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )
        
        passed = response.status_code == 201
        print_test(
            "Create new user with admin token",
            passed,
            f"Status: {response.status_code}, Response: {response.json()}"
        )
    except Exception as e:
        print_test("Create user with admin token", False, str(e))


def test_10_create_duplicate_user():
    """Test 10: POST /users with duplicate username"""
    print("\n🧪 Test 10: Create user with duplicate username")
    if not admin_token:
        print_test("Create duplicate user", False, "No admin token available")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "username": "admin",  # Duplicate username
                "email": "admin2@example.com",
                "password": "password123",
                "full_name": "Admin 2",
                "role": "admin"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )
        
        passed = response.status_code == 409
        print_test(
            "Create user with duplicate username should return 409",
            passed,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_test("Create duplicate user", False, str(e))


def test_11_logout():
    """Test 11: POST /logout"""
    print("\n🧪 Test 11: Logout")
    try:
        response = requests.post(
            f"{BASE_URL}/logout",
            headers={"Authorization": f"Bearer {admin_token}"} if admin_token else HEADERS
        )
        
        passed = response.status_code == 200
        print_test(
            "Logout should return 200",
            passed,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_test("Logout", False, str(e))


def test_12_rate_limiting():
    """Test 12: Rate limiting on login endpoint"""
    print("\n🧪 Test 12: Rate limiting on login endpoint")
    try:
        # Try to login multiple times rapidly
        responses = []
        for i in range(7):  # Try 7 times (limit is 5)
            response = requests.post(
                f"{BASE_URL}/login",
                json={"username": "invalid", "password": "invalid"},
                headers=HEADERS
            )
            responses.append(response.status_code)
        
        # Check if we got rate limited (429)
        passed = 429 in responses
        print_test(
            "Rate limiting should trigger after multiple failed attempts",
            passed,
            f"Response codes: {responses}"
        )
    except Exception as e:
        print_test("Rate limiting", False, str(e))


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total = len(test_results)
    passed = sum(1 for t in test_results if t["passed"])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for test in test_results:
            if not test["passed"]:
                print(f"  - {test['name']}")
                if test["message"]:
                    print(f"    {test['message']}")
    
    print("\n" + "="*60)
    
    return failed == 0


def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Authentication & User Management API Tests")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_1_login_invalid_credentials()
    test_2_login_missing_fields()
    test_3_login_valid_admin()
    test_4_get_me_without_token()
    test_5_get_me_with_token()
    test_6_get_users_without_token()
    test_7_get_users_with_admin_token()
    test_8_create_user_without_token()
    test_9_create_user_with_admin_token()
    test_10_create_duplicate_user()
    test_11_logout()
    test_12_rate_limiting()
    
    # Print summary
    success = print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

