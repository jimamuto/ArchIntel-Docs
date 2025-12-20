from services.llm_service import generate_doc

def generate_doc_with_groq(prompt: str) -> str:
    """
    Legacy wrapper for backward compatibility.
    Now defaults to the unified LLM service.
    """
    return generate_doc(prompt)
