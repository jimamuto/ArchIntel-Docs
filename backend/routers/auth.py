import os
import httpx
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from supabase import create_client, Client
from typing import Optional

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get the currently authenticated user from Supabase.
    Expects 'Authorization: Bearer <access_token>'
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        # Verify the token with Supabase
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid session or token")
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

async def get_supabase_client(authorization: Optional[str] = Header(None)):
    """
    Dependency that returns a Supabase client pre-configured with the user's JWT.
    This ensures that Row-Level Security (RLS) policies are correctly applied.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    # Create a NEW client instance for this request with the user's JWT
    # This is necessary because the global client uses the anon key
    user_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    user_supabase.postgrest.auth(token)
    return user_supabase

@router.get("/github/login")
async def github_login():
    """
    Redirects the user to GitHub to authorize the app.
    Scopes: 'repo' is needed to access private repositories.
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID is not configured.")
    
    scope = "repo"
    redirect_uri = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={scope}"
    return RedirectResponse(redirect_uri)

@router.get("/github/callback")
async def github_callback(code: str):
    """
    Exchanges the authorization code for an access token.
    Returns the token to the frontend via a simple HTML page that communicates with the parent window (if opened in popup).
    """
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub credentials are not configured.")
    
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        # GitHub expects form-encoded data, not JSON
        response = await client.post(token_url, headers=headers, data=data)
        
    if response.status_code != 200:
        error_html = f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h3 style="color: #ef4444;">Authentication Failed</h3>
                <p style="color: #9ca3af;">Failed to retrieve token from GitHub.</p>
                <p style="color: #6b7280; font-size: 12px;">Status: {response.status_code}</p>
                <button onclick="window.close()" style="margin-top: 20px; padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer;">
                    Close Window
                </button>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        error_description = token_data.get('error_description', 'Unknown error')
        error_html = f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h3 style="color: #ef4444;">Error: Could not retrieve token</h3>
                <p style="color: #9ca3af;">{error_description}</p>
                <button onclick="window.close()" style="margin-top: 20px; padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer;">
                    Close Window
                </button>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    # Return a script that sends the token to the main window and closes the popup
    html_content = f"""
    <html>
        <body>
            <div style="font-family: sans-serif; text-align: center; padding: 50px;">
                <div style="width: 64px; height: 64px; margin: 0 auto 20px; background: linear-gradient(135deg, #a855f7, #06b6d4); border-radius: 16px; display: flex; align-items: center; justify-content: center;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                </div>
                <h3 style="color: #4ade80; margin-bottom: 8px;">Authentication Successful!</h3>
                <p style="color: #9ca3af;">Redirecting you back to ArchIntel...</p>
            </div>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{ type: 'GITHUB_AUTH_SUCCESS', token: '{access_token}' }}, '*');
                    setTimeout(() => window.close(), 1000);
                }} else {{
                    // If not a popup, redirect to projects page
                    setTimeout(() => window.location.href = 'http://localhost:3000/projects', 2000);
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    """
    Returns the current user profile from Supabase.
    """
    return {"user": user}
