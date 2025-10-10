"""
Test suite for Admin Panel functionality
Testing all Admin Panel routes and features
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

# Global variables for storing tokens and IDs
admin_token = None
test_category_id = None
test_application_id = None


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_test(test_name: str, result: str, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if result == "PASS" else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    Details: {details}")


def make_request(method: str, endpoint: str, token: Optional[str] = None, 
                 data: Optional[Dict[str, Any]] = None) -> requests.Response:
    """Make HTTP request with optional token"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if data:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"    Request error: {type(e).__name__}: {str(e)}")
        return None
    except Exception as e:
        print(f"    Unexpected error: {type(e).__name__}: {str(e)}")
        return None


# ============================================================================
# SECTION 1: Admin Authentication
# ============================================================================

def test_admin_authentication():
    """Test admin login"""
    global admin_token
    
    print_section("SECTION 1: Admin Authentication")
    
    # Test 1: Admin login
    response = make_request("POST", "/login", data=ADMIN_CREDENTIALS)
    
    if response and response.status_code == 200:
        data = response.json()
        admin_token = data.get("token")
        print_test("Admin login", "PASS", f"Token received: {admin_token[:20]}...")
    else:
        print_test("Admin login", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}")
        return False
    
    return True


# ============================================================================
# SECTION 2: Dashboard Statistics API
# ============================================================================

def test_dashboard_api():
    """Test admin dashboard API"""
    print_section("SECTION 2: Dashboard Statistics API")
    
    # Test 1: GET /dashboard - Get dashboard stats
    response = make_request("GET", "/dashboard", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        required_fields = ["total_applications", "pending_applications", 
                          "approved_applications", "active_support"]
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_test("GET /dashboard - Response structure", "FAIL", 
                      f"Missing fields: {missing_fields}")
        else:
            print_test("GET /dashboard - Get stats", "PASS", 
                      f"Total apps: {data['total_applications']}, "
                      f"Pending: {data['pending_applications']}")
    else:
        print_test("GET /dashboard", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}")


# ============================================================================
# SECTION 3: Applications Management API
# ============================================================================

def test_applications_api():
    """Test applications management endpoints"""
    global test_application_id
    
    print_section("SECTION 3: Applications Management API")
    
    # Test 1: GET /applications - Get all applications
    response = make_request("GET", "/applications", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        applications = data.get("applications", [])
        print_test("GET /applications - List all", "PASS", 
                  f"Found {len(applications)} applications")
        
        # Store first application ID for further tests
        if applications:
            test_application_id = applications[0]["id"]
    else:
        print_test("GET /applications", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}")
    
    # Test 2: POST /applications/<id>/review - Review application (approve)
    if test_application_id:
        review_data = {
            "is_approved": True,
            "review_notes": "Test approval - good application"
        }
        response = make_request("POST", f"/applications/{test_application_id}/review", 
                              token=admin_token, data=review_data)
        
        if response and response.status_code == 200:
            print_test("POST /applications/<id>/review - Approve", "PASS", 
                      "Application approved successfully")
        else:
            print_test("POST /applications/<id>/review", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")
        
        # Test 3: POST /applications/<id>/review - Review application (reject)
        review_data = {
            "is_approved": False,
            "review_notes": "Test rejection - incomplete information"
        }
        response = make_request("POST", f"/applications/{test_application_id}/review", 
                              token=admin_token, data=review_data)
        
        if response and response.status_code == 200:
            print_test("POST /applications/<id>/review - Reject", "PASS", 
                      "Application rejected successfully")
        else:
            print_test("POST /applications/<id>/review", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")
    
    # Test 4: DELETE /applications/<id> - Delete application
    if test_application_id:
        response = make_request("DELETE", f"/applications/{test_application_id}", 
                              token=admin_token)
        
        if response and response.status_code == 200:
            print_test("DELETE /applications/<id>", "PASS", 
                      "Application deleted successfully")
        else:
            print_test("DELETE /applications/<id>", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")


# ============================================================================
# SECTION 4: Categories Management API
# ============================================================================

def test_categories_api():
    """Test categories management endpoints"""
    global test_category_id
    
    print_section("SECTION 4: Categories Management API")
    
    # Test 1: GET /admin/categories - Get all categories
    response = make_request("GET", "/admin/categories", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        categories = data.get("categories", [])
        print_test("GET /admin/categories - List all", "PASS", 
                  f"Found {len(categories)} categories")
    else:
        print_test("GET /admin/categories", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}")
    
    # Test 2: POST /admin/categories - Create new category
    new_category = {
        "name": "Test Category - تست دسته‌بندی"
    }
    response = make_request("POST", "/admin/categories", token=admin_token, 
                          data=new_category)
    
    if response and response.status_code == 201:
        data = response.json()
        test_category_id = data.get("category", {}).get("id")
        print_test("POST /admin/categories - Create", "PASS", 
                  f"Category created with ID: {test_category_id}")
    else:
        print_test("POST /admin/categories", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}")
    
    # Test 3: POST /admin/categories - Create duplicate (should fail)
    response = make_request("POST", "/admin/categories", token=admin_token, 
                          data=new_category)
    
    if response and response.status_code == 400:
        print_test("POST /admin/categories - Duplicate check", "PASS", 
                  "Correctly rejected duplicate category")
    else:
        print_test("POST /admin/categories - Duplicate check", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}, "
                  "Should reject duplicate")
    
    # Test 4: PUT /admin/categories/<id> - Update category
    if test_category_id:
        updated_data = {
            "name": "Updated Test Category"
        }
        response = make_request("PUT", f"/admin/categories/{test_category_id}", 
                              token=admin_token, data=updated_data)
        
        if response and response.status_code == 200:
            print_test("PUT /admin/categories/<id> - Update", "PASS", 
                      "Category updated successfully")
        else:
            print_test("PUT /admin/categories/<id>", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")
    
    # Test 5: GET /admin/categories/<id>/companies - Get companies in category
    if test_category_id:
        response = make_request("GET", f"/admin/categories/{test_category_id}/companies", 
                              token=admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            companies = data.get("companies", [])
            print_test("GET /admin/categories/<id>/companies", "PASS", 
                      f"Found {len(companies)} companies")
        else:
            print_test("GET /admin/categories/<id>/companies", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")
    
    # Test 6: GET /admin/categories/statistics - Get statistics
    response = make_request("GET", "/admin/categories/statistics", token=admin_token)
    
    if response and response.status_code == 200:
        data = response.json()
        print_test("GET /admin/categories/statistics", "PASS", 
                  f"Total categories: {data.get('total_categories', 0)}, "
                  f"Total companies: {data.get('total_companies', 0)}")
    else:
        print_test("GET /admin/categories/statistics", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}")
    
    # Test 7: DELETE /admin/categories/<id> - Delete category
    if test_category_id:
        response = make_request("DELETE", f"/admin/categories/{test_category_id}", 
                              token=admin_token)
        
        if response and response.status_code == 200:
            print_test("DELETE /admin/categories/<id>", "PASS", 
                      "Category deleted successfully")
        else:
            print_test("DELETE /admin/categories/<id>", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")


# ============================================================================
# SECTION 5: Authorization Tests
# ============================================================================

def test_authorization():
    """Test authorization and access control"""
    print_section("SECTION 5: Authorization Tests")
    
    # Test 1: Access without token
    response = make_request("GET", "/dashboard")
    
    if response and response.status_code == 401:
        print_test("Access without token", "PASS", 
                  "Correctly rejected unauthorized request")
    else:
        print_test("Access without token", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}, "
                  "Should reject unauthorized")
    
    # Test 2: Access categories management without token
    response = make_request("GET", "/admin/categories")
    
    if response and response.status_code == 401:
        print_test("Categories access without token", "PASS", 
                  "Correctly rejected unauthorized request")
    else:
        print_test("Categories access without token", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}, "
                  "Should reject unauthorized")
    
    # Test 3: Create category without token
    response = make_request("POST", "/admin/categories", 
                          data={"name": "Unauthorized Test"})
    
    if response and response.status_code == 401:
        print_test("Create category without token", "PASS", 
                  "Correctly rejected unauthorized request")
    else:
        print_test("Create category without token", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}, "
                  "Should reject unauthorized")


# ============================================================================
# SECTION 6: Input Validation Tests
# ============================================================================

def test_input_validation():
    """Test input validation"""
    print_section("SECTION 6: Input Validation Tests")
    
    # Test 1: Create category without name
    response = make_request("POST", "/admin/categories", token=admin_token, 
                          data={})
    
    if response and response.status_code == 400:
        print_test("Create category without name", "PASS", 
                  "Correctly rejected empty name")
    else:
        print_test("Create category without name", "FAIL", 
                  f"Status: {response.status_code if response else 'No response'}, "
                  "Should reject empty name")
    
    # Test 2: Update category with empty name
    if test_category_id:
        response = make_request("PUT", f"/admin/categories/{test_category_id}", 
                              token=admin_token, data={"name": ""})
        
        if response and response.status_code == 400:
            print_test("Update category with empty name", "PASS", 
                      "Correctly rejected empty name")
        else:
            print_test("Update category with empty name", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}, "
                      "Should reject empty name")
    
    # Test 3: Review application without required fields
    if test_application_id:
        response = make_request("POST", f"/applications/{test_application_id}/review", 
                              token=admin_token, data={})
        
        # This should still work as is_approved defaults to False
        if response and response.status_code in [200, 400]:
            print_test("Review application without fields", "PASS", 
                      "Handled missing fields correctly")
        else:
            print_test("Review application without fields", "FAIL", 
                      f"Status: {response.status_code if response else 'No response'}")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all admin panel tests"""
    print("\n" + "="*80)
    print("  ADMIN PANEL TEST SUITE")
    print("  Testing all Admin Panel routes and features")
    print("="*80)
    
    # Run tests
    if not test_admin_authentication():
        print("\n❌ Admin authentication failed. Cannot proceed with other tests.")
        return
    
    test_dashboard_api()
    test_applications_api()
    test_categories_api()
    test_authorization()
    test_input_validation()
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUITE COMPLETED")
    print("="*80)
    print("\nPlease review the results above for any failed tests.")
    print("Failed tests indicate issues that need to be fixed.\n")


if __name__ == "__main__":
    run_all_tests()

