from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel
from supabase import create_client, Client
import os
import re
from datetime import datetime
from services.github_service import GitHubService
from services.llm_service import generate_doc

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class IngestRequest(BaseModel):
    limit: Optional[int] = 30

@router.post("/{project_id}/ingest/discussions")
async def ingest_discussions(project_id: str, request: IngestRequest = Body(...)):
    """
    Fetch PRs and Issues from GitHub and store them in the database.
    """
    try:
        # 1. Get project details
        project_response = supabase.table("projects").select("name, repo_url, github_token").eq("id", project_id).execute()
        project = project_response.data[0] if hasattr(project_response, 'data') and project_response.data else None
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        repo_url = project["repo_url"]
        github_token = project.get("github_token")

        # Extract owner/repo
        github_match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', repo_url)
        if not github_match:
            raise HTTPException(status_code=400, detail="Only GitHub repositories are supported for discussion ingestion currently.")
        
        owner, repo_name = github_match.groups()

        # 2. Fetch from GitHub
        prs = GitHubService.get_repo_pull_requests(owner, repo_name, github_token, limit=request.limit)
        issues = GitHubService.get_repo_issues(owner, repo_name, github_token, limit=request.limit)
        
        all_discussions = prs + issues
        
        if not all_discussions:
            return {"message": "No discussions found to ingest.", "count": 0}

        # 3. Store in Supabase (upsert)
        for disc in all_discussions:
            data = {
                "project_id": project_id,
                "source": disc["source"],
                "external_id": disc["external_id"],
                "title": disc["title"],
                "body": disc["body"],
                "author": disc["author"],
                "url": disc["url"],
                "created_at": disc["created_at"]
            }
            
            # Use upsert to avoid duplicates
            supabase.table("discussions").upsert(data, on_conflict="project_id, source, external_id").execute()

        return {
            "message": f"Successfully ingested discussions for {project['name']}.",
            "count": len(all_discussions),
            "prs": len(prs),
            "issues": len(issues)
        }

    except Exception as e:
        print(f"Error ingesting discussions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/discussions")
async def get_discussions(
    project_id: str,
    source: Optional[str] = Query(None, regex="^(github_pr|github_issue)$"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Retrieve ingested discussions for a project.
    """
    try:
        query = supabase.table("discussions").select("*").eq("project_id", project_id).order("created_at", desc=True).limit(limit)
        
        if source:
            query = query.eq("source", source)
            
        response = query.execute()
        discussions = response.data if hasattr(response, 'data') else response["data"]
        
        return {"discussions": discussions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/rationale")
async def get_rationale(project_id: str):
    """
    Generate a design rationale for the project by analyzing ingested discussions.
    """
    try:
        # 1. Fetch ingested discussions
        discussions_response = supabase.table("discussions").select("source, title, body, author").eq("project_id", project_id).execute()
        discussions = discussions_response.data if hasattr(discussions_response, 'data') else discussions_response["data"]
        
        if not discussions:
            return {
                "rationale": "# Design Rationale\n\nNo discussions (PRs/Issues) have been ingested for this project yet. Please ingest data to generate an AI-powered design rationale.",
                "discussions_count": 0
            }

        # 2. Prepare prompt for LLM
        discussions_context = ""
        for i, d in enumerate(discussions[:20]): # Limit to top 20 for prompt length
            discussions_context += f"--- Discussion {i+1} ({d['source']}) ---\n"
            discussions_context += f"Title: {d['title']}\n"
            discussions_context += f"Author: {d['author']}\n"
            discussions_context += f"Content: {d['body'][:500]}...\n\n"

        prompt = f"""
You are an expert software architect. Analyze the following Pull Requests and Issues (discussions) from a software project and synthesize a comprehensive "Design Rationale" document in Markdown format.

Your report should include:
1. **Key Design Decisions**: What were the major decisions made based on these discussions?
2. **Trade-offs & Alternatives**: What alternatives were considered? Why was the chosen path preferred?
3. **Known Constraints**: Any limitations or technical debt mentioned.
4. **Author Contributions**: Briefly mention key contributors and their roles in these decisions.

Discussions Data:
{discussions_context}

Output only the Markdown document. Keep it professional, insightful, and concise.
"""
        # 3. Call LLM
        rationale = generate_doc(prompt)
        
        return {
            "rationale": rationale,
            "discussions_count": len(discussions)
        }
        
    except Exception as e:
        print(f"Error generating rationale: {e}")
        raise HTTPException(status_code=500, detail=str(e))
