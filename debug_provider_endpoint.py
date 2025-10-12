"""
Script to debug provider application endpoint
اسکریپت debug برای بررسی endpoint ثبت درخواست
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint():
    """Test the provider application endpoint"""
    
    print("=" * 60)
    print("Testing Provider Application Endpoint")
    print("=" * 60)
    
    # Test data
    data = {
        "companyName": "شرکت تست دیباگ",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران، تست",
        "phoneMobile": "09121234567",
        "serviceCategories": ["امداد جاده‌ای"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    # Test URL
    url = f"{BASE_URL}/api/provider-applications"
    
    print(f"\n1. URL: {url}")
    print(f"2. Method: POST")
    print(f"3. Data:")
    try:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except UnicodeEncodeError:
        print(json.dumps(data, indent=2, ensure_ascii=True))
    
    try:
        print("\n" + "=" * 60)
        print("Sending request...")
        print("=" * 60)
        
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"\nResponse JSON:")
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(f"\nResponse Text:")
            print(response.text)
        
        if response.status_code == 201:
            print("\n✓ SUCCESS: Request was successful!")
            return True
        else:
            print(f"\n✗ FAILED: Status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n✗ CONNECTION ERROR: Cannot connect to {BASE_URL}")
        print("  Make sure Flask server is running:")
        print("  python scripts/run_backend.py")
        return False
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_endpoint()

