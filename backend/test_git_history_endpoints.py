from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import pytest

client = TestClient(app)

# Mock endpoint tests to verify fix
def test_get_file_history_endpoint_success():
    # This test expects 200 now
    response = client.get("/docs/mock-project-id/history/backend/main.py?repo_path=.")
    print(f"History Status: {response.status_code}")
    if response.status_code != 200:
        print(f"History Response: {response.text}")
    assert response.status_code == 200
    assert "commits" in response.json()

def test_get_author_stats_endpoint_success():
    response = client.get("/docs/mock-project-id/history/stats?path=backend/main.py&repo_path=.")
    print(f"Stats Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Stats Response: {response.text}")
    assert response.status_code == 200
    assert "stats" in response.json()

def test_get_files_search_endpoint_success():
    response = client.get("/docs/mock-project-id/search?q=main")
    print(f"Search Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Search Response: {response.text}")
    assert response.status_code == 200
    assert "files" in response.json()

def test_get_project_history_endpoint_success():
    response = client.get("/docs/mock-project-id/history/project?repo_path=.")
    print(f"Project History Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Project History Response: {response.text}")
    assert response.status_code == 200
    json_data = response.json()
    assert "commits" in json_data
    assert isinstance(json_data["commits"], list)


