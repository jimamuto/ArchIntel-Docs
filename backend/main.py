import sys
import os

# Load environment variables BEFORE importing modules that need them
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import projects, docs

app = FastAPI(title="ArchIntel Docs Backend")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers for modular endpoints
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(docs.router, prefix="/docs", tags=["Docs"])

@app.get("/")
def root():
    return {"message": "ArchIntel Docs Backend is running."}
