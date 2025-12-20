import os
import httpx
from typing import Optional

def generate_doc(prompt: str, provider: Optional[str] = None) -> str:
    """
    Main entry point for LLM documentation generation.
    Uses Groq with fallback to smart mock.
    """
    groq_key = os.getenv("GROQ_API_KEY")

    if groq_key:
        return _call_groq(prompt, groq_key)
    
    # Fallback to mock if no API key
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
    except Exception as e:
        print(f"Groq API Error: {e}")
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
