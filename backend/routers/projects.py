from fastapi import APIRouter, HTTPException, Request
from supabase import create_client, Client
import os
import pathlib
import ast

router = APIRouter()

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
        import tempfile
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

        # Create a temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(temp_dir, repo_name)

            try:
                # Clone the repository
                subprocess.run(['git', 'clone', repo_url, repo_path],
                             check=True, capture_output=True, text=True)

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
                    return {"message": f"Successfully cloned and ingested {len(files)} files from {repo_url}"}
                else:
                    return {"message": f"Repository cloned but no supported code files found in {repo_url}"}

            except subprocess.CalledProcessError as e:
                raise HTTPException(status_code=500, detail=f"Failed to clone repository: {e.stderr}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to process repository: {str(e)}")

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
