import pytest
from unittest.mock import patch, MagicMock
import os
from services import llm_service

@patch('services.llm_service.os.getenv')
@patch('services.llm_service._call_groq')
@patch('services.llm_service._call_openrouter')
@patch('services.llm_service._call_gemini')
def test_openrouter_fallback_success(mock_gemini, mock_openrouter, mock_groq, mock_getenv):
    # Setup environment mocks
    def getenv_side_effect(key, default=None):
        if key == "GROQ_API_KEY": return "fake_groq_key"
        if key == "OPENROUTER_API_KEY": return "fake_openrouter_key"
        if key == "GEMINI_API_KEY": return "fake_gemini_key"
        return default
    mock_getenv.side_effect = getenv_side_effect

    # Setup fallback chain behavior
    mock_groq.return_value = "Error: Groq API rate limit reached"
    mock_openrouter.return_value = "OpenRouter Response Content"
    
    # Execution
    result = llm_service.generate_doc("Test Prompt")

    # Verification
    assert result == "OpenRouter Response Content"
    mock_groq.assert_called_once()
    mock_openrouter.assert_called_once()
    mock_gemini.assert_not_called()

@patch('services.llm_service.os.getenv')
@patch('services.llm_service._call_groq')
@patch('services.llm_service._call_openrouter')
@patch('services.llm_service._call_gemini')
def test_openrouter_failure_fallback_to_gemini(mock_gemini, mock_openrouter, mock_groq, mock_getenv):
    # Setup environment mocks
    def getenv_side_effect(key, default=None):
        if key == "GROQ_API_KEY": return "fake_groq_key"
        if key == "OPENROUTER_API_KEY": return "fake_openrouter_key"
        if key == "GEMINI_API_KEY": return "fake_gemini_key"
        return default
    mock_getenv.side_effect = getenv_side_effect

    # Setup fallback chain behavior
    mock_groq.return_value = "Error: Groq API rate limit reached"
    mock_openrouter.return_value = "Error: OpenRouter API returned 500"
    mock_gemini.return_value = "Gemini Response Content"
    
    # Execution
    result = llm_service.generate_doc("Test Prompt")

    # Verification
    assert result == "Gemini Response Content"
    mock_groq.assert_called_once()
    mock_openrouter.assert_called_once()
    mock_gemini.assert_called_once()
