import os
import tempfile
import shutil
import subprocess
import re
from arq import cron
from arq.connections import RedisSettings
from supabase import create_client, Client
from dotenv import load_dotenv

# Import security modules
from services.subprocess_security import secure_subprocess, SecurityError, execute_git_clone
from services.url_validator import url_validator, is_valid_repository_url, sanitize_repository_url, URLValidationError

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
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("CRITICAL: Supabase environment variables missing in worker context")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Convert project_id to int if necessary
        try:
            pid = int(project_id)
        except (ValueError, TypeError):
            pid = project_id

        print(f"Starting analysis for project {pid}")

        # Get project details
        project_response = supabase.table("projects").select("name, repo_url, github_token").eq("id", pid).execute()
        project = project_response.data[0] if project_response.data else None
        
        if not project:
            print(f"Project {pid} not found in database")
            return

        repo_url = project["repo_url"]
        github_token = project.get("github_token")
        
        # Update status to analyzing
        supabase.table("projects").update({"status": "analyzing"}).eq("id", pid).execute()

        print(f"Cloning repository: {repo_url}")

        # Clone to temp directory
        temp_dir = tempfile.mkdtemp()
        repo_dir = os.path.join(temp_dir, "repo")

try:
                # Validate repository URL
                if not is_valid_repository_url(repo_url):
                    raise URLValidationError(f"Invalid repository URL: {sanitize_repository_url(repo_url)}")
                
                # Prepare clone command with security validation
                clone_cmd = ["git", "clone", "--depth", "1", repo_url, repo_dir]
                if github_token:
                    github_match = re.match(r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
                    if github_match:
                        owner, repo = github_match.groups()
                        auth_repo_url = f"https://{github_token}@github.com/{owner}/{repo}.git"
                        clone_cmd = ["git", "clone", "--depth", "1", auth_repo_url, repo_dir]

                # Set environment to prevent git from hanging on credentials prompt
                env = os.environ.copy()
                env["GIT_TERMINAL_PROMPT"] = "0"

                # Execute clone using secure subprocess
                result = execute_git_clone(repo_url, repo_dir, timeout=300)
                
                if result.returncode != 0:
                    error_msg = result.stderr
                    if github_token:
                        error_msg = error_msg.replace(github_token, "[REDACTED]")
                    supabase.table("projects").update({"status": "error"}).eq("id", pid).execute()
                    print(f"Clone failed for project {pid}: {error_msg}")
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
                supabase.table("files").delete().eq("project_id", pid).execute()
                supabase.table("files").insert(files_to_insert).execute()
            
            # Update status to active
            supabase.table("projects").update({"status": "active"}).eq("id", pid).execute()
            print(f"Project {pid} analysis completed. Found {len(files_to_insert)} files.")

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"Error in analyze_project_task for project {project_id}: {e}")
        try:
            supabase.table("projects").update({"status": "error"}).eq("id", project_id).execute()
        except:
            pass

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
