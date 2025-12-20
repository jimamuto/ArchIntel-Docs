import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.llm_service import generate_doc, _call_gemini

# Check environment variables
print("Environment Check:")
print("=" * 50)
print(f"GEMINI_API_KEY exists: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"GOOGLE_API_KEY exists: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"GROQ_API_KEY exists: {bool(os.getenv('GROQ_API_KEY'))}")
print("=" * 50)

# Test Gemini directly
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if gemini_key:
    print("\nTesting Gemini API directly...")
    print("=" * 50)
    try:
        response = _call_gemini("Say 'Hello from Gemini!' in one sentence.", gemini_key)
        print(f"SUCCESS: {response}")
    except Exception as e:
        print(f"ERROR: {e}")
    print("=" * 50)
else:
    print("\nNo Gemini API key found in environment!")
