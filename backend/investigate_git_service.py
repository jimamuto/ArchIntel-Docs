import sys
import os
from pprint import pprint

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print(f"Current Working Directory: {os.getcwd()}")
print(f"System Path: {sys.path}")

try:
    from services.git_service import GitHistoryService
    print("Successfully imported GitHistoryService")
except ImportError as e:
    print(f"Failed to import GitHistoryService: {e}")
    sys.exit(1)

# Mock data
repo_path = "."  # Use current repo
file_path = "backend/main.py" 

print(f"\nTesting GitHistoryService on {file_path} in {repo_path}")

try:
    # 1. Test get_file_history
    print("\n--- Testing get_file_history ---")
    commits = GitHistoryService.get_file_history(repo_path, file_path)
    print(f"Found {len(commits)} commits")
    if commits:
        pprint(commits[0])

    # 2. Test get_author_stats
    print("\n--- Testing get_author_stats ---")
    stats = GitHistoryService.get_author_stats(repo_path, file_path)
    print(f"Found {len(stats)} authors")
    if stats:
        pprint(stats[0])

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
