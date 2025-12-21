import os
from dotenv import load_dotenv

load_dotenv()

print("--- Environment Diagnosis ---")
print(f"GROQ_API_KEY: {'Present' if os.getenv('GROQ_API_KEY') else 'Missing'}")
print(f"OPENROUTER_API_KEY: {'Present' if os.getenv('OPENROUTER_API_KEY') else 'Missing'}")
print(f"SUPABASE_URL: {'Present' if os.getenv('SUPABASE_URL') else 'Missing'}")
print(f"SUPABASE_KEY: {'Present' if os.getenv('SUPABASE_KEY') else 'Missing'}")
print(f"Checking .env file existence: {'Found' if os.path.exists('.env') else 'Not Found'}")

try:
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        client = create_client(url, key)
        print("Supabase client created successfully.")
        # Try a simple query
        # res = client.table("projects").select("count", count="exact").execute()
        # print(f"Supabase connection test: {res}")
    else:
        print("Skipping Supabase client creation (missing vars).")
except Exception as e:
    print(f"Supabase client creation/test failed: {e}")
