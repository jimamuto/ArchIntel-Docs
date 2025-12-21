import os
import sys
from dotenv import load_dotenv

# Add current directory to sys.path
sys.path.append(os.getcwd())

from services.llm_service import generate_doc, _call_openrouter

def test_live():
    # Load real env vars from .env
    load_dotenv()

    # Check if key is loaded
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("Error: OPENROUTER_API_KEY not found in environment.")
        return

    print(f"OpenRouter Key found: {key[:5]}...{key[-3:] if len(key)>5 else ''}")

    # 1. Direct Test
    print("\n--- 1. Testing Direct OpenRouter Call ---")
    try:
        print("Sending request to OpenRouter (model: deepseek/deepseek-r1-0528:free)...")
        result = _call_openrouter("Return the word 'SUCCESS' if you can read this.", key)
        print(f"Direct Result: {result}\n")
    except Exception as e:
        print(f"Direct Call Failed: {e}")
        return

    # 2. Fallback Test
    print("--- 2. Testing Fallback Logic (Simulating Groq Failure) ---")
    # Back up Groq key and remove it to force fallback
    original_groq = os.environ.get("GROQ_API_KEY")
    if original_groq:
        del os.environ["GROQ_API_KEY"]
        print("Temporarily removed GROQ_API_KEY from env to force fallback.")

    try:
        # This should now hit OpenRouter
        print("Calling generate_doc()...")
        result = generate_doc("Write a one-sentence docstring for a void function.")
        print(f"Fallback Flow Result: {result}")
        
        if "ArchIntel Analysis" in result and "Static Analysis" in result:
             print("\nWARNING: It seems to have fallen back to MOCK data. Check logs above.")
        else:
             print("\nSUCCESS: Received a generated response (likely from OpenRouter).")

    finally:
        # Restore 
        if original_groq:
            os.environ["GROQ_API_KEY"] = original_groq

if __name__ == "__main__":
    test_live()
