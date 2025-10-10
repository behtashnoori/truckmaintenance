import requests
import json

def test_frontend_api():
    """Test what the frontend would receive"""
    try:
        # Test the exact endpoint that frontend calls
        response = requests.get('http://127.0.0.1:5000/api/public/categories')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Frontend API Test:")
            print(f"Status: {response.status_code}")
            print(f"Success: {data.get('success')}")
            print(f"Categories count: {len(data.get('data', []))}")
            
            print("\n📊 Categories with provider counts:")
            for cat in data.get('data', []):
                print(f"  - {cat['name']}: {cat['companies_count']} providers")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_api()
