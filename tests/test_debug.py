"""Simple debug test to check what's happening"""

import requests

BASE_URL = "http://127.0.0.1:5000/api"

# Test 1: Login
print("Test 1: Admin Login")
try:
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "admin123"
    }, timeout=5)
    print(f"Status: {response.status_code}")
    token = response.json().get("token")
    print(f"Token: {token[:30]}...\n")
except Exception as e:
    print(f"Error: {e}\n")
    token = None

# Test 2: Try to access dashboard without token
print("Test 2: Access dashboard without token")
try:
    response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text[:200]}\n")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}\n")

# Test 3: Try duplicate category with proper debugging
print("Test 3: Create duplicate category")
if token:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First create
    try:
        response = requests.post(f"{BASE_URL}/admin/categories", 
                               headers=headers,
                               json={"name": "Test Duplicate Category"},
                               timeout=5)
        print(f"First create - Status: {response.status_code}")
        print(f"Body: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}\n")
    
    # Try duplicate
    try:
        response = requests.post(f"{BASE_URL}/admin/categories", 
                               headers=headers,
                               json={"name": "Test Duplicate Category"},
                               timeout=5)
        print(f"Duplicate create - Status: {response.status_code}")
        print(f"Body: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}\n")

# Test 4: Empty name
print("Test 4: Create category with empty name")
if token:
    try:
        response = requests.post(f"{BASE_URL}/admin/categories", 
                               headers=headers,
                               json={},
                               timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}\n")

print("Debug test completed")

