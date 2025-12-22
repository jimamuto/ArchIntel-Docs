from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import PlainTextResponse, FileResponse
import tempfile
import shutil
import subprocess
from supabase import create_client, Client
import os
import pathlib
import ast
import gzip
import hashlib
import base64
from datetime import datetime

from routers.auth import get_current_user, get_supabase_client

router = APIRouter()

# --- Stateless endpoint: Extract documentation from GitHub repo and return as download ---
@router.post("/stateless/extract-docs")
async def stateless_extract_docs(request: Request):
    """
    Accepts a JSON body with a 'repo_url'.
    Clones the repo to a temp dir, extracts documentation files, zips them, and returns the zip for download.
    No data is stored in the database.
    """
    data = await request.json()
    repo_url = data.get("repo_url")
    if not repo_url:
        raise HTTPException(status_code=400, detail="Missing 'repo_url' in request body")

    temp_dir = tempfile.mkdtemp()
    zip_path = None
    try:
        # Clone the repo to temp_dir/repo
        repo_dir = os.path.join(temp_dir, "repo")
        result = subprocess.run(["git", "clone", "--depth", "1", repo_url, repo_dir], capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Git clone failed: {result.stderr}")

        # Collect documentation files (README, .md, .rst, .txt, /docs/)
        doc_files = []
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                if file.lower().startswith("readme") or file.lower().endswith((".md", ".rst", ".txt")):
                    doc_files.append(os.path.join(root, file))
            # Also include everything in a 'docs' folder
            if "docs" in dirs:
                docs_dir = os.path.join(root, "docs")
                for docs_root, _, docs_files in os.walk(docs_dir):
                    for docs_file in docs_files:
                        doc_files.append(os.path.join(docs_root, docs_file))

        if not doc_files:
            raise HTTPException(status_code=404, detail="No documentation files found in the repository.")

        # Create a zip file with the documentation
        zip_path = os.path.join(temp_dir, "documentation.zip")
        import zipfile
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in doc_files:
                arcname = os.path.relpath(file_path, repo_dir)
                zipf.write(file_path, arcname)

        # Return the zip file as a download
        return FileResponse(zip_path, filename="documentation.zip", media_type="application/zip")
    finally:
        # Clean up temp files after response is sent
        if zip_path and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except Exception:
                pass
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

# --- New endpoint: Extract code from a file for a project ---
@router.get("/{project_id}/file/code", response_class=PlainTextResponse)
def get_file_code(project_id: str, path: str = Query(..., description="Relative path of the file in the project"), repo_path: str = Query(..., description="Local path to the repo"), supabase: Client = Depends(get_supabase_client)):
    """
    Returns the code content of a file for a given project and relative file path.
    Reads from filesystem only (stateless - no database storage).
    """
    temp_dir = None
    try:
        if not repo_path:
            return "// Repository path not provided."

        # Handle different repo_path formats
        if repo_path == ".":
            # Current directory (project root)
            current_dir = os.path.dirname(__file__)  # backend/routers/
            backend_dir = os.path.dirname(current_dir)  # backend/
            repo_path_full = os.path.dirname(backend_dir)  # project root
        elif repo_path.startswith("repos/"):
            # Backend is in backend/routers/ directory, so go up three levels to project root
            current_dir = os.path.dirname(__file__)  # backend/routers/
            backend_dir = os.path.dirname(current_dir)  # backend/
            project_root = os.path.dirname(backend_dir)  # project root
            repo_path_full = os.path.join(project_root, repo_path)
        else:
            repo_path_full = repo_path

        abs_path = os.path.abspath(os.path.join(repo_path_full, path))
        # Security: Ensure abs_path is within repo_path
        if not abs_path.startswith(os.path.abspath(repo_path_full)):
            return "// Invalid file path - access denied for security reasons."

        # Check if repo_path exists locally
        if not os.path.exists(repo_path_full):
            # Repository not found locally, clone it temporarily
            # Get project details to get repo URL
            project_response = supabase.table("projects").select("name, repo_url").eq("id", project_id).execute()
            project = project_response.data[0] if hasattr(project_response, 'data') and project_response.data else project_response["data"][0]

            # Clone repository temporarily
            temp_dir = tempfile.mkdtemp()
            result = subprocess.run(["git", "clone", "--depth", "1", project["repo_url"], repo_path_full], capture_output=True, text=True)
            if result.returncode != 0:
                return f"// Failed to clone repository: {result.stderr}"

        if not os.path.exists(abs_path):
            return f"// File not found: {path}"

        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
        return code
    except Exception as e:
        return f"// Error reading file: {str(e)}\n// File path: {path}"
    finally:
        # Clean up temporary clone if it was created
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

# Mapping of file extensions to programming languages
LANGUAGE_EXTENSIONS = {
    # Python
    '.py': 'python', '.pyc': 'python', '.pyo': 'python', '.pyw': 'python',
    # JavaScript/TypeScript
    '.js': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
    '.mjs': 'javascript', '.cjs': 'javascript',
    # Java
    '.java': 'java', '.class': 'java', '.jar': 'java',
    # C/C++
    '.c': 'c', '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.h': 'c', '.hpp': 'cpp',
    # C#
    '.cs': 'csharp',
    # PHP
    '.php': 'php', '.phtml': 'php', '.php3': 'php', '.php4': 'php', '.php5': 'php', '.php7': 'php', '.php8': 'php',
    # Ruby
    '.rb': 'ruby', '.rbw': 'ruby',
    # Go
    '.go': 'go',
    # Rust
    '.rs': 'rust',
    # Swift
    '.swift': 'swift',
    # Kotlin
    '.kt': 'kotlin', '.kts': 'kotlin',
    # Scala
    '.scala': 'scala', '.sc': 'scala',
    # HTML/CSS
    '.html': 'html', '.htm': 'html', '.css': 'css', '.scss': 'scss', '.sass': 'sass', '.less': 'less',
    # Data/Config
    '.sql': 'sql', '.json': 'json', '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml',
    # Shell
    '.sh': 'shell', '.bash': 'shell', '.zsh': 'shell', '.fish': 'shell',
    # Documentation
    '.md': 'markdown', '.markdown': 'markdown',
    # R
    '.r': 'r', '.rmd': 'r',
    # Perl
    '.pl': 'perl', '.pm': 'perl',
    # Lua
    '.lua': 'lua',
    # Haskell
    '.hs': 'haskell', '.lhs': 'haskell',
    # Erlang
    '.erl': 'erlang', '.hrl': 'erlang',
    # Elixir
    '.ex': 'elixir', '.exs': 'elixir',
    # Clojure
    '.clj': 'clojure', '.cljs': 'clojure', '.cljc': 'clojure',
    # Lisp
    '.lisp': 'lisp', '.lsp': 'lisp', '.cl': 'lisp',
    # Fortran
    '.f': 'fortran', '.f90': 'fortran', '.f95': 'fortran', '.f03': 'fortran',
    # COBOL
    '.cob': 'cobol', '.cbl': 'cobol',
    # Assembly
    '.asm': 'assembly', '.s': 'assembly',
    # MATLAB
    '.m': 'matlab',
    # Julia
    '.jl': 'julia',
    # Dart
    '.dart': 'dart',
    # Objective-C
    '.m': 'objective-c', '.mm': 'objective-c',
    # Pascal
    '.pas': 'pascal', '.pp': 'pascal',
    # Ada
    '.adb': 'ada', '.ads': 'ada',
    # Prolog
    '.pl': 'prolog', '.pro': 'prolog',
    # Scheme
    '.scm': 'scheme', '.ss': 'scheme',
    # Tcl
    '.tcl': 'tcl', '.tk': 'tcl',
    # Smalltalk
    '.st': 'smalltalk',
    # APL
    '.apl': 'apl',
    # BASIC
    '.bas': 'basic', '.vb': 'vb',
    # Visual Basic
    '.vb': 'vb', '.vbs': 'vb',
    # PowerShell
    '.ps1': 'powershell',
    # Batch
    '.bat': 'batch', '.cmd': 'batch',
    # Makefile
    'Makefile': 'makefile', 'makefile': 'makefile',
    # Dockerfile
    'Dockerfile': 'dockerfile',
    # Configuration files
    '.ini': 'ini', '.cfg': 'config', '.conf': 'config', '.properties': 'properties',
}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("")
def get_projects(user = Depends(get_current_user), supabase: Client = Depends(get_supabase_client)):
    try:
        response = supabase.table("projects").select("id, name, repo_url, status, created_at, updated_at").eq("user_id", user.id).execute()
        projects = response.data if hasattr(response, 'data') else response["data"]
        
        # Enrich each project with real-time stats
        for project in projects:
            # Get file count and languages
            files_response = supabase.table("files").select("language").eq("project_id", project["id"]).execute()
            files = files_response.data if hasattr(files_response, 'data') else files_response["data"]
            
            project["file_count"] = len(files)
            
            # Extract unique languages
            languages = list(set([f["language"] for f in files if f.get("language") and f["language"] != "unknown"]))
            project["languages"] = languages[:5]  # Limit to top 5
            
            # Set last_analyzed to updated_at or created_at
            project["last_analyzed"] = project.get("updated_at") or project.get("created_at")
        
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def register_project(request: Request, user = Depends(get_current_user), supabase: Client = Depends(get_supabase_client)):
    data = await request.json()
    name = data.get("name")
    repo_url = data.get("repo_url")
    github_token = data.get("github_token") # Optional: PAT for private repos

    if not name or not repo_url:
        raise HTTPException(status_code=400, detail="Missing name or repo_url")
    try:
        # Check for existing project for THIS user
        existing = supabase.table("projects").select("*").eq("repo_url", repo_url).eq("user_id", user.id).execute()
        existing_data = existing.data if hasattr(existing, 'data') else existing["data"]
        
        if existing_data:
            # Update
            project_id = existing_data[0]["id"]
            update_data = {"name": name, "status": "ready"}
            if github_token:
                update_data["github_token"] = github_token
            
            response = supabase.table("projects").update(update_data).eq("id", project_id).eq("user_id", user.id).execute()
        else:
            # Insert
            insert_data = {"name": name, "repo_url": repo_url, "status": "ready", "user_id": user.id}
            if github_token:
                insert_data["github_token"] = github_token
                
            response = supabase.table("projects").insert(insert_data).execute()
            
        project = response.data[0] if hasattr(response, 'data') and response.data else response["data"][0]
        
        # Trigger background analysis immediately after registration
        if app_state := getattr(request.app, "state", None):
            arq_pool = getattr(app_state, "arq_pool", None)
            if arq_pool:
                await arq_pool.enqueue_job("analyze_project_task", project["id"])
            else:
                print(f"Warning: Background analysis skipped for project {project['id']} (Redis unavailable)")
        
        return {"message": "Project registered and analysis queued", "project": project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/ingest/code")
async def ingest_code(project_id: str, request: Request, supabase: Client = Depends(get_supabase_client)):
    data = await request.json()
    repo_path = data.get("repo_path")
    if not repo_path or not os.path.exists(repo_path):
        raise HTTPException(status_code=400, detail="Invalid or missing repo_path")
    try:
        files = []
        for dirpath, _, filenames in os.walk(repo_path):
            if any(excluded in dirpath for excluded in ["venv", "node_modules", ".git"]):
                continue
            for filename in filenames:
                # Check for exact filename matches (like Makefile, Dockerfile)
                if filename in LANGUAGE_EXTENSIONS:
                    language = LANGUAGE_EXTENSIONS[filename]
                    file_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(file_path, repo_path).replace("\\", "/")
                    files.append({
                        "project_id": project_id,
                        "path": rel_path,
                        "language": language
                    })
                else:
                    # Check for file extension matches
                    _, ext = os.path.splitext(filename)
                    if ext in LANGUAGE_EXTENSIONS:
                        language = LANGUAGE_EXTENSIONS[ext]
                        file_path = os.path.join(dirpath, filename)
                        rel_path = os.path.relpath(file_path, repo_path).replace("\\", "/")
                        files.append({
                            "project_id": project_id,
                            "path": rel_path,
                            "language": language
                        })
        if files:
            supabase.table("files").insert(files).execute()
        else:
            return {"message": f"No supported code files found in repo {repo_path}", "files_count": 0}
        return {"message": f"Code ingested for project {project_id}", "files_count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/structure")
def get_structure(project_id: str, supabase: Client = Depends(get_supabase_client)):
    try:
        response = supabase.table("files").select("id, path, language").eq("project_id", project_id).execute()
        files = response.data if hasattr(response, 'data') else response["data"]
        return {"structure": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/clone")
async def clone_and_ingest_code(project_id: str, request: Request, supabase: Client = Depends(get_supabase_client)):
    """
    Queue background task to clone repository and ingest file metadata.
    """
    try:
        # Check if project exists
        project_response = supabase.table("projects").select("id, name").eq("id", project_id).execute()
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        # Queue the background task
        if app_state := getattr(request.app, "state", None):
            arq_pool = getattr(app_state, "arq_pool", None)
            if arq_pool:
                await arq_pool.enqueue_job("analyze_project_task", project_id)
                # Update status to pending/analyzing
                supabase.table("projects").update({"status": "analyzing"}).eq("id", project_id).execute()
                
                return {
                    "message": "Project analysis task queued",
                    "project_id": project_id,
                    "status": "analyzing"
                }
            else:
                print("Warning: Redis unavailable, falling back to synchronous execution for project {project_id}")
                # For now, let's keep it simple and just return 503 if we specifically want background
                raise HTTPException(status_code=503, detail="Background worker unavailable (Redis connection failed)")
        
        raise HTTPException(status_code=500, detail="Background worker not initialized")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/sync")
async def sync_project(project_id: str, supabase: Client = Depends(get_supabase_client)):
    """
    Synchronizes the project by deleting existing metadata and re-scanning.
    """
    try:
        # 1. Delete existing files
        supabase.table("files").delete().eq("project_id", project_id).execute()
        
        # 2. Update status and queue task
        return await clone_and_ingest_code(project_id, request, supabase)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: str, supabase: Client = Depends(get_supabase_client)):
    try:
        # First delete all files associated with the project
        supabase.table("files").delete().eq("project_id", project_id).execute()

        # Then delete the project itself
        response = supabase.table("projects").delete().eq("id", project_id).execute()

        if not hasattr(response, 'data') or not response.data:
             if not isinstance(response, dict) or not response.get("data"):
                 raise HTTPException(status_code=404, detail="Project not found")

        return {"message": "Project deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
