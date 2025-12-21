import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    print(f"\n--- Testing {name} ---")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                keys = list(data.keys()) if isinstance(data, dict) else "List"
                print(f"Success. Keys: {keys}")
            except:
                print(f"Success (text): {response.text[:100]}")
        else:
            print(f"Error Body: {response.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

# 1. Test Git History
test_endpoint("Git History", f"{BASE_URL}/docs/test-project/history/backend/main.py?repo_path=.")

# 2. Test Git Stats
test_endpoint("Git Stats", f"{BASE_URL}/docs/test-project/history/stats?path=backend/main.py&repo_path=.")

# 3. Test Search
test_endpoint("Search", f"{BASE_URL}/docs/test-project/search?q=main")

# 4. Test Projects (Checking 500 error)
test_endpoint("Projects List", f"{BASE_URL}/projects")
