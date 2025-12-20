import os
from dotenv import load_dotenv
load_dotenv(override=True)

import sys
sys.path.append(os.path.dirname(__file__))

from services.llm_service import _call_groq, _call_gemini

# Open output file
output_file = open("llm_test_results.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    output_file.write(msg + "\n")

log("=" * 70)
log("TESTING LLM PROVIDERS FOR ARCHINTEL")
log("=" * 70)

# Check environment
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

log("\n1. Environment Variables:")
log(f"   GROQ_API_KEY: {'✓ Found (' + groq_key[:20] + '...)' if groq_key else '✗ Missing'}")
log(f"   GEMINI_API_KEY: {'✓ Found (' + gemini_key[:20] + '...)' if gemini_key else '✗ Missing'}")

test_prompt = "Explain what a REST API is in exactly one sentence."

# Test Groq
if groq_key:
    log("\n2. Testing Groq (llama-3.3-70b-versatile):")
    log("-" * 70)
    try:
        response = _call_groq(test_prompt, groq_key)
        if "Groq Error" in response or "Error" in response:
            log(f"❌ FAILED:\n{response}")
        else:
            log(f"✅ SUCCESS:\n{response}")
    except Exception as e:
        log(f"❌ EXCEPTION: {e}")
else:
    log("\n2. Groq: SKIPPED (no API key)")

# Test Gemini
if gemini_key:
    log("\n3. Testing Gemini (gemini-1.5-flash):")
    log("-" * 70)
    try:
        response = _call_gemini(test_prompt, gemini_key)
        if "Gemini Error" in response or "Error" in response:
            log(f"❌ FAILED:\n{response}")
        else:
            log(f"✅ SUCCESS:\n{response}")
    except Exception as e:
        log(f"❌ EXCEPTION: {e}")
else:
    log("\n3. Gemini: SKIPPED (no API key)")

log("\n" + "=" * 70)
log("TEST COMPLETED - Results saved to llm_test_results.txt")
log("=" * 70)

output_file.close()
