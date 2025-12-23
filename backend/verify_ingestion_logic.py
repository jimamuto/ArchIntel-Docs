
import unittest
from unittest.mock import patch, MagicMock
from services.github_service import GitHubService

class TestGitHubIngestion(unittest.TestCase):

    @patch('requests.get')
    def test_get_repo_pull_requests_includes_closed(self, mock_get):
        # Mock GitHub /pulls response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Merged PR",
                "body": "Body 1",
                "user": {"login": "user1"},
                "merged_at": "2023-01-01T00:00:00Z",
                "html_url": "url1",
                "created_at": "2023-01-01T00:00:00Z"
            },
            {
                "number": 2,
                "title": "Unmerged Closed PR",
                "body": None,
                "user": {"login": "user2"},
                "merged_at": None,
                "html_url": "url2",
                "created_at": "2023-01-01T00:00:00Z"
            }
        ]
        mock_get.return_value = mock_response

        results = GitHubService.get_repo_pull_requests("owner", "repo")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "merged")
        self.assertEqual(results[1]["status"], "closed")
        self.assertEqual(results[1]["body"], "") # Check None handling

    @patch('requests.get')
    def test_get_repo_issues_filters_prs(self, mock_get):
        # Mock GitHub /issues response (which contains PRs)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 3,
                "title": "Actual Issue",
                "body": "Body 3",
                "user": {"login": "user3"},
                "state": "closed",
                "html_url": "url3",
                "created_at": "2023-01-01T00:00:00Z"
                # NO pull_request key
            },
            {
                "number": 4,
                "title": "PR that looks like an issue",
                "body": "Body 4",
                "user": {"login": "user4"},
                "state": "closed",
                "html_url": "url4",
                "created_at": "2023-01-01T00:00:00Z",
                "pull_request": {} # PR key present
            }
        ]
        mock_get.return_value = mock_response

        results = GitHubService.get_repo_issues("owner", "repo")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["external_id"], "3")
        self.assertEqual(results[0]["source"], "github_issue")

if __name__ == '__main__':
    unittest.main()
