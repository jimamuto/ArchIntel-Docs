import sys
import os

# Ensure backend dir is in path
sys.path.append(os.getcwd())

print("Attempting to import main...")
try:
    from main import app
    print("Successfully imported app")
except Exception as e:
    print(f"Failed to import app: {e}")
    import traceback
    traceback.print_exc()
