import requests
import os
import subprocess

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

PROJECT_NAME = "saveeatsproject"
REPO_URL = "https://github.com/jimamuto/SaveEAT.git"
REPO_PATH = os.path.abspath("../SaveEAT")

def clone_repo_locally():
    """Clone the repository locally if it doesn't exist"""
    if not os.path.exists(REPO_PATH):
        print(f"Cloning {REPO_URL} to {REPO_PATH}...")
        os.makedirs(os.path.dirname(REPO_PATH), exist_ok=True)
        subprocess.run(['git', 'clone', REPO_URL, REPO_PATH], check=True)
        print("Repository cloned locally.")
    else:
        print("Repository already exists locally.")

def test_register_project():
    resp = requests.post(f"{API_BASE}/projects", json={"name": PROJECT_NAME, "repo_url": REPO_URL})
    print("Register Project Response:", resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert "project" in data
    return data["project"]["id"] if "project" in data else None

def test_clone_and_ingest(project_id):
    resp = requests.post(f"{API_BASE}/projects/{project_id}/clone")
    print("Clone and Ingest Response:", resp.json())
    assert resp.status_code == 200
    return resp.json()

def test_get_structure(project_id):
    resp = requests.get(f"{API_BASE}/projects/{project_id}/structure")
    print("Get Structure Response:", resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert "structure" in data
    return data["structure"]

def test_get_file_code(project_id, structure, repo_path):
    if not structure:
        print("No files to fetch code for.")
        return
    file_path = structure[0]["path"]
    params = {"path": file_path, "repo_path": repo_path}
    resp = requests.get(f"{API_BASE}/projects/{project_id}/file/code", params=params)
    print(f"Get File Code Response for {file_path}:", resp.text[:200] + ("..." if len(resp.text) > 200 else ""))
    assert resp.status_code == 200
    assert len(resp.text) > 0
    return resp.text

if __name__ == "__main__":
    clone_repo_locally()
    project_id = test_register_project()
    if project_id:
        test_clone_and_ingest(project_id)
        structure = test_get_structure(project_id)
        print(f"Structure: {structure}")
        code = test_get_file_code(project_id, structure, REPO_PATH)
        print(f"Sample code from first file:\n{code[:500]}{'...' if code and len(code) > 500 else ''}")
    else:
        print("Project registration failed.")
