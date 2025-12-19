from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import PlainTextResponse
from supabase import create_client, Client
import os
import pathlib
import ast

router = APIRouter()

# --- New endpoint: Extract code from a file for a project ---
@router.get("/{project_id}/file/code", response_class=PlainTextResponse)
def get_file_code(project_id: str, path: str = Query(..., description="Relative path of the file in the project"), repo_path: str = Query(None, description="Local path to the repo (optional, for local projects)")):
    """
    Returns the code content of a file for a given project and relative file path.
    If repo_path is not provided or repository is not available, returns a placeholder message.
    """
    try:
        if not repo_path:
            return "// Repository path not provided. Please ensure the project repository is cloned locally."

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

        if not os.path.exists(abs_path):
            return f"// File not found: {path}\n// The repository may not be cloned locally or the file path may be incorrect.\n// Repository path: {repo_path}\n// Full path: {repo_path_full}"

        # Check if repo_path exists
        if not os.path.exists(repo_path_full):
            return f"// Repository not found locally: {repo_path}\n// Full path: {repo_path_full}\n// Please clone the repository first to view source code."

        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
        return code
    except Exception as e:
        return f"// Error reading file: {str(e)}\n// File path: {path}\n// Repository path: {repo_path or 'Not provided'}"

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
def get_projects():
    try:
        response = supabase.table("projects").select("id, name, repo_url, status, created_at, updated_at").execute()
        projects = response.data if hasattr(response, 'data') else response["data"]
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def register_project(request: Request):
    data = await request.json()
    name = data.get("name")
    repo_url = data.get("repo_url")
    if not name or not repo_url:
        raise HTTPException(status_code=400, detail="Missing name or repo_url")
    try:
        response = supabase.table("projects").insert({"name": name, "repo_url": repo_url, "status": "ready"}).execute()
        project = response.data[0] if hasattr(response, 'data') and response.data else response["data"][0]
        return {"message": "Project registered", "project": project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/ingest/code")
async def ingest_code(project_id: str, request: Request):
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
                    rel_path = os.path.relpath(file_path, repo_path)
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
                        rel_path = os.path.relpath(file_path, repo_path)
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
def get_structure(project_id: str):
    try:
        response = supabase.table("files").select("id, path, language").eq("project_id", project_id).execute()
        files = response.data if hasattr(response, 'data') else response["data"]
        return {"structure": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/clone")
def clone_and_ingest_code(project_id: str):
    try:
        import subprocess
        import shutil

        # Get project details
        project_response = supabase.table("projects").select("name, repo_url").eq("id", project_id).execute()
        try:
            project = project_response.data[0]
        except (AttributeError, IndexError, TypeError):
            try:
                project = project_response["data"][0]
            except (KeyError, IndexError, TypeError):
                raise HTTPException(status_code=404, detail="Project not found")

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        repo_url = project["repo_url"]
        repo_name = repo_url.split('/')[-1].replace('.git', '')

        # Create permanent repos directory
        repos_dir = os.path.join(os.getcwd(), "repos")
        os.makedirs(repos_dir, exist_ok=True)

        repo_path = os.path.join(repos_dir, repo_name)

        # Check if repo already exists
        if os.path.exists(repo_path):
            # If it exists, just update it
            try:
                subprocess.run(['git', 'pull'], cwd=repo_path, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError:
                # If pull fails, remove and reclone
                shutil.rmtree(repo_path)
                subprocess.run(['git', 'clone', repo_url, repo_path], check=True, capture_output=True, text=True)
        else:
            # Clone the repository
            subprocess.run(['git', 'clone', repo_url, repo_path], check=True, capture_output=True, text=True)

        # Now ingest the code using the existing endpoint logic
        files = []
        for dirpath, _, filenames in os.walk(repo_path):
            if any(excluded in dirpath for excluded in ["venv", "node_modules", ".git"]):
                continue
            for filename in filenames:
                # Check for exact filename matches (like Makefile, Dockerfile)
                if filename in LANGUAGE_EXTENSIONS:
                    language = LANGUAGE_EXTENSIONS[filename]
                    file_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(file_path, repo_path)
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
                        rel_path = os.path.relpath(file_path, repo_path)
                        files.append({
                            "project_id": project_id,
                            "path": rel_path,
                            "language": language
                        })

        if files:
            supabase.table("files").insert(files).execute()
            return {"message": f"Successfully cloned and ingested {len(files)} files from {repo_url}", "repo_path": repo_path}
        else:
            return {"message": f"Repository cloned but no supported code files found in {repo_url}", "repo_path": repo_path}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone repository: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
def delete_project(project_id: str):
    try:
        # First delete all files associated with the project
        supabase.table("files").delete().eq("project_id", project_id).execute()

        # Then delete the project itself
        response = supabase.table("projects").delete().eq("id", project_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return {"message": "Project deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
