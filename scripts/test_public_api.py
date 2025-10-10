"""
Script to test public API endpoints
"""

import requests
import json

def test_public_providers():
    """Test the public providers endpoint"""
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 60)
    print("🧪 تست API Public Providers")
    print("=" * 60)
    
    # Test with Tehran coordinates
    test_cases = [
        {
            "name": "تهران - بدون فیلتر",
            "lat": 35.6892,
            "lon": 51.3890,
            "category": None,
            "vehicle": None
        },
        {
            "name": "تهران - دسته تعمیرات موتور",
            "lat": 35.6892,
            "lon": 51.3890,
            "category": "تعمیرات موتور",
            "vehicle": None
        },
        {
            "name": "تهران - دسته تعمیرات گیربکس",
            "lat": 35.6892,
            "lon": 51.3890,
            "category": "تعمیرات گیربکس",
            "vehicle": None
        },
    ]
    
    for test in test_cases:
        print(f"\n{'─' * 60}")
        print(f"📍 {test['name']}")
        print(f"   Location: ({test['lat']}, {test['lon']})")
        if test['category']:
            print(f"   Category: {test['category']}")
        
        # Build URL
        url = f"{base_url}/api/public/providers"
        params = {
            "lat": test["lat"],
            "lon": test["lon"]
        }
        if test["category"]:
            params["category"] = test["category"]
        if test["vehicle"]:
            params["vehicle"] = test["vehicle"]
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    providers = data.get("data", [])
                    print(f"\n   ✅ Success! Found {len(providers)} providers")
                    
                    for i, provider in enumerate(providers, 1):
                        print(f"\n   Provider #{i}:")
                        print(f"      - نام: {provider['name']}")
                        print(f"      - فاصله: {provider['distance_km']} کیلومتر")
                        print(f"      - شعاع: {provider['radius_km']} کیلومتر")
                        print(f"      - دسته‌ها: {', '.join(provider['categories'])}")
                else:
                    print(f"\n   ❌ API returned error: {data.get('error')}")
            else:
                print(f"\n   ❌ HTTP Error {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        
        except requests.exceptions.ConnectionError:
            print(f"\n   ❌ Connection Error - Backend is not running!")
            break
        except Exception as e:
            print(f"\n   ❌ Error: {str(e)}")
    
    print(f"\n{'=' * 60}")

def test_categories():
    """Test categories endpoint"""
    base_url = "http://127.0.0.1:5000"
    url = f"{base_url}/api/public/categories"
    
    print("\n" + "=" * 60)
    print("🧪 تست API Categories")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                categories = data.get("data", [])
                print(f"\n✅ Found {len(categories)} categories:")
                for cat in categories:
                    print(f"   - {cat['name']}")
            else:
                print(f"\n❌ API returned error: {data.get('error')}")
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error - Backend is not running!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print(f"\n{'=' * 60}")

if __name__ == "__main__":
    test_categories()
    test_public_providers()

