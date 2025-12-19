from fastapi import FastAPI
from routers import projects, docs

app = FastAPI(title="ArchIntel Docs Backend")

# Include routers for modular endpoints
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(docs.router, prefix="/docs", tags=["Docs"])

@app.get("/")
def root():
    return {"message": "ArchIntel Docs Backend is running."}
