"""
Git History Service
Extracts commit history from Git repositories
"""
import os
from git import Repo
from datetime import datetime
from typing import List, Dict, Optional

class GitHistoryService:
    """Service for extracting Git commit history"""
    
    @staticmethod
    def get_file_history(repo_path: str, file_path: str, limit: int = 50) -> List[Dict]:
        """
        Get commit history for a specific file
        
        Args:
            repo_path: Path to the Git repository
            file_path: Relative path to the file within the repo
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries with metadata and file changes
        """
        try:
            repo = Repo(repo_path)
            commits = []
            
            # Get commits that affected this file
            for commit in repo.iter_commits(paths=file_path, max_count=limit):
                # Get file stats for this commit
                files_changed = []
                additions = 0
                deletions = 0
                
                # Get diff stats
                if commit.parents:
                    diffs = commit.parents[0].diff(commit, paths=file_path, create_patch=True)
                    for diff in diffs:
                        if diff.a_path == file_path or diff.b_path == file_path:
                            change_type = 'modified'
                            if diff.new_file:
                                change_type = 'added'
                            elif diff.deleted_file:
                                change_type = 'deleted'
                            elif diff.renamed_file:
                                change_type = 'renamed'
                            
                            # Count line changes
                            file_additions = 0
                            file_deletions = 0
                            
                            if diff.diff:
                                diff_text = diff.diff.decode('utf-8', errors='ignore')
                                for line in diff_text.split('\n'):
                                    if line.startswith('+') and not line.startswith('+++'):
                                        file_additions += 1
                                    elif line.startswith('-') and not line.startswith('---'):
                                        file_deletions += 1
                            
                            files_changed.append({
                                'path': diff.b_path or diff.a_path,
                                'changeType': change_type,
                                'additions': file_additions,
                                'deletions': file_deletions
                            })
                            
                            additions += file_additions
                            deletions += file_deletions
                else:
                    # First commit (no parents)
                    files_changed.append({
                        'path': file_path,
                        'changeType': 'added',
                        'additions': 0,
                        'deletions': 0
                    })
                
                commit_data = {
                    'id': commit.hexsha[:7],
                    'hash': commit.hexsha[:7],
                    'fullHash': commit.hexsha,
                    'author': commit.author.name,
                    'email': commit.author.email,
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message.strip(),
                    'filesChanged': len(files_changed),
                    'additions': additions,
                    'deletions': deletions,
                    'files': files_changed
                }
                
                commits.append(commit_data)
            
            return commits
            
        except Exception as e:
            print(f"Error getting file history: {e}")
            return []
    
    @staticmethod
    def get_project_history(repo_path: str, limit: int = 100) -> List[Dict]:
        """
        Get overall commit history for the entire project
        
        Args:
            repo_path: Path to the Git repository
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries
        """
        try:
            repo = Repo(repo_path)
            commits = []
            
            for commit in repo.iter_commits(max_count=limit):
                # Count files changed
                files_changed = 0
                additions = 0
                deletions = 0
                
                if commit.parents:
                    diffs = commit.parents[0].diff(commit, create_patch=True)
                    files_changed = len(diffs)
                    
                    for diff in diffs:
                        if diff.diff:
                            diff_text = diff.diff.decode('utf-8', errors='ignore')
                            for line in diff_text.split('\n'):
                                if line.startswith('+') and not line.startswith('+++'):
                                    additions += 1
                                elif line.startswith('-') and not line.startswith('---'):
                                    deletions += 1
                
                commit_data = {
                    'id': commit.hexsha[:7],
                    'hash': commit.hexsha[:7],
                    'fullHash': commit.hexsha,
                    'author': commit.author.name,
                    'email': commit.author.email,
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message.strip(),
                    'filesChanged': files_changed,
                    'additions': additions,
                    'deletions': deletions
                }
                
                commits.append(commit_data)
            
            return commits
            
        except Exception as e:
            print(f"Error getting project history: {e}")
            return []

    @staticmethod
    def get_commit_diff(repo_path: str, commit_hash: str, file_path: Optional[str] = None) -> str:
        """
        Get the raw unified diff for a specific commit.
        If file_path is provided, only shows diff for that file.
        """
        try:
            repo = Repo(repo_path)
            commit = repo.commit(commit_hash)
            
            # If it's the first commit, we need a special case or diff against NULL
            if not commit.parents:
                # For first commit, we can use git show
                return repo.git.show(commit_hash, "--format=", file_path) if file_path else repo.git.show(commit_hash, "--format=")

            parent = commit.parents[0]
            
            # Use git-python to get unified diff
            if file_path:
                return repo.git.diff(parent.hexsha, commit.hexsha, "--", file_path)
            else:
                return repo.git.diff(parent.hexsha, commit.hexsha)
                
        except Exception as e:
            print(f"Error getting commit diff: {e}")
            return f"Error loading diff: {str(e)}"

    @staticmethod
    def get_author_stats(repo_path: str, path: Optional[str] = None) -> List[Dict]:
        """
        Aggregate commit statistics by author for a specific path (file or folder).
        """
        try:
            repo = Repo(repo_path)
            stats = {}
            
            kwargs = {}
            if path:
                kwargs['paths'] = path

            for commit in repo.iter_commits(**kwargs):
                author = commit.author.name
                if author not in stats:
                    stats[author] = {
                        "name": author,
                        "email": commit.author.email,
                        "commits": 0,
                        "additions": 0,
                        "deletions": 0
                    }
                
                stats[author]["commits"] += 1
                
                # Optionally count lines (this can be slow, so we might want to limit it)
                if commit.parents:
                    diffs = commit.parents[0].diff(commit, paths=path, create_patch=True)
                    for diff in diffs:
                        if path and (diff.a_path != path and diff.b_path != path and not (diff.a_path.startswith(path) or diff.b_path.startswith(path))):
                            continue
                        
                        if diff.diff:
                            diff_text = diff.diff.decode('utf-8', errors='ignore')
                            for line in diff_text.split('\n'):
                                if line.startswith('+') and not line.startswith('+++'):
                                    stats[author]["additions"] += 1
                                elif line.startswith('-') and not line.startswith('---'):
                                    stats[author]["deletions"] += 1
            
            # Convert to list and sort by commits
            result = list(stats.values())
            result.sort(key=lambda x: x["commits"], reverse=True)
            return result
            
        except Exception as e:
            print(f"Error getting author stats: {e}")
            return []
