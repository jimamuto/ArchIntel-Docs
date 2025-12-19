from fastapi import APIRouter

router = APIRouter()

@router.get("/{project_id}")
def get_docs(project_id: str):
    # TODO: Implement docs retrieval logic
    return {"docs": []}
