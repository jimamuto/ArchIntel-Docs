import requests
import json
import sys

BASE_URL = "http://localhost:8000"
LOG_FILE = "debug_results.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

# Clear log
with open(LOG_FILE, "w") as f:
    f.write("--- Start Debug ---\n")

def test_endpoint(name, url):
    log(f"\n--- Testing {name} ---")
    log(f"URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        log(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                keys = list(data.keys()) if isinstance(data, dict) else "List"
                log(f"Success. Keys: {keys}")
                log(f"Confirm Commits: {len(data.get('commits', [])) if 'commits' in data else 'N/A'}")
            except:
                log(f"Success (text): {response.text[:100]}")
        else:
            log(f"Error Body: {response.text}")
    except Exception as e:
        log(f"Request Failed: {e}")

# 1. Test Git History
test_endpoint("Git History", f"{BASE_URL}/docs/test-project/history/backend/main.py?repo_path=.")

# 2. Test Git Stats
test_endpoint("Git Stats", f"{BASE_URL}/docs/test-project/history/stats?path=backend/main.py&repo_path=.")

# 3. Test Search
test_endpoint("Search", f"{BASE_URL}/docs/test-project/search?q=main")

# 4. Test Projects (Checking 500 error)
test_endpoint("Projects List", f"{BASE_URL}/projects")
