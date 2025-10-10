"""
Comprehensive Test Suite for Business Expert Panel APIs
Tests all Business Expert functionalities including:
- Dashboard statistics
- Application management (list, view, approve, reject)
- Provider management (CRUD operations)
- Bulk upload operations
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
BUSINESS_EXPERT_USERNAME = "business_expert"
BUSINESS_EXPERT_PASSWORD = "expert123"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.details = []

    def add_result(self, test_name, passed, message=""):
        self.total += 1
        if passed:
            self.passed += 1
            status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}"
        else:
            self.failed += 1
            status = f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        
        self.details.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status} - {test_name}")
        if message:
            print(f"  Message: {message}")

    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"Total Tests: {self.total}")
        print(f"{Colors.OKGREEN}Passed: {self.passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {self.failed}{Colors.ENDC}")
        
        if self.failed > 0:
            print(f"\n{Colors.FAIL}Failed Tests:{Colors.ENDC}")
            for detail in self.details:
                if not detail['passed']:
                    print(f"  - {detail['test']}: {detail['message']}")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

# Global test results
results = TestResults()

def print_section(title):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def login_as_business_expert():
    """Login as business expert and return token"""
    print_section("AUTHENTICATION")
    
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": BUSINESS_EXPERT_USERNAME,
            "password": BUSINESS_EXPERT_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        results.add_result("Login as Business Expert", True, f"Token received")
        return token
    else:
        results.add_result("Login as Business Expert", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_dashboard(token):
    """Test dashboard statistics endpoint"""
    print_section("DASHBOARD STATISTICS")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/business-expert/dashboard", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        required_fields = ["pending_reviews", "approved_today", "total_companies"]
        
        missing_fields = [field for field in required_fields if field not in data]
        if not missing_fields:
            results.add_result("Get Dashboard Statistics", True, 
                             f"Pending: {data.get('pending_reviews')}, "
                             f"Approved Today: {data.get('approved_today')}, "
                             f"Total Companies: {data.get('total_companies')}")
        else:
            results.add_result("Get Dashboard Statistics", False, 
                             f"Missing fields: {missing_fields}")
    else:
        results.add_result("Get Dashboard Statistics", False, 
                         f"Status: {response.status_code}, Response: {response.text}")

def create_test_application():
    """Create a test provider application"""
    response = requests.post(
        f"{BASE_URL}/provider-applications",
        json={
            "companyName": "Test Provider Company",
            "representativeFirstName": "احمد",
            "representativeLastName": "محمدی",
            "address": "تهران، خیابان ولیعصر، پلاک 123",
            "phoneMobile": "09123456789",
            "phoneLandline": "02112345678",
            "serviceDomain": "تعمیرات موتور",
            "latitude": 35.6892,
            "longitude": 51.3890
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        results.add_result("Create Test Application", True, f"Application ID: {data.get('id')}")
        return data.get('id')
    else:
        results.add_result("Create Test Application", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_get_applications(token):
    """Test getting pending applications"""
    print_section("APPLICATION MANAGEMENT - List Applications")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/business-expert/applications", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        applications = data.get('applications', [])
        results.add_result("Get Pending Applications", True, 
                         f"Found {len(applications)} pending applications")
        return applications
    else:
        results.add_result("Get Pending Applications", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return []

def test_get_application_details(token, app_id):
    """Test getting application details"""
    print_section(f"APPLICATION MANAGEMENT - Get Details (ID: {app_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/business-expert/applications/{app_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        results.add_result(f"Get Application Details (ID: {app_id})", True, 
                         f"Company: {data.get('company_name')}, Status: {data.get('status')}")
        return data
    else:
        results.add_result(f"Get Application Details (ID: {app_id})", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_approve_application(token, app_id):
    """Test approving an application"""
    print_section(f"APPLICATION MANAGEMENT - Approve Application (ID: {app_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/business-expert/applications/{app_id}/approve",
        headers=headers,
        json={"notes": "تایید شد - تست خودکار"}
    )
    
    if response.status_code == 200:
        data = response.json()
        results.add_result(f"Approve Application (ID: {app_id})", True, 
                         f"Message: {data.get('message')}")
        return True
    else:
        results.add_result(f"Approve Application (ID: {app_id})", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return False

def test_reject_application(token, app_id):
    """Test rejecting an application"""
    print_section(f"APPLICATION MANAGEMENT - Reject Application (ID: {app_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/business-expert/applications/{app_id}/reject",
        headers=headers,
        json={"notes": "رد شد - تست خودکار"}
    )
    
    if response.status_code == 200:
        data = response.json()
        results.add_result(f"Reject Application (ID: {app_id})", True, 
                         f"Message: {data.get('message')}")
        return True
    else:
        results.add_result(f"Reject Application (ID: {app_id})", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return False

def test_get_providers(token):
    """Test getting list of providers"""
    print_section("PROVIDER MANAGEMENT - List Providers")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/business-expert/providers", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        providers = data.get('providers', [])
        results.add_result("Get Providers List", True, 
                         f"Found {len(providers)} providers")
        return providers
    else:
        results.add_result("Get Providers List", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return []

def test_create_provider(token):
    """Test creating a new provider directly"""
    print_section("PROVIDER MANAGEMENT - Create Provider")
    
    headers = {"Authorization": f"Bearer {token}"}
    timestamp = int(time.time())
    
    response = requests.post(
        f"{BASE_URL}/business-expert/providers",
        headers=headers,
        json={
            "companyName": f"Direct Provider {timestamp}",
            "representativeFirstName": "رضا",
            "representativeLastName": "احمدی",
            "address": "اصفهان، خیابان چهارباغ",
            "phoneMobile": f"0912{timestamp % 10000000:07d}",
            "phoneLandline": "03112345678",
            "serviceDomain": "تعمیرات برق",
            "latitude": 32.6546,
            "longitude": 51.6680,
            "isActive": True
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        provider_id = data.get('provider_id')
        results.add_result("Create Provider Directly", True, 
                         f"Provider ID: {provider_id}")
        return provider_id
    else:
        results.add_result("Create Provider Directly", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_toggle_provider_status(token, provider_id):
    """Test toggling provider active status"""
    print_section(f"PROVIDER MANAGEMENT - Toggle Status (ID: {provider_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First deactivate
    response = requests.patch(
        f"{BASE_URL}/business-expert/providers/{provider_id}/toggle-status",
        headers=headers,
        json={"is_active": False}
    )
    
    if response.status_code == 200:
        results.add_result(f"Deactivate Provider (ID: {provider_id})", True, 
                         response.json().get('message'))
    else:
        results.add_result(f"Deactivate Provider (ID: {provider_id})", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
    
    # Then reactivate
    response = requests.patch(
        f"{BASE_URL}/business-expert/providers/{provider_id}/toggle-status",
        headers=headers,
        json={"is_active": True}
    )
    
    if response.status_code == 200:
        results.add_result(f"Reactivate Provider (ID: {provider_id})", True, 
                         response.json().get('message'))
    else:
        results.add_result(f"Reactivate Provider (ID: {provider_id})", False, 
                         f"Status: {response.status_code}, Response: {response.text}")

def test_delete_provider(token, provider_id):
    """Test deleting a provider"""
    print_section(f"PROVIDER MANAGEMENT - Delete Provider (ID: {provider_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/business-expert/providers/{provider_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        results.add_result(f"Delete Provider (ID: {provider_id})", True, 
                         response.json().get('message'))
        return True
    else:
        results.add_result(f"Delete Provider (ID: {provider_id})", False, 
                         f"Status: {response.status_code}, Response: {response.text}")
        return False

def test_download_template(token):
    """Test downloading Excel template"""
    print_section("BULK UPLOAD - Download Template")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/business-expert/providers/template", headers=headers)
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'excel' in content_type or 'spreadsheet' in content_type:
            results.add_result("Download Excel Template", True, 
                             f"File size: {len(response.content)} bytes")
            
            # Save template for testing
            with open('template_providers_test.xlsx', 'wb') as f:
                f.write(response.content)
            return True
        else:
            results.add_result("Download Excel Template", False, 
                             f"Wrong content type: {content_type}")
            return False
    else:
        results.add_result("Download Excel Template", False, 
                         f"Status: {response.status_code}")
        return False

def test_bulk_upload(token):
    """Test bulk upload functionality"""
    print_section("BULK UPLOAD - Upload Excel File")
    
    # First download template
    if not test_download_template(token):
        results.add_result("Bulk Upload", False, "Could not download template")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to upload the template file
    try:
        with open('template_providers_test.xlsx', 'rb') as f:
            files = {'file': ('providers.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(
                f"{BASE_URL}/business-expert/providers/bulk-upload",
                headers=headers,
                files=files
            )
        
        # Accept both 200 (sync) and 202 (async) as success
        if response.status_code in [200, 202]:
            data = response.json()
            processing_mode = data.get('processing_mode', 'unknown')
            
            if processing_mode == 'async':
                task_id = data.get('task_id')
                results.add_result("Bulk Upload - Submit File", True, 
                                 f"Task ID: {task_id} (async mode)")
                
                # Test status endpoint
                if task_id:
                    test_bulk_upload_status(token, task_id)
            elif processing_mode == 'sync':
                upload_results = data.get('results', {})
                results.add_result("Bulk Upload - Submit File", True, 
                                 f"Processed: {upload_results.get('total')}, "
                                 f"Success: {upload_results.get('success')}, "
                                 f"Failed: {upload_results.get('failed')} (sync mode - Redis not available)")
            else:
                results.add_result("Bulk Upload - Submit File", True, 
                                 f"Upload successful (mode: {processing_mode})")
        else:
            results.add_result("Bulk Upload - Submit File", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
    
    except Exception as e:
        results.add_result("Bulk Upload - Submit File", False, str(e))
    
    # Cleanup
    if os.path.exists('template_providers_test.xlsx'):
        os.remove('template_providers_test.xlsx')

def test_bulk_upload_status(token, task_id):
    """Test checking bulk upload status"""
    print_section(f"BULK UPLOAD - Check Status (Task: {task_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Poll status a few times
    for i in range(3):
        response = requests.get(
            f"{BASE_URL}/business-expert/providers/bulk-upload/status/{task_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('state')
            status = data.get('status')
            
            results.add_result(f"Check Upload Status (Attempt {i+1})", True, 
                             f"State: {state}, Status: {status}")
            
            if state in ['SUCCESS', 'FAILURE']:
                break
            
            time.sleep(2)
        else:
            results.add_result(f"Check Upload Status (Attempt {i+1})", False, 
                             f"Status: {response.status_code}")
            break

def test_unauthorized_access():
    """Test that endpoints require authentication"""
    print_section("SECURITY - Unauthorized Access Tests")
    
    endpoints = [
        ("GET", "/business-expert/dashboard"),
        ("GET", "/business-expert/applications"),
        ("GET", "/business-expert/providers"),
    ]
    
    for method, endpoint in endpoints:
        response = requests.request(method, f"{BASE_URL}{endpoint}")
        
        if response.status_code == 401:
            results.add_result(f"Unauthorized Access Blocked - {method} {endpoint}", True, 
                             "Correctly returned 401")
        else:
            results.add_result(f"Unauthorized Access Blocked - {method} {endpoint}", False, 
                             f"Expected 401, got {response.status_code}")

def test_invalid_inputs(token):
    """Test validation of invalid inputs"""
    print_section("VALIDATION - Invalid Input Tests")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test creating provider with missing fields
    response = requests.post(
        f"{BASE_URL}/business-expert/providers",
        headers=headers,
        json={
            "companyName": "Test"
            # Missing required fields
        }
    )
    
    if response.status_code >= 400:
        results.add_result("Reject Incomplete Provider Data", True, 
                         f"Correctly rejected with status {response.status_code}")
    else:
        results.add_result("Reject Incomplete Provider Data", False, 
                         f"Should reject incomplete data, got {response.status_code}")
    
    # Test invalid phone number
    response = requests.post(
        f"{BASE_URL}/business-expert/providers",
        headers=headers,
        json={
            "companyName": "Test Provider",
            "representativeFirstName": "Test",
            "representativeLastName": "User",
            "address": "Test Address",
            "phoneMobile": "invalid_phone",
            "serviceDomain": "Test",
            "latitude": 35.0,
            "longitude": 51.0
        }
    )
    
    if response.status_code >= 400:
        results.add_result("Reject Invalid Phone Number", True, 
                         f"Correctly rejected with status {response.status_code}")
    else:
        results.add_result("Reject Invalid Phone Number", False, 
                         "Should reject invalid phone number")

def run_all_tests():
    """Run all test suites"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}BUSINESS EXPERT PANEL - COMPREHENSIVE TEST SUITE{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Test unauthorized access first
    test_unauthorized_access()
    
    # Login
    token = login_as_business_expert()
    if not token:
        print(f"\n{Colors.FAIL}Cannot proceed without authentication{Colors.ENDC}")
        results.print_summary()
        return
    
    # Test Dashboard
    test_dashboard(token)
    
    # Test Application Management
    # Create test applications
    app_id_to_approve = create_test_application()
    app_id_to_reject = create_test_application()
    
    # Get applications list
    applications = test_get_applications(token)
    
    # Test application details
    if applications and len(applications) > 0:
        test_get_application_details(token, applications[0]['id'])
    
    # Test approve
    if app_id_to_approve:
        test_approve_application(token, app_id_to_approve)
    
    # Test reject
    if app_id_to_reject:
        test_reject_application(token, app_id_to_reject)
    
    # Test Provider Management
    providers = test_get_providers(token)
    
    # Create new provider
    new_provider_id = test_create_provider(token)
    
    # Test toggle status
    if new_provider_id:
        test_toggle_provider_status(token, new_provider_id)
    
    # Test delete (use the newly created provider)
    if new_provider_id:
        test_delete_provider(token, new_provider_id)
    
    # Test Bulk Upload
    test_bulk_upload(token)
    
    # Test Invalid Inputs
    test_invalid_inputs(token)
    
    # Print summary
    results.print_summary()
    
    # Save results to file
    save_test_report()

def save_test_report():
    """Save test results to a markdown file"""
    with open('BUSINESS_EXPERT_TEST_REPORT.md', 'w', encoding='utf-8') as f:
        f.write("# Business Expert Panel - Test Report\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Base URL:** {BASE_URL}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Tests:** {results.total}\n")
        f.write(f"- **Passed:** {results.passed} ✓\n")
        f.write(f"- **Failed:** {results.failed} ✗\n")
        success_rate = (results.passed / results.total * 100) if results.total > 0 else 0
        f.write(f"- **Success Rate:** {success_rate:.1f}%\n\n")
        
        f.write("## Test Details\n\n")
        
        current_section = None
        for detail in results.details:
            test_name = detail['test']
            # Extract section from test name
            section = test_name.split(' - ')[0] if ' - ' in test_name else test_name.split('(')[0].strip()
            
            if section != current_section:
                current_section = section
                f.write(f"\n### {current_section}\n\n")
            
            status = "✓ PASS" if detail['passed'] else "✗ FAIL"
            f.write(f"- **{status}** - {test_name}\n")
            if detail['message']:
                f.write(f"  - {detail['message']}\n")
        
        f.write("\n## API Endpoints Tested\n\n")
        f.write("### Dashboard\n")
        f.write("- `GET /business-expert/dashboard` - Dashboard statistics\n\n")
        
        f.write("### Application Management\n")
        f.write("- `GET /business-expert/applications` - List pending applications\n")
        f.write("- `GET /business-expert/applications/<app_id>` - Get application details\n")
        f.write("- `POST /business-expert/applications/<app_id>/approve` - Approve application\n")
        f.write("- `POST /business-expert/applications/<app_id>/reject` - Reject application\n\n")
        
        f.write("### Provider Management\n")
        f.write("- `GET /business-expert/providers` - List providers\n")
        f.write("- `POST /business-expert/providers` - Create provider\n")
        f.write("- `PATCH /business-expert/providers/<id>/toggle-status` - Toggle provider status\n")
        f.write("- `DELETE /business-expert/providers/<id>` - Delete provider\n\n")
        
        f.write("### Bulk Upload\n")
        f.write("- `GET /business-expert/providers/template` - Download template\n")
        f.write("- `POST /business-expert/providers/bulk-upload` - Upload file\n")
        f.write("- `GET /business-expert/providers/bulk-upload/status/<task_id>` - Check status\n\n")
    
    print(f"\n{Colors.OKGREEN}Test report saved to: BUSINESS_EXPERT_TEST_REPORT.md{Colors.ENDC}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
        results.print_summary()
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}")
        results.print_summary()

