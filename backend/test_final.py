import os
from dotenv import load_dotenv
load_dotenv(override=True)

import sys
sys.path.append(os.path.dirname(__file__))

from services.llm_service import generate_doc

print("=" * 60)
print("TESTING ARCHINTEL LLM INTEGRATION")
print("=" * 60)

# Check keys
print("\n1. Environment Variables:")
print(f"   GROQ_API_KEY: {os.getenv('GROQ_API_KEY')[:20] if os.getenv('GROQ_API_KEY') else 'NOT FOUND'}...")
print(f"   GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20] if os.getenv('GEMINI_API_KEY') else 'NOT FOUND'}...")

# Test the service
print("\n2. Testing LLM Service (auto-selects provider):")
print("-" * 60)
response = generate_doc("Explain what a REST API is in exactly 2 sentences.")
print(response)
print("-" * 60)

print("\n✅ Test completed!")
print("=" * 60)
