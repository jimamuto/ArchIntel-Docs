import os

def fix_env_encoding():
    env_path = 'c:\\archintel\\backend\\.env'
    if not os.path.exists(env_path):
        print(f"File not found: {env_path}")
        return

    try:
        with open(env_path, 'rb') as f:
            content = f.read()
        
        # Check for UTF-16 BOM or null bytes which indicate utf-16
        if b'\x00' in content:
            print("Detected null bytes (likely UTF-16). Fixing...")
            # Decode as utf-16 (or try) if it looks like it, otherwise just filter nulls
            # Simplest approach for "ASCII with nulls" (which is what usually happens with '>>' in PS to an ASCII file)
            # is to just remove null bytes if the original file was ASCII.
            
            # However, if the WHOLE file became UTF-16, we should decode properly.
            # But usually '>>' appends UTF-16 to an ASCII file, creating a mixed mess.
            # Let's try to just filter out null bytes, which usually works for ASCII content.
            fixed_content = content.replace(b'\x00', b'')
            
            with open(env_path, 'wb') as f:
                f.write(fixed_content)
            print("Fixed encoding.")
        else:
            print("No null bytes found. File encoding seems okay.")

    except Exception as e:
        print(f"Error fixing .env: {e}")

if __name__ == "__main__":
    fix_env_encoding()
