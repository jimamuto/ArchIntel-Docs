import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.path.dirname(__file__))

from services.llm_service import generate_doc

print("=" * 60)
print("TESTING GROQ INTEGRATION")
print("=" * 60)

groq_key = os.getenv("GROQ_API_KEY")
print(f"\nGROQ_API_KEY: {'✓ Found' if groq_key else '✗ Missing'}")

if groq_key:
    print("\nTest 1: Simple question")
    print("-" * 60)
    response = generate_doc("What is a REST API? Answer in one sentence.")
    print(response)
    
    print("\n\nTest 2: Code documentation")
    print("-" * 60)
    response = generate_doc("""
    Generate documentation for this Python function:
    
    def calculate_total(items, tax_rate=0.1):
        subtotal = sum(item['price'] for item in items)
        tax = subtotal * tax_rate
        return subtotal + tax
    """)
    print(response)
    
    print("\n" + "=" * 60)
    print("✅ GROQ IS WORKING!")
    print("=" * 60)
else:
    print("\n❌ No Groq API key found. Add GROQ_API_KEY to .env file.")
