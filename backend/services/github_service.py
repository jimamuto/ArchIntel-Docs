
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime

class GitHubService:
    """Service for fetching data directly from GitHub API"""
    
    BASE_URL = "https://api.github.com"

    @staticmethod
    def _get_headers(token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

    @staticmethod
    def get_repo_info(owner: str, repo: str, token: Optional[str] = None) -> Dict:
        """Get repository metadata"""
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url, headers=GitHubService._get_headers(token))
        if response.status_code == 200:
            return response.json()
        return {}

    @staticmethod
    def get_file_history(owner: str, repo: str, file_path: str, token: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get commit history for a file via GitHub API
        """
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"path": file_path, "per_page": limit}
        
        try:
            response = requests.get(url, headers=GitHubService._get_headers(token), params=params)
            
            if response.status_code != 200:
                print(f"GitHub API Error: {response.status_code} - {response.text}")
                return []

            commits_data = response.json()
            result = []

            # To avoid N+1 slow requests, we fetch details in parallel for the returned commits
            # We limit this to the requested amount (already limited by GitHub's per_page)
            # but we use a ThreadPool to speed it up.
            from concurrent.futures import ThreadPoolExecutor
            
            def fetch_details(item):
                sha = item["sha"]
                commit = item["commit"]
                author = commit["author"]
                
                details = GitHubService.get_commit_details(owner, repo, sha, token)
                
                return {
                    'id': sha[:7],
                    'hash': sha[:7],
                    'fullHash': sha,
                    'author': author["name"],
                    'email': author["email"],
                    'date': author["date"],
                    'message': commit["message"],
                    'filesChanged': details.get('filesChanged', 1),
                    'additions': details.get('additions', 0),
                    'deletions': details.get('deletions', 0),
                    'files': details.get('files', [])
                }

            with ThreadPoolExecutor(max_workers=5) as executor:
                result = list(executor.map(fetch_details, commits_data))

            return result
        except Exception as e:
            print(f"Error calling GitHub API: {e}")
            return []

    @staticmethod
    def get_commit_details(owner: str, repo: str, sha: str, token: Optional[str] = None) -> Dict:
        """
        Get full details of a commit including diff stats
        """
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/commits/{sha}"
        try:
            response = requests.get(url, headers=GitHubService._get_headers(token))
            if response.status_code != 200:
                return {}
            
            data = response.json()
            stats = data.get("stats", {"additions": 0, "deletions": 0})
            files = []
            
            for f in data.get("files", []):
                files.append({
                    'path': f['filename'],
                    'changeType': f['status'], # modified, added, removed, renamed
                    'additions': f['additions'],
                    'deletions': f['deletions']
                })

            return {
                'additions': stats['additions'],
                'deletions': stats['deletions'],
                'filesChanged': len(files),
                'files': files
            }
        except Exception as e:
            print(f"Error fetching commit details: {e}")
            return {}

    @staticmethod
    def get_commit_diff(owner: str, repo: str, sha: str, token: Optional[str] = None) -> str:
        """
        Get the unified diff for a specific commit via GitHub API
        Note: GitHub API typically returns patches per file. We'll reconstruct a simplified diff view.
        """
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/commits/{sha}"
        try:
            response = requests.get(url, headers=GitHubService._get_headers(token))
            if response.status_code != 200:
                return f"Error: {response.status_code}"
            
            data = response.json()
            diff_output = []
            
            # Message
            diff_output.append(f"Subject: {data['commit']['message']}")
            diff_output.append(f"Author: {data['commit']['author']['name']} <{data['commit']['author']['email']}>")
            diff_output.append(f"Date: {data['commit']['author']['date']}")
            diff_output.append("")
            
            for f in data.get("files", []):
                diff_output.append(f"diff --git a/{f['filename']} b/{f['filename']}")
                if f.get('patch'):
                    diff_output.append(f['patch'])
                else:
                    diff_output.append(f"Binary files or large diff suppressed for {f['filename']}")
                diff_output.append("")
                
            return "\n".join(diff_output)
        except Exception as e:
            return f"Error fetching diff: {str(e)}"

    @staticmethod
    def get_author_stats(owner: str, repo: str, path: Optional[str] = None, token: Optional[str] = None) -> List[Dict]:
        """
        Get aggregated author stats from GitHub.
        Note: This requires iterating many commits, which is expensive on API.
        For MVP, we will fetch the last 100 commits and aggregate.
        """
        # Reuse get_file_history to get commits list
        # If path is None, we need project history - get_file_history handles path param optionally if we adjust it, 
        # checking the code for get_file_history... it takes 'file_path'. 
        
        # Let's just define URL manually here similar to get_file_history but with optional path
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}
        if path:
            params["path"] = path
            
        try:
            response = requests.get(url, headers=GitHubService._get_headers(token), params=params)
            if response.status_code != 200:
                return []
            
            commits_data = response.json()
            stats = {}
            
            for item in commits_data:
                commit = item["commit"]
                author_name = commit["author"]["name"]
                author_email = commit["author"]["email"]
                
                if author_name not in stats:
                    stats[author_name] = {
                        "name": author_name,
                        "email": author_email,
                        "commits": 0,
                        "additions": 0, # Not available in list view without N+1
                        "deletions": 0
                    }
                
                stats[author_name]["commits"] += 1
                # We can't easily get additions/deletions without fetching each commit details
                # For now, we leave them as 0 to avoid rate limits
            
            result = list(stats.values())
            result.sort(key=lambda x: x["commits"], reverse=True)
            return result
            
        except Exception as e:
            print(f"Error fetching author stats: {e}")
            return []
    @staticmethod
    def get_repo_pull_requests(owner: str, repo: str, token: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Fetch merged pull requests from GitHub"""
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {"state": "closed", "per_page": limit, "sort": "updated", "direction": "desc"}
        
        try:
            response = requests.get(url, headers=GitHubService._get_headers(token), params=params)
            if response.status_code != 200:
                print(f"GitHub PR API Error: {response.status_code} - {response.text}")
                return []

            prs = response.json()
            result = []
            for pr in prs:
                # Inclue closed PRs (merged or just closed)
                result.append({
                    "external_id": str(pr["number"]),
                    "title": pr["title"],
                    "body": pr["body"] or "",
                    "author": pr["user"]["login"],
                    "status": "merged" if pr.get("merged_at") else "closed",
                    "url": pr["html_url"],
                    "created_at": pr["created_at"],
                    "source": "github_pr"
                })
            return result
        except Exception as e:
            print(f"Error fetching PRs: {e}")
            return []

    @staticmethod
    def get_repo_issues(owner: str, repo: str, token: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Fetch closed issues from GitHub"""
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/issues"
        # pull_requests are technically issues in GitHub API, but we filter them out
        params = {"state": "closed", "per_page": limit, "sort": "updated", "direction": "desc"}
        
        try:
            response = requests.get(url, headers=GitHubService._get_headers(token), params=params)
            if response.status_code != 200:
                print(f"GitHub Issues API Error: {response.status_code} - {response.text}")
                return []

            issues = response.json()
            result = []
            for issue in issues:
                # Skip PRs (they have a pull_request key)
                if "pull_request" not in issue:
                    result.append({
                        "external_id": str(issue["number"]),
                        "title": issue["title"],
                        "body": issue["body"] or "",
                        "author": issue["user"]["login"],
                        "status": issue["state"],
                        "url": issue["html_url"],
                        "created_at": issue["created_at"],
                        "source": "github_issue"
                    })
            return result
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []
