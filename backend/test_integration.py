import requests
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def test_register_project():
    resp = requests.post(f"{API_BASE}/projects", json={"name": "Test Project", "repo_url": "https://github.com/example/repo"})
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    print("Register project: PASS")

def test_ingest_code():
    # This assumes a project with id '1' exists
    resp = requests.post(f"{API_BASE}/projects/1/ingest/code")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    print("Ingest code: PASS")

def test_get_structure():
    resp = requests.get(f"{API_BASE}/projects/1/structure")
    assert resp.status_code == 200
    data = resp.json()
    assert "structure" in data
    print("Get structure: PASS")

def test_get_docs():
    resp = requests.get(f"{API_BASE}/docs/1")
    assert resp.status_code == 200
    data = resp.json()
    assert "docs" in data
    print("Get docs: PASS")

if __name__ == "__main__":
    test_register_project()
    test_ingest_code()
    test_get_structure()
    test_get_docs()
