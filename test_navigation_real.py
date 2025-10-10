#!/usr/bin/env python3
"""
Real Navigation Test Script
Tests navigation functionality with real data from the system
"""

import sys
import os
sys.path.append('backend')

from app import create_app
import requests
import json

def test_navigation_urls():
    """Test navigation URLs with real coordinates"""
    
    # Real coordinates (Tehran)
    user_lat, user_lon = 35.6892, 51.3890  # User location (Tehran center)
    dest_lat, dest_lon = 35.6945, 51.3917  # Provider location
    label = 'تعمیرگاه جامع امین'
    
    print("=== Real Navigation Test ===")
    print(f"User Location: {user_lat}, {user_lon}")
    print(f"Destination: {dest_lat}, {dest_lon}")
    print(f"Label: {label}")
    print()
    
    # Test URLs
    urls = {
        "Neshan": f"https://neshan.org/maps/route?from={user_lat},{user_lon}&to={dest_lat},{dest_lon}&destination_name={label}",
        "Google Maps": f"https://www.google.com/maps/dir/?api=1&destination={dest_lat},{dest_lon}&destination_place_id={label}&origin={user_lat},{user_lon}",
        "Waze": f"https://waze.com/ul?ll={dest_lat},{dest_lon}&navigate=yes&from={user_lat},{user_lon}",
        "Apple Maps": f"http://maps.apple.com/?daddr={dest_lat},{dest_lon}&saddr={user_lat},{user_lon}"
    }
    
    results = {}
    
    for name, url in urls.items():
        print(f"Testing {name}...")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            results[name] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "url": url
            }
            
            if response.status_code == 200:
                print(f"✅ {name} URL works!")
            else:
                print(f"❌ {name} URL failed with status {response.status_code}")
                
        except Exception as e:
            results[name] = {
                "status": "error",
                "success": False,
                "error": str(e),
                "url": url
            }
            print(f"❌ {name} URL error: {e}")
        
        print()
    
    return results

def test_provider_data():
    """Test getting real provider data from API"""
    
    print("=== Testing Provider Data ===")
    
    try:
        # Test getting providers
        response = requests.get("http://127.0.0.1:5000/api/public/providers?lat=35.6892&lon=51.3890&category=تعمیرات موتور")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Provider API works!")
            print(f"Found {len(data.get('data', []))} providers")
            
            if data.get('data'):
                provider = data['data'][0]
                print(f"First provider: {provider.get('name')}")
                print(f"Location: {provider.get('location', {}).get('lat')}, {provider.get('location', {}).get('lon')}")
                return provider
        else:
            print(f"❌ Provider API failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Provider API error: {e}")
    
    return None

def main():
    """Main test function"""
    
    print("🚀 Starting Real Navigation Test")
    print("=" * 50)
    
    # Test provider data
    provider = test_provider_data()
    print()
    
    # Test navigation URLs
    results = test_navigation_urls()
    
    # Summary
    print("=== Test Summary ===")
    working_urls = [name for name, result in results.items() if result['success']]
    failed_urls = [name for name, result in results.items() if not result['success']]
    
    print(f"✅ Working URLs: {', '.join(working_urls)}")
    print(f"❌ Failed URLs: {', '.join(failed_urls)}")
    
    if working_urls:
        print(f"\n🎉 {len(working_urls)} navigation URLs are working!")
        print("You can use these for navigation:")
        for name in working_urls:
            print(f"  - {name}: {results[name]['url']}")
    else:
        print("\n❌ No navigation URLs are working!")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
