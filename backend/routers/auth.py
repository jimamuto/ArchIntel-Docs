import os
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

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
        response = await client.post(token_url, headers=headers, json=data)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve token from GitHub.")
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
         return HTMLResponse(content=f"<html><body><h3>Error: Could not retrieve token.</h3><p>{token_data.get('error_description')}</p></body></html>", status_code=400)

    # Return a script that sends the token to the main window and closes the popup
    html_content = f"""
    <html>
        <body>
            <h3>Authentication Successful!</h3>
            <p>You can close this window now.</p>
            <script>
                // Send token to parent window
                if (window.opener) {{
                    window.opener.postMessage({{ type: 'GITHUB_AUTH_SUCCESS', token: '{access_token}' }}, '*');
                    window.close();
                }} else {{
                    // Fallback if not a popup (e.g. direct nav), assume user can manually copy or redirect
                     document.body.innerHTML += "<p>Token: {access_token}</p>";
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
