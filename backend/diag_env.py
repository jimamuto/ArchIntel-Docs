import os
from dotenv import load_dotenv

# Replicate main.py's loading logic
print("--- Diagnostic Environment Check ---")
print(f"Working Directory: {os.getcwd()}")
print(f"Loading .env from current directory...")
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY") 

print(f"GROQ_API_KEY present: {bool(groq_key)}")
if groq_key:
    print(f"GROQ_API_KEY starts with: {groq_key[:5]}...")

print(f"GEMINI_API_KEY present: {bool(gemini_key)}")
if gemini_key:
    print(f"GEMINI_API_KEY starts with: {gemini_key[:5]}...")
print("-----------------------------------")
