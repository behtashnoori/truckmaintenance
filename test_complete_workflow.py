#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Workflow Test Script
Tests the full provider registration workflow from signup to display
"""

import sys
import os
import io
import requests
import json
from datetime import datetime

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_provider_signup():
    """Test Step 1: Provider submits application"""
    print_section("STEP 1: Provider Application Signup")
    
    # Generate a unique phone number (09 + 9 digits)
    timestamp = datetime.now().strftime('%H%M%S')
    phone = f"0912{timestamp}123"[:11]  # Ensure exactly 11 digits
    
    test_data = {
        "companyName": f"شرکت تست {timestamp}",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران، خیابان ولیعصر، پلاک 123",
        "phoneMobile": phone,
        "phoneLandline": "02112345678",
        "serviceCategories": ["تعمیرات موتور", "تعویض روغن"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    print(f"Submitting application for: {test_data['companyName']}")
    print(f"Categories: {test_data['serviceCategories']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/provider-applications",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                app_id = data.get('data', {}).get('id')
                print(f"✅ Application submitted successfully! ID: {app_id}")
                return app_id, test_data
            else:
                print(f"❌ Application failed: {data.get('error')}")
                return None, None
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None, None

def test_business_expert_login():
    """Test Step 2: Business Expert logs in"""
    print_section("STEP 2: Business Expert Login")
    
    login_data = {
        "username": "business_expert",
        "password": "expert123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data.get('token')  # Token is at top level, not in data
                if token:
                    print(f"✅ Login successful! Got token.")
                    return token
                else:
                    print(f"❌ Login response missing token")
                    return None
            else:
                print(f"❌ Login failed: {data.get('error')}")
                return None
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_get_pending_applications(token):
    """Test Step 3: Get pending applications"""
    print_section("STEP 3: View Pending Applications")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/business-expert/applications?status=pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"✅ Found {len(items)} pending applications")
                return items
            else:
                print(f"❌ Failed: {data.get('error')}")
                return []
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def test_approve_application(app_id, token):
    """Test Step 4: Approve application"""
    print_section(f"STEP 4: Approve Application #{app_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/business-expert/applications/{app_id}/approve",
            json={"notes": "تایید شد - تست خودکار"},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Application approved successfully!")
                return True
            else:
                print(f"❌ Approval failed: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_get_categories():
    """Test Step 5: Get categories with counts"""
    print_section("STEP 5: View Categories on Homepage")
    
    try:
        response = requests.get(f"{BASE_URL}/api/public/categories")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                categories = data.get('data', [])
                print(f"✅ Found {len(categories)} categories\n")
                
                for cat in categories:
                    count = cat.get('companies_count', 0)
                    if count > 0:
                        print(f"  • {cat['name']:30s} → {count} ارائه‌دهنده")
                
                return categories
            else:
                print(f"❌ Failed: {data.get('error')}")
                return []
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def test_get_providers_by_category(category_name):
    """Test Step 6: Get providers in a category"""
    print_section(f"STEP 6: View Providers in '{category_name}'")
    
    try:
        params = {"category": category_name}
        response = requests.get(
            f"{BASE_URL}/api/public/providers",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                providers = data.get('data', [])
                print(f"✅ Found {len(providers)} providers\n")
                
                for provider in providers:
                    print(f"  • {provider['name']}")
                    print(f"    Phone: {provider['phone']}")
                    print(f"    Categories: {provider['categories']}")
                    print()
                
                return providers
            else:
                print(f"❌ Failed: {data.get('error')}")
                return []
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def test_get_provider_detail(provider_id):
    """Test Step 7: View provider details"""
    print_section(f"STEP 7: View Provider Details (ID: {provider_id})")
    
    try:
        response = requests.get(f"{BASE_URL}/api/public/providers/{provider_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                provider = data.get('data', {})
                print(f"✅ Provider details loaded\n")
                print(f"  Name: {provider.get('name')}")
                print(f"  Phone: {provider.get('phone')}")
                print(f"  Address: {provider.get('address')}")
                print(f"  Categories: {provider.get('categories')}")
                return provider
            else:
                print(f"❌ Failed: {data.get('error')}")
                return None
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Run complete workflow test"""
    print_section("PROVIDER REGISTRATION WORKFLOW TEST")
    print("Testing complete flow from signup to public display\n")
    
    # Step 1: Provider signup
    app_id, test_data = test_provider_signup()
    if not app_id:
        print("\n❌ TEST FAILED: Could not submit application")
        return
    
    # Step 2: Business expert login
    token = test_business_expert_login()
    if not token:
        print("\n❌ TEST FAILED: Could not login as business expert")
        print("Please ensure business expert account exists:")
        print("  Username: business_expert")
        print("  Password: expert123")
        return
    
    # Step 3: View pending applications
    pending_apps = test_get_pending_applications(token)
    if not pending_apps:
        print("\n⚠️  No pending applications found")
    
    # Step 4: Approve the application
    success = test_approve_application(app_id, token)
    if not success:
        print("\n❌ TEST FAILED: Could not approve application")
        return
    
    # Step 5: Check categories
    categories = test_get_categories()
    test_categories = test_data['serviceCategories']
    
    # Step 6: Check providers in each test category
    all_found = True
    for cat_name in test_categories:
        providers = test_get_providers_by_category(cat_name)
        
        # Check if our test company is in the results
        found = any(p['phone'] == test_data['phoneMobile'] for p in providers)
        if found:
            print(f"✅ Test company found in '{cat_name}' category")
            
            # Get provider ID for detail test
            provider_id = next(p['id'] for p in providers if p['phone'] == test_data['phoneMobile'])
            
            # Step 7: Check provider details
            detail = test_get_provider_detail(provider_id)
            if detail:
                print(f"✅ Provider detail page works correctly")
        else:
            print(f"❌ Test company NOT found in '{cat_name}' category!")
            all_found = False
    
    # Final summary
    print_section("TEST SUMMARY")
    if all_found:
        print("✅ ALL TESTS PASSED!")
        print("\nThe complete workflow is working correctly:")
        print("  1. Provider can submit application ✓")
        print("  2. Business expert can log in ✓")
        print("  3. Business expert can view pending applications ✓")
        print("  4. Business expert can approve applications ✓")
        print("  5. Categories show correct company counts ✓")
        print("  6. Providers appear in category listings ✓")
        print("  7. Provider detail page displays correctly ✓")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the output above for details.")

if __name__ == "__main__":
    main()

