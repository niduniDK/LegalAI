"""
LangSmith Configuration for LegalAI Backend

This module handles the configuration and initialization of LangSmith
for tracing and monitoring LangChain/LangGraph operations.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith Configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "legalai-backend")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

def configure_langsmith():
    """
    Configure LangSmith tracing for the application.
    Should be called at application startup.
    """
    if LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
        print(f"✓ LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
        return True
    else:
        print("⚠ LangSmith API key not found. Tracing disabled.")
        return False

def is_langsmith_enabled() -> bool:
    """Check if LangSmith is properly configured."""
    return bool(LANGSMITH_API_KEY)
