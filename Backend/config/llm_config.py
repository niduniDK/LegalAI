"""
LLM Configuration Module

Centralized configuration for LLM providers (Gemini and OpenAI).
Provides factory functions to create LLM instances based on environment variables.
"""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# LLM Provider Configuration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()
LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def get_langchain_llm(temperature: float = 0.3, **kwargs):
    """
    Factory function to create a LangChain LLM instance based on configuration.
    
    Args:
        temperature: Temperature for response generation (0.0-1.0)
        **kwargs: Additional provider-specific parameters
        
    Returns:
        LangChain LLM instance (ChatGoogleGenerativeAI or ChatOpenAI)
        
    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    if LLM_PROVIDER == 'gemini':
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
            convert_system_message_to_human=True,
            **kwargs
        )
    
    elif LLM_PROVIDER == 'openai':
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            model=LLM_MODEL,
            openai_api_key=OPENAI_API_KEY,
            temperature=temperature,
            **kwargs
        )
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {LLM_PROVIDER}. "
            f"Supported providers: gemini, openai"
        )


def get_generative_client():
    """
    Factory function to create a generative client for direct API calls.
    Used in llm_handler.py for non-LangChain interactions.
    
    Returns:
        Generative client instance
        
    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    if LLM_PROVIDER == 'gemini':
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel(LLM_MODEL)
    
    elif LLM_PROVIDER == 'openai':
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {LLM_PROVIDER}. "
            f"Supported providers: gemini, openai"
        )


def generate_content(client, prompt: str, temperature: Optional[float] = None) -> str:
    """
    Generate content using the specified client.
    Abstracts away provider-specific API differences.
    
    Args:
        client: LLM client (from get_generative_client)
        prompt: Text prompt
        temperature: Optional temperature override
        
    Returns:
        Generated text response
    """
    if LLM_PROVIDER == 'gemini':
        response = client.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text
        else:
            return "Sorry, something went wrong. Please try again later."
    
    elif LLM_PROVIDER == 'openai':
        messages = [{"role": "user", "content": prompt}]
        kwargs = {"model": LLM_MODEL, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature
        
        response = client.chat.completions.create(**kwargs)
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            return "Sorry, something went wrong. Please try again later."
    
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")


def get_provider_info() -> dict:
    """
    Get information about the current LLM provider configuration.
    
    Returns:
        Dictionary with provider, model, and availability info
    """
    return {
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "gemini_available": bool(GEMINI_API_KEY),
        "openai_available": bool(OPENAI_API_KEY)
    }
