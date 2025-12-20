import os
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

print("Direct .env test:")
print("=" * 50)
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20] if os.getenv('GEMINI_API_KEY') else 'NOT FOUND'}...")
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')[:20] if os.getenv('GOOGLE_API_KEY') else 'NOT FOUND'}...")
print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')[:20] if os.getenv('GROQ_API_KEY') else 'NOT FOUND'}...")
print("=" * 50)

# Now test Gemini
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if gemini_key:
    print("\nTesting Gemini API...")
    import httpx
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello in one sentence"}]}]
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS: {result['candidates'][0]['content']['parts'][0]['text']}")
            else:
                print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
else:
    print("\nNo Gemini key found!")
