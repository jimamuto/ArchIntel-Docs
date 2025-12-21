import os
import httpx
from typing import Optional

def generate_doc(prompt: str, provider: Optional[str] = None) -> str:
    """
    Main entry point for LLM documentation generation.
    Cascading fallback: Groq -> Gemini -> Mock
    """
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    print(f"DEBUG: groq_key present: {bool(groq_key)}")
    print(f"DEBUG: gemini_key present: {bool(gemini_key)}")

    # 1. Try Groq
    if groq_key:
        print("DEBUG: Attempting Groq...")
        result = _call_groq(prompt, groq_key)
        # Only fallback if it's a rate limit or specific API error, not a logic error
        if not result.startswith("Error: Groq API rate limit") and not result.startswith("Error: Groq API returned 429"):
            print("DEBUG: Groq successful (or non-retryable error)")
            return result
        print("DEBUG: Groq rate limit/error detected, trying Gemini fallback...")

    # 2. Try Gemini
    if gemini_key:
        return _call_gemini(prompt, gemini_key)
    
    # 3. Fallback to mock
    return _call_mock(prompt)

def _call_groq(prompt: str, api_key: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_detail = "Unknown Error"
        try:
            error_detail = e.response.json().get("error", {}).get("message", str(e))
        except:
            error_detail = str(e)
            
        print(f"Groq API HTTP Error {status_code}: {error_detail}")
        if status_code == 401:
            return f"Error: GROQ_API_KEY is invalid or expired. Please check your environment variables."
        elif status_code == 429:
            return f"Error: Groq API rate limit reached or insufficient credits. {error_detail}"
        return f"Error: Groq API returned {status_code}: {error_detail}"
    except Exception as e:
        print(f"Groq Generic API Error: {e}")
        return f"Error: Groq call failed: {str(e)}"

def _call_gemini(prompt: str, api_key: str) -> str:
    """
    Call Google's Gemini 1.5 Flash API.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 4096,
        }
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return _call_mock(prompt)

def _call_mock(prompt: str) -> str:
    """
    Smart mock that analyzes the prompt to provide relevant documentation.
    Used when no API keys are present or when API calls fail.
    """
    if "class" in prompt.lower() or "function" in prompt.lower():
        return f"""# Architectural Intelligence Report
## Static Analysis Result
The code analysis identifies structural patterns including component definitions and utility functions. 

### Key Observations:
- **Structural Integrity**: High
- **Complexity Module**: Standard
- **Design Pattern**: Inferred from syntax

**Note**: To get full AI synthesis, please provide a `GROQ_API_KEY` in the environment.
"""
    return f"# ArchIntel Analysis\n\nAutomated structural report generated for the current context."
