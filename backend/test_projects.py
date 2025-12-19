import requests
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

PROJECT_NAME = "FundiFix Project"
REPO_URL = "https://github.com/jimamuto/FundiFix-Project.git"  # Remote repo URL for FundiFix Project

def test_register_project():
    resp = requests.post(f"{API_BASE}/projects", json={"name": PROJECT_NAME, "repo_url": REPO_URL})
    print("Register Project Response:", resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert "project" in data
    return data["project"]["id"] if "project" in data else None

def test_ingest_code(project_id):
    # Use the locally cloned repo path
    repo_path = "../FundiFix-Project"
    resp = requests.post(f"{API_BASE}/projects/{project_id}/ingest/code", json={"repo_path": repo_path})
    print("Ingest Code Response:", resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert "files_count" in data
    return data["files_count"]

def test_get_structure(project_id):
    resp = requests.get(f"{API_BASE}/projects/{project_id}/structure")
    print("Get Structure Response:", resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert "structure" in data
    return data["structure"]

if __name__ == "__main__":
    project_id = test_register_project()
    if project_id:
        files_count = test_ingest_code(project_id)
        structure = test_get_structure(project_id)
        print(f"Files ingested: {files_count}")
        print(f"Structure: {structure}")
    else:
        print("Project registration failed.")
