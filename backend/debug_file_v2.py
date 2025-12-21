import requests
import json
import time

BASE_URL = "http://localhost:8000"
LOG_FILE = "debug_results_v2.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

with open(LOG_FILE, "w") as f:
    f.write("--- Start Debug V2 ---\n")

def test_endpoint(name, url):
    log(f"\n--- Testing {name} ---")
    log(f"URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        log(f"Status: {response.status_code}")
        if response.status_code == 200:
            log("Success.")
        else:
            log(f"Error Body: {response.text}")
    except Exception as e:
        log(f"Request Failed: {e}")

# Wait for server startup
time.sleep(2)

# 0. Test Router Root
test_endpoint("Docs Router Root", f"{BASE_URL}/docs/test")

# 1. Test Git History
test_endpoint("Git History", f"{BASE_URL}/docs/test-project/history/backend/main.py?repo_path=.")

# 2. Test Git Stats
test_endpoint("Git Stats", f"{BASE_URL}/docs/test-project/history/stats?path=backend/main.py&repo_path=.")

# 3. Test Search
test_endpoint("Search", f"{BASE_URL}/docs/test-project/search?q=main")

# 4. Test Projects (Checking 500 error)
test_endpoint("Projects List", f"{BASE_URL}/projects")
