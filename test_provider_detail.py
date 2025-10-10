import requests
import json

def test_provider_detail():
    """Test provider detail API"""
    try:
        # Test with provider ID 92 (تعمیرگاه جامع امین)
        url = 'http://127.0.0.1:5000/api/public/providers/92'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Provider Detail API Response:")
            print(f"Success: {data.get('success')}")
            print(f"Data type: {type(data.get('data'))}")
            print("\nFull response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_provider_detail()
