"""
Comprehensive Test Suite for Admin Panel - Section 4
Testing all Admin Panel routes, features, and security
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name, details=""):
        self.total += 1
        self.passed += 1
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name, details=""):
        self.total += 1
        self.failed += 1
        error_msg = f"❌ FAIL: {test_name}"
        if details:
            error_msg += f"\n   {details}"
        print(error_msg)
        self.errors.append(error_msg)
    
    def print_summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total tests: {self.total}")
        print(f"Passed: {self.passed} ({self.passed/self.total*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/self.total*100:.1f}%)")
        
        if self.errors:
            print("\nFailed Tests:")
            for error in self.errors:
                print(error)


def make_request(method, endpoint, token=None, data=None):
    """Make HTTP request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.request(method, url, headers=headers, json=data, timeout=10)
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"   ⚠️  Connection error: Cannot connect to {url}")
        return None
    except Exception as e:
        print(f"   ⚠️  Error: {type(e).__name__}: {str(e)}")
        return None


def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


# Global variables
admin_token = None
test_category_id = None
test_app_id = None
results = TestResults()


def test_1_authentication():
    """Section 1: Admin Authentication"""
    global admin_token
    
    print_section("SECTION 1: Admin Authentication")
    
    # Test admin login
    response = make_request("POST", "/login", data={
        "username": "admin",
        "password": "admin123"
    })
    
    if response and response.status_code == 200:
        data = response.json()
        admin_token = data.get("token")
        results.add_pass("Admin Login", f"Token: {admin_token[:30]}...")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Admin Login", f"Status: {status}")
        return False
    
    return True


def test_2_dashboard():
    """Section 2: Dashboard Statistics API"""
    print_section("SECTION 2: Dashboard Statistics - GET /dashboard")
    
    # Test: GET /dashboard
    response = make_request("GET", "/dashboard", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        required_fields = ["total_applications", "pending_applications", 
                          "approved_applications", "active_support"]
        
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            results.add_fail("GET /dashboard - Response structure", 
                           f"Missing fields: {missing}")
        else:
            results.add_pass("GET /dashboard - Admin stats", 
                           f"Apps: {data['total_applications']}, "
                           f"Pending: {data['pending_applications']}")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("GET /dashboard", f"Status: {status}")


def test_3_applications():
    """Section 3: Applications Management API"""
    global test_app_id
    
    print_section("SECTION 3: Applications Management")
    
    # Test 1: GET /applications
    response = make_request("GET", "/applications", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        apps = data.get("applications", [])
        results.add_pass("GET /applications - List all", f"Found {len(apps)} applications")
        
        if apps:
            test_app_id = apps[0]["id"]
    else:
        status = response.status_code if response else "No response"
        results.add_fail("GET /applications", f"Status: {status}")
    
    # Test 2: POST /applications/<id>/review - Approve
    if test_app_id:
        response = make_request("POST", f"/applications/{test_app_id}/review",
                              token=admin_token, data={
                                  "is_approved": True,
                                  "review_notes": "Test approval"
                              })
        
        if response and response.status_code == 200:
            results.add_pass("POST /applications/<id>/review - Approve")
        else:
            status = response.status_code if response else "No response"
            results.add_fail("POST /applications/<id>/review - Approve", 
                           f"Status: {status}")
        
        # Test 3: POST /applications/<id>/review - Reject
        response = make_request("POST", f"/applications/{test_app_id}/review",
                              token=admin_token, data={
                                  "is_approved": False,
                                  "review_notes": "Test rejection"
                              })
        
        if response and response.status_code == 200:
            results.add_pass("POST /applications/<id>/review - Reject")
        else:
            status = response.status_code if response else "No response"
            results.add_fail("POST /applications/<id>/review - Reject", 
                           f"Status: {status}")
    
    # Test 4: DELETE /applications/<id>
    # Note: Skipping deletion to preserve test data
    # if test_app_id:
    #     response = make_request("DELETE", f"/applications/{test_app_id}", token=admin_token)
    #     ...


def test_4_categories():
    """Section 4: Categories Management API"""
    global test_category_id
    
    print_section("SECTION 4: Categories Management")
    
    # Test 1: GET /admin/categories
    response = make_request("GET", "/admin/categories", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        cats = data.get("categories", [])
        results.add_pass("GET /admin/categories - List", f"Found {len(cats)} categories")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("GET /admin/categories", f"Status: {status}")
    
    # Test 2: POST /admin/categories - Create
    unique_name = f"Test Category {datetime.now().strftime('%Y%m%d%H%M%S')}"
    response = make_request("POST", "/admin/categories", token=admin_token,
                          data={"name": unique_name})
    
    if response and response.status_code == 201:
        data = response.json()
        test_category_id = data.get("category", {}).get("id")
        results.add_pass("POST /admin/categories - Create", 
                       f"Created category ID: {test_category_id}")
    else:
        status = response.status_code if response else "No response"
        body = response.json() if response else {}
        results.add_fail("POST /admin/categories - Create", 
                       f"Status: {status}, Body: {body}")
    
    # Test 3: POST /admin/categories - Duplicate (should fail)
    if test_category_id:
        response = make_request("POST", "/admin/categories", token=admin_token,
                              data={"name": unique_name})
        
        if response and response.status_code == 400:
            results.add_pass("POST /admin/categories - Duplicate prevention")
        else:
            status = response.status_code if response else "No response"
            results.add_fail("POST /admin/categories - Duplicate prevention", 
                           f"Status: {status}, should be 400")
    
    # Test 4: PUT /admin/categories/<id> - Update
    if test_category_id:
        new_name = f"Updated Category {datetime.now().strftime('%H%M%S')}"
        response = make_request("PUT", f"/admin/categories/{test_category_id}",
                              token=admin_token, data={"name": new_name})
        
        if response and response.status_code == 200:
            results.add_pass("PUT /admin/categories/<id> - Update")
        else:
            status = response.status_code if response else "No response"
            body = response.json() if response else {}
            results.add_fail("PUT /admin/categories/<id> - Update", 
                           f"Status: {status}, Body: {body}")
    
    # Test 5: GET /admin/categories/<id>/companies
    if test_category_id:
        response = make_request("GET", f"/admin/categories/{test_category_id}/companies",
                              token=admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            companies = data.get("companies", [])
            results.add_pass("GET /admin/categories/<id>/companies", 
                           f"Found {len(companies)} companies")
        else:
            status = response.status_code if response else "No response"
            results.add_fail("GET /admin/categories/<id>/companies", 
                           f"Status: {status}")
    
    # Test 6: GET /admin/categories/statistics
    response = make_request("GET", "/admin/categories/statistics", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        results.add_pass("GET /admin/categories/statistics", 
                       f"Total categories: {data.get('total_categories', 0)}")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("GET /admin/categories/statistics", f"Status: {status}")
    
    # Test 7: DELETE /admin/categories/<id>
    if test_category_id:
        response = make_request("DELETE", f"/admin/categories/{test_category_id}",
                              token=admin_token)
        
        if response and response.status_code == 200:
            results.add_pass("DELETE /admin/categories/<id>")
        else:
            status = response.status_code if response else "No response"
            body = response.json() if response else {}
            results.add_fail("DELETE /admin/categories/<id>", 
                           f"Status: {status}, Body: {body}")


def test_5_authorization():
    """Section 5: Authorization and Security"""
    print_section("SECTION 5: Authorization and Security")
    
    # Test 1: Access dashboard without token
    response = make_request("GET", "/dashboard")
    
    if response and response.status_code == 401:
        results.add_pass("Dashboard - Unauthorized access blocked")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Dashboard - Unauthorized access", 
                       f"Status: {status}, should be 401")
    
    # Test 2: Access categories without token
    response = make_request("GET", "/admin/categories")
    
    if response and response.status_code == 401:
        results.add_pass("Categories - Unauthorized access blocked")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Categories - Unauthorized access", 
                       f"Status: {status}, should be 401")
    
    # Test 3: Create category without token
    response = make_request("POST", "/admin/categories", 
                          data={"name": "Unauthorized Test"})
    
    if response and response.status_code == 401:
        results.add_pass("Create category - Unauthorized access blocked")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Create category - Unauthorized access", 
                       f"Status: {status}, should be 401")
    
    # Test 4: Update category without token
    response = make_request("PUT", "/admin/categories/1", 
                          data={"name": "Unauthorized Update"})
    
    if response and response.status_code == 401:
        results.add_pass("Update category - Unauthorized access blocked")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Update category - Unauthorized access", 
                       f"Status: {status}, should be 401")
    
    # Test 5: Delete category without token
    response = make_request("DELETE", "/admin/categories/999")
    
    if response and response.status_code == 401:
        results.add_pass("Delete category - Unauthorized access blocked")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Delete category - Unauthorized access", 
                       f"Status: {status}, should be 401")


def test_6_validation():
    """Section 6: Input Validation"""
    print_section("SECTION 6: Input Validation")
    
    # Test 1: Create category without name
    response = make_request("POST", "/admin/categories", token=admin_token,
                          data={})
    
    if response and response.status_code == 400:
        results.add_pass("Create category - Empty name rejected")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Create category - Empty name validation", 
                       f"Status: {status}, should be 400")
    
    # Test 2: Create category with only spaces
    response = make_request("POST", "/admin/categories", token=admin_token,
                          data={"name": "   "})
    
    if response and response.status_code == 400:
        results.add_pass("Create category - Whitespace name rejected")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Create category - Whitespace validation", 
                       f"Status: {status}, should be 400")
    
    # Test 3: Update category with empty name
    response = make_request("PUT", "/admin/categories/1", token=admin_token,
                          data={"name": ""})
    
    if response and response.status_code == 400:
        results.add_pass("Update category - Empty name rejected")
    else:
        status = response.status_code if response else "No response"
        results.add_fail("Update category - Empty name validation", 
                       f"Status: {status}, should be 400")


def test_7_frontend():
    """Section 7: Frontend Routes"""
    print_section("SECTION 7: Frontend Routes (Manual Check Required)")
    
    print("✓ Please manually verify the following frontend routes:")
    print("  • /admin/dashboard - Admin dashboard page")
    print("  • /admin/categories - Category management page")
    print("\nThese routes should be accessible only when logged in as admin.")


def run_all_tests():
    """Main test runner"""
    print("\n" + "="*80)
    print("  ADMIN PANEL COMPREHENSIVE TEST SUITE")
    print("  Section 4: Admin Panel - Complete Testing")
    print("="*80)
    print(f"\nStarting tests at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run all test sections
    if not test_1_authentication():
        print("\n❌ Authentication failed. Cannot proceed with other tests.")
        results.print_summary()
        return
    
    test_2_dashboard()
    test_3_applications()
    test_4_categories()
    test_5_authorization()
    test_6_validation()
    test_7_frontend()
    
    # Print summary
    results.print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()

