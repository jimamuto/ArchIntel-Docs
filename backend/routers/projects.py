from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/")
def register_project():
    # TODO: Implement project registration logic
    return {"message": "Project registered (stub)"}

@router.post("/{project_id}/ingest/code")
def ingest_code(project_id: str):
    # TODO: Implement code ingestion logic
    return {"message": f"Code ingested for project {project_id} (stub)"}

@router.get("/{project_id}/structure")
def get_structure(project_id: str):
    # TODO: Implement structure retrieval logic
    return {"structure": []}
