#!/usr/bin/env python3
"""
Comprehensive test script for public API endpoints
Tests all public-facing pages functionality
"""

import requests
import json
import sys
from typing import Dict, Any, List

BASE_URL = "http://127.0.0.1:5000/api/public"

def test_endpoint(url: str, description: str) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        result = {
            'url': url,
            'description': description,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response_time': response.elapsed.total_seconds()
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                result['data'] = data
                result['has_data'] = 'data' in data and data['data'] is not None
                if result['has_data']:
                    if isinstance(data['data'], list):
                        result['data_count'] = len(data['data'])
                    else:
                        result['data_count'] = 1
                else:
                    result['data_count'] = 0
                print(f"✅ Status: {response.status_code} | Data: {result['data_count']} items")
            except json.JSONDecodeError:
                result['error'] = "Invalid JSON response"
                print(f"❌ Status: {response.status_code} | Error: Invalid JSON")
        else:
            result['error'] = f"HTTP {response.status_code}"
            print(f"❌ Status: {response.status_code} | Error: {response.text[:100]}")
            
    except requests.exceptions.RequestException as e:
        result = {
            'url': url,
            'description': description,
            'success': False,
            'error': str(e)
        }
        print(f"❌ Connection Error: {e}")
    
    return result

def test_categories():
    """Test categories endpoint"""
    return test_endpoint(f"{BASE_URL}/categories", "Categories List")

def test_locations():
    """Test locations endpoint"""
    return test_endpoint(f"{BASE_URL}/locations", "Locations List")

def test_providers_list():
    """Test providers list with different parameters"""
    results = []
    
    # Test with Tehran coordinates
    params = "lat=35.6892&lon=51.3890"
    results.append(test_endpoint(f"{BASE_URL}/providers?{params}", "Providers List (Tehran)"))
    
    # Test with category filter
    params = "lat=35.6892&lon=51.3890&category=تعمیرات موتور"
    results.append(test_endpoint(f"{BASE_URL}/providers?{params}", "Providers List (Tehran + Engine Repair)"))
    
    # Test with different category
    params = "lat=35.6892&lon=51.3890&category=تعویض روغن"
    results.append(test_endpoint(f"{BASE_URL}/providers?{params}", "Providers List (Tehran + Oil Change)"))
    
    # Test with vehicle filter
    params = "lat=35.6892&lon=51.3890&vehicle=truck"
    results.append(test_endpoint(f"{BASE_URL}/providers?{params}", "Providers List (Tehran + Truck)"))
    
    return results

def test_provider_detail():
    """Test provider detail endpoint"""
    results = []
    
    # First get a list of providers to find valid IDs
    list_result = test_endpoint(f"{BASE_URL}/providers?lat=35.6892&lon=51.3890", "Get Provider IDs")
    
    if list_result['success'] and list_result.get('has_data'):
        providers = list_result['data']['data']
        if providers:
            # Test with first provider
            provider_id = providers[0]['id']
            results.append(test_endpoint(f"{BASE_URL}/providers/{provider_id}", f"Provider Detail (ID: {provider_id})"))
            
            # Test with second provider if available
            if len(providers) > 1:
                provider_id = providers[1]['id']
                results.append(test_endpoint(f"{BASE_URL}/providers/{provider_id}", f"Provider Detail (ID: {provider_id})"))
        else:
            print("⚠️  No providers found to test detail endpoint")
    else:
        print("⚠️  Could not get provider list to test detail endpoint")
    
    # Test with invalid ID
    results.append(test_endpoint(f"{BASE_URL}/providers/99999", "Provider Detail (Invalid ID)"))
    
    return results

def test_health():
    """Test health endpoint"""
    return test_endpoint(f"{BASE_URL}/health", "API Health Check")

def analyze_results(all_results: List[Dict[str, Any]]):
    """Analyze and summarize test results"""
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for result in all_results:
            if not result['success']:
                print(f"  - {result['description']}: {result.get('error', 'Unknown error')}")
    
    # Check for data consistency
    print("\n📋 DATA CONSISTENCY CHECK:")
    
    # Check categories
    categories_result = next((r for r in all_results if 'Categories List' in r['description']), None)
    if categories_result and categories_result['success']:
        categories = categories_result['data']['data']
        print(f"Categories found: {len(categories)}")
        for cat in categories:
            print(f"  - {cat['name']}: {cat.get('companies_count', 0)} companies")
    
    # Check providers
    providers_results = [r for r in all_results if 'Providers List' in r['description'] and r['success']]
    if providers_results:
        print(f"\nProviders tests: {len(providers_results)} successful")
        for result in providers_results:
            if result.get('has_data'):
                print(f"  - {result['description']}: {result['data_count']} providers")
            else:
                print(f"  - {result['description']}: No providers found")

def main():
    """Run all tests"""
    print("🚀 Starting Public API Comprehensive Test")
    print("="*60)
    
    all_results = []
    
    # Test basic endpoints
    all_results.append(test_health())
    all_results.append(test_categories())
    all_results.append(test_locations())
    
    # Test providers
    all_results.extend(test_providers_list())
    all_results.extend(test_provider_detail())
    
    # Analyze results
    analyze_results(all_results)
    
    # Return exit code
    failed_tests = sum(1 for r in all_results if not r['success'])
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} tests failed. Check the results above.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
