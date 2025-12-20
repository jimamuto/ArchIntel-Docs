from fastapi import APIRouter, HTTPException, Request
from supabase import create_client, Client
import os
from datetime import datetime

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/activity")
def get_activity():
    """
    Fetch system activity logs. 
    If the table doesn't exist yet, we'll return a simulated log based on project activity.
    """
    try:
        # Attempt to get real activity from a table if you were to create one
        # response = supabase.table("activity_logs").select("*").order("created_at", desc=True).limit(20).execute()
        # return {"logs": response.data}
        
        # Simulated activity logs for MVP demonstration
        projects_res = supabase.table("projects").select("name, updated_at, status").execute()
        projects = projects_res.data
        
        logs = []
        for p in projects:
            logs.append({
                "id": f"log-{p['name']}",
                "event": "Project Synchronized" if p['status'] == 'active' else "System Analysis",
                "message": f"Successfully processed architectural nodes for {p['name']}",
                "timestamp": p['updated_at'],
                "type": "success" if p['status'] == 'active' else "info",
                "user": "System Oracle"
            })
            
        # Add some static system logs
        logs.append({
            "id": "sys-1",
            "event": "Engine Startup",
            "message": "ArchIntel Intelligence Node initialized with Groq (Llama 3.3 70B)",
            "timestamp": datetime.now().isoformat(),
            "type": "system",
            "user": "Root"
        })
        
        return {"logs": sorted(logs, key=lambda x: x['timestamp'], reverse=True)}
    except Exception as e:
        return {"logs": [], "error": str(e)}

@router.get("/settings")
def get_settings():
    """Return current system settings"""
    return {
        "ai_provider": "Groq",
        "model": "llama-3.3-70b-versatile",
        "exclusion_patterns": ["node_modules", ".git", "venv", "dist", ".next"],
        "analytics_enabled": True,
        "api_status": "connected" if os.getenv("GROQ_API_KEY") else "missing_key"
    }

@router.post("/settings")
async def update_settings(request: Request):
    """Update system settings (Simplified for MVP)"""
    data = await request.json()
    # In a real app, we would persist these to Supabase 'settings' table or .env
    # For this MVP, we acknowledge the update
    return {"message": "Settings updated successfully (Local Session Only)", "updated": data}
