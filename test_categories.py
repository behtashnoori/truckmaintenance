import requests
import json

def test_categories():
    try:
        response = requests.get('http://127.0.0.1:5000/api/public/categories')
        if response.status_code == 200:
            data = response.json()
            print("✅ Categories API Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_categories()
