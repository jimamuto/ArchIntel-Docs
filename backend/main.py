import sys
import os

# Load environment variables BEFORE importing modules that need them
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from arq import create_pool
from arq.connections import RedisSettings
from routers import projects, docs, system, auth, context

app = FastAPI(title="ArchIntel Docs Backend")

# CORS setup
allowed_origins = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup_event():
    # Use redis://localhost:6379 by default or whatever is in env
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    source = "env" if os.getenv("REDIS_URL") else "default"
    try:
        app.state.arq_pool = await create_pool(RedisSettings.from_dsn(redis_url))
        print(f"Connected to Redis for background tasks at {redis_url} (source: {source})")
    except Exception as e:
        print(f"Warning: Could not connect to Redis at {redis_url} (source: {source}). Background tasks will be disabled. Error: {e}")
        app.state.arq_pool = None

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "arq_pool") and app.state.arq_pool:
        await app.state.arq_pool.close()

# Include routers for modular endpoints
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(docs.router, prefix="/docs", tags=["Docs"])
app.include_router(context.router, prefix="/context", tags=["Context"])
app.include_router(system.router, prefix="/system", tags=["System"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "ArchIntel Docs Backend is running."}
