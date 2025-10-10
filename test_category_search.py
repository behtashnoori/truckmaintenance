import requests
import json

def test_category_search():
    """Test category search API"""
    try:
        # Test with تعمیرات موتور category
        url = 'http://127.0.0.1:5000/api/public/providers'
        params = {
            'lat': 35.6892,
            'lon': 51.3890,
            'category': 'تعمیرات موتور'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Category Search API Response:")
            print(f"Success: {data.get('success')}")
            print(f"Data type: {type(data.get('data'))}")
            print(f"Data length: {len(data.get('data', []))}")
            print("\nFull response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_category_search()
