import os
import httpx
from dotenv import load_dotenv
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

print("GROQ TEST:")
print("=" * 50)
if groq_key:
    try:
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Say 'Hello from Groq' in one sentence."}],
                "temperature": 0.3
            },
            timeout=15.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()['choices'][0]['message']['content']}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
else:
    print("No Groq key found")

print("\n\nGEMINI TEST:")
print("=" * 50)
if gemini_key:
    try:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": "Say 'Hello from Gemini' in one sentence."}]}],
                "generationConfig": {"temperature": 0.3}
            },
            timeout=15.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()['candidates'][0]['content']['parts'][0]['text']}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
else:
    print("No Gemini key found")
