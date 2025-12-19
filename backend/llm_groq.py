import os
import httpx

GROQ_API_URL = "https://api.groq.com/v1/generate"  # Placeholder, update to actual endpoint
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def generate_doc_with_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.2
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("text", "")
