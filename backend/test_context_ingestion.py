from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import pytest

client = TestClient(app)

def test_get_discussions_endpoint_exists():
    # Mock Supabase to avoid 500 if table doesn't exist
    with patch("routers.context.supabase") as mock_supabase:
        mock_supabase.table().select().eq().order().limit().execute.return_value.data = []
        response = client.get("/context/mock-id/discussions")
        assert response.status_code == 200
        assert "discussions" in response.json()

@patch("services.github_service.GitHubService.get_repo_pull_requests")
@patch("services.github_service.GitHubService.get_repo_issues")
def test_ingest_discussions_mock(mock_issues, mock_prs):
    # Mock GitHub responses
    mock_prs.return_value = [{
        "external_id": "1",
        "title": "Merged PR",
        "body": "Rationale here",
        "author": "dev",
        "url": "http://github.com/pr/1",
        "created_at": "2024-01-01T00:00:00Z",
        "source": "github_pr"
    }]
    mock_issues.return_value = []

    # Mock Supabase
    with patch("routers.context.supabase") as mock_supabase:
        mock_supabase.table().select().eq().execute.return_value.data = [{"id": "uuid", "name": "project", "repo_url": "https://github.com/owner/repo"}]
        mock_supabase.table().upsert().execute.return_value = MagicMock()

        response = client.post("/context/project-id/ingest/discussions", json={"limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["prs"] == 1
        assert data["issues"] == 0

def test_get_rationale_endpoint():
    with patch("routers.context.supabase") as mock_supabase:
        mock_supabase.table().select().eq().execute.return_value.data = [
            {"source": "github_pr", "title": "Add auth", "body": "Implementing JWT", "author": "dev1"},
            {"source": "github_issue", "title": "Fix bug", "body": "Race condition in login", "author": "dev2"}
        ]
        
        with patch("routers.context.generate_doc", return_value="AI Generated Rationale"):
            response = client.get("/context/test-project/rationale")
            assert response.status_code == 200
            data = response.json()
            assert "rationale" in data
            assert data["rationale"] == "AI Generated Rationale"
            assert data["discussions_count"] == 2
