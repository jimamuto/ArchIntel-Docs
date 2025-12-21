import os
import sys
from dotenv import load_dotenv

# Add current directory to sys.path so we can import services
sys.path.append(os.getcwd())

from services.llm_service import generate_doc, _call_deepseek

def test_live():
    # Load real env vars from .env
    load_dotenv()

    # Check if key is loaded
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        print("Error: DEEPSEEK_API_KEY not found in environment. Did you save the .env file?")
        return

    print(f"DeepSeek Key found: {key[:5]}...{key[-3:] if len(key)>5 else ''}")

    # 1. Direct Test
    print("\n--- 1. Testing Direct DeepSeek Call ---")
    try:
        print("Sending request to DeepSeek (model: deepseek-reasoner)...")
        result = _call_deepseek("Return the word 'SUCCESS' if you can read this.", key)
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
    else:
        print("GROQ_API_KEY was not set anyway.")

    try:
        # This should now hit DeepSeek
        print("Calling generate_doc()...")
        result = generate_doc("Write a one-sentence docstring for a void function.")
        print(f"Fallback Flow Result: {result}")
        
        if "ArchIntel Analysis" in result and "Static Analysis" in result:
             print("\nWARNING: It seems to have fallen back to MOCK data. Check DeepSeek logs above.")
        else:
             print("\nSUCCESS: Received a generated response (likely from DeepSeek).")

    finally:
        # Restore 
        if original_groq:
            os.environ["GROQ_API_KEY"] = original_groq

if __name__ == "__main__":
    test_live()
