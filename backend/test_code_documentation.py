import requests
import os
import time

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

PROJECT_NAME = "saveeatsproject"
REPO_URL = "https://github.com/jimamuto/SaveEAT.git"
REPO_PATH = "../soko-predicts"  # The actual cloned repo location

# Use existing working project ID to avoid Supabase issues
EXISTING_PROJECT_ID = "26e8ed46-315c-4d69-b187-c422c5fb093b"

def test_register_project():
    # Skip registration and use existing project
    print(f"Using existing project ID: {EXISTING_PROJECT_ID}")
    return EXISTING_PROJECT_ID

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

def test_get_file_documentation(project_id, structure, repo_path):
    if not structure:
        print("No files to fetch documentation for.")
        return
    file_path = structure[0]["path"]
    # Use LLM endpoint with repo_path
    params = {"path": file_path, "repo_path": repo_path}
    resp = requests.get(f"{API_BASE}/docs/{project_id}/file/doc", params=params)
    print(f"Get LLM File Documentation Response for {file_path}:", resp.text[:500] + "..." if len(resp.text) > 500 else resp.text)
    assert resp.status_code == 200
    doc = resp.text
    assert len(doc) > 0 and not doc.startswith("# Error")
    return doc

if __name__ == "__main__":
    project_id = test_register_project()
    if project_id:
        # Skip clone/ingest since project already has files
        structure = test_get_structure(project_id)
        print(f"Structure: {structure}")
        if structure and len(structure) > 0:
            doc = test_get_file_documentation(project_id, structure, REPO_PATH)
            print(f"Sample documentation from first file:\n{doc[:1000]}{'...' if doc and len(doc) > 1000 else ''}")
        else:
            print("No files available for documentation testing.")
    else:
        print("Project setup failed.")
