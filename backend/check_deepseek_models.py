import os
import httpx
from dotenv import load_dotenv

def check_models():
    load_dotenv('c:\\archintel\\backend\\.env')
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("No API Key found.")
        return

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    models_to_test = ["deepseek-chat", "deepseek-reasoner"]
    
    for model in models_to_test:
        print(f"\nTesting model: {model}...")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }
        try:
            response = httpx.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"SUCCESS: {model} is working.")
                print(f"Response: {response.json()['choices'][0]['message']['content']}")
            else:
                print(f"FAILED: {model} returned {response.status_code}")
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"ERROR: {model} exception: {e}")

if __name__ == "__main__":
    check_models()
