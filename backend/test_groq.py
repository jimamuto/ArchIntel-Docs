import os
from dotenv import load_dotenv
load_dotenv(override=True)

import sys
sys.path.append(os.path.dirname(__file__))

from services.llm_service import generate_doc

print("Testing LLM with Groq key...")
print("=" * 50)

# Move the Groq key to the correct env var
groq_key = os.getenv("GEMINI_API_KEY")  # This is actually a Groq key
if groq_key and groq_key.startswith("gsk_"):
    os.environ["GROQ_API_KEY"] = groq_key
    print(f"Using Groq key: {groq_key[:20]}...")
    
response = generate_doc("Explain what a microservice is in 2 sentences.")
print(response)
print("=" * 50)
