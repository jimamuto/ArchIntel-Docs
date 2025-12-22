import os
import tempfile
import shutil
import subprocess
import re
from arq import cron
from arq.connections import RedisSettings
from supabase import create_client, Client
from dotenv import load_dotenv

from llm_groq import generate_doc_with_groq
from services.ast_parser import parse_code_structure

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Mapping of file extensions to programming languages (duplicated for worker context)
LANGUAGE_EXTENSIONS = {
    '.py': 'python', '.js': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
    '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.php': 'php', '.rb': 'ruby', '.go': 'go', '.rs': 'rust',
    '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala', '.html': 'html', '.css': 'css', '.sql': 'sql',
    '.json': 'json', '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml', '.sh': 'shell', '.md': 'markdown'
}

async def analyze_project_task(ctx, project_id: str):
    """
    Background task to clone repo, scan files, and update Supabase.
    """
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Get project details
        project_response = supabase.table("projects").select("name, repo_url, github_token").eq("id", project_id).execute()
        project = project_response.data[0] if project_response.data else None
        
        if not project:
            print(f"Project {project_id} not found")
            return

        repo_url = project["repo_url"]
        github_token = project.get("github_token")
        
        # Update status to analyzing
        supabase.table("projects").update({"status": "analyzing"}).eq("id", project_id).execute()

        # Clone to temp directory
        temp_dir = tempfile.mkdtemp()
        repo_dir = os.path.join(temp_dir, "repo")

        try:
            # Prepare clone command
            clone_cmd = ["git", "clone", "--depth", "1", repo_url, repo_dir]
            if github_token:
                github_match = re.match(r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
                if github_match:
                    owner, repo = github_match.groups()
                    auth_repo_url = f"https://{github_token}@github.com/{owner}/{repo}.git"
                    clone_cmd = ["git", "clone", "--depth", "1", auth_repo_url, repo_dir]

            result = subprocess.run(clone_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                error_msg = result.stderr
                if github_token:
                    error_msg = error_msg.replace(github_token, "[REDACTED]")
                supabase.table("projects").update({"status": "error"}).eq("id", project_id).execute()
                print(f"Clone failed: {error_msg}")
                return

            # Scan files
            files_to_insert = []
            for dirpath, _, filenames in os.walk(repo_dir):
                if any(excluded in dirpath for excluded in ["venv", "node_modules", ".git", ".next", "dist", "build"]):
                    continue
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(dirpath, filename), repo_dir).replace("\\", "/")
                    
                    language = "unknown"
                    if filename in LANGUAGE_EXTENSIONS:
                        language = LANGUAGE_EXTENSIONS[filename]
                    else:
                        _, ext = os.path.splitext(filename)
                        if ext in LANGUAGE_EXTENSIONS:
                            language = LANGUAGE_EXTENSIONS[ext]

                    files_to_insert.append({
                        "project_id": project_id,
                        "path": rel_path,
                        "language": language
                    })

            if files_to_insert:
                # Delete existing files for this project before re-inserting (sync logic)
                supabase.table("files").delete().eq("project_id", project_id).execute()
                supabase.table("files").insert(files_to_insert).execute()
            
            # Update status to active
            supabase.table("projects").update({"status": "active"}).eq("id", project_id).execute()
            print(f"Project {project_id} analysis completed. Found {len(files_to_insert)} files.")

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"Error in analyze_project_task: {e}")
        supabase.table("projects").update({"status": "error"}).eq("id", project_id).execute()

async def generate_system_docs_task(ctx, project_id: str, repo_path: str):
    """
    Background task to generate comprehensive system documentation.
    (Placeholder for now - core cloning/scanning is implemented)
    """
    pass

async def startup(ctx):
    print("Arq worker started")

async def shutdown(ctx):
    print("Arq worker shutting down")

class WorkerSettings:
    functions = [analyze_project_task, generate_system_docs_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379"))
