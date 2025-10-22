import os
import requests
from dotenv import load_dotenv
from config.llm_config import get_generative_client, generate_content, get_provider_info
from .query_processor import retrieve_doc

load_dotenv()

# Get LLM client based on configuration
llm_client = get_generative_client()
provider_info = get_provider_info()
print(f"🤖 Using LLM Provider: {provider_info['provider']} ({provider_info['model']})")

# Hugging Face configuration
HF_API_TOKEN = os.getenv('HF_API_TOKEN')
HF_ENDPOINT_URL = os.getenv('HF_ENDPOINT_URL')  # Your endpoint URL
MODEL_TYPE = os.getenv('MODEL_TYPE', 'gemini')  # 'gemini' or 'huggingface'

def generate_response_hf(query: str, history: list = []) -> str:
    """Generate response using Hugging Face endpoint"""
    content, filenames = retrieve_doc(query)
    context = "\n".join(list(content))
    
    print(f"\n> Retrieved {len(content)} document chunks from {len(filenames)} unique documents")
    print(f"Total context length: {len(context)} characters")
    
    # Format history for prompt
    formatted_history = ""
    if history:
        formatted_history = "\n".join([
            f"{msg.get('role', 'user').title()}: {msg.get('content', '')}" 
            for msg in history if msg.get('content')
        ])
    
    prompt = (f"""You are a helpful assistant specialized in answering questions related to Sri Lankan law. Use the provided context to generate accurate and relevant responses. 
If the context does not contain sufficient information, refine the query to better match available documents and use refined query as the query in {retrieve_doc(query)} and get relevant content. 
Provide clear and concise answers based on the context but do not fabricate information and your response should be easy to understand by laymans. If users ask for legal advice, recommend consulting a qualified legal professional.
If the user asks more professional or technical questions, provide answers in a professional tone with more domain specifically.
If the context is not useful, generate a response by doing a web-search on Sri Lankan law and link the sources you used.
If you cannot find an answer, Use Sri Lankan constitution as the primary source of law and refer to it in your answer https://www.parliament.lk/files/pdf/constitution.pdf. 
Always end your response with a friendly question to keep the conversation going.
Use the following pieces of context to answer the question at the end. If you use any piece of context, cite it using [filename] after the sentence where it is used. If multiple pieces of context support your answer, cite all relevant filenames.
{context}
Use the following conversation history as reference to maintain context and continuity in the conversation:
{formatted_history}
Question: {query}
Answer:""")

#     prompt = f"""You are a helpful assistant that provides legal information and answers to queries based on the provided context.
# Use the following context to answer the question:
# {context}
# Question: {query}
# Answer:"""
    
    # Since endpoint is public, no authorization needed
    headers = {
        "Content-Type": "application/json"
    }
    
    # Use OpenAI-compatible chat completions format for vLLM
    payload = {
        "model": "Nishan726/gemma-3-finetune3",  # Your model name
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        print(f"\n> Sending request to Hugging Face endpoint (OpenAI format)")
        # Use OpenAI-compatible endpoint
        openai_endpoint = f"{HF_ENDPOINT_URL}/v1/chat/completions"
        response = requests.post(openai_endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            answer = result['choices'][0]['message']['content'].strip()
            print(f"Generated Response: {answer}")
            return answer
        else:
            print(f"Unexpected response format: {result}")
            return "Sorry, something went wrong. Please try again later."
            
    except Exception as e:
        print(f"Error generating response from HF endpoint: {e}")
        return "Sorry, something went wrong. Please try again later."


def generate_response_gemini(query: str, history: list = []) -> str:

    print(f"\n> LLM HANDLER: Generating response for query: '{query}'")
    content, filenames = retrieve_doc(query)
    context = "\n".join(list(content))
    
    print(f"\n> Retrieved {len(content)} document chunks from {len(filenames)} unique documents")
    print(f"Total context length: {len(context)} characters")
    
    # Format history for prompt
    formatted_history = ""
    if history:
        formatted_history = "\n".join([
            f"{msg.get('role', 'user').title()}: {msg.get('content', '')}" 
            for msg in history if msg.get('content')
        ])

    prompt = (f"""You are a helpful assistant specialized in answering questions related to Sri Lankan law. Use the provided context to generate accurate and relevant responses. 
If the context does not contain sufficient information, refine the query to better match available documents and use refined query as the query in {retrieve_doc(query)} and get relevant content. 
Provide clear and concise answers based on the context but do not fabricate information and your response should be easy to understand by laymans. If users ask for legal advice, recommend consulting a qualified legal professional.
If the user asks more professional or technical questions, provide answers in a professional tone with more domain specifically.
If the context is not useful, generate a response by doing a web-search on Sri Lankan law and link the sources you used.
If you cannot find an answer, Use Sri Lankan constitution as the primary source of law and refer to it in your answer https://www.parliament.lk/files/pdf/constitution.pdf. 
Always end your response with a friendly question to keep the conversation going.
Use the following pieces of context to answer the question at the end. If you use any piece of context, cite it using [filename] after the sentence where it is used. If multiple pieces of context support your answer, cite all relevant filenames.
{context}
Use the following conversation history as reference to maintain context and continuity in the conversation:
{formatted_history}
Question: {query}
Answer:""")
    
    try:
        print(f"\n> Sending prompt to {provider_info['provider']} API")
        response_text = generate_content(llm_client, prompt)
        print(f"Generated Response: {response_text}")
        return response_text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, something went wrong. Please try again later."

def generate_response(query: str, history: list = []) -> str:
    """Main function to generate response using configured model"""
    print(f"\n> LLM HANDLER: Generating response for query: '{query}' using {MODEL_TYPE}")
    
    if MODEL_TYPE == 'huggingface':
        return generate_response_hf(query)
    else:
        return generate_response_gemini(query)

# def generate_response(query: str, language, history: list = []) -> str:

#     print(f"\n> LLM HANDLER: Generating response for query: '{query}'")
#     content, filenames = retrieve_doc(query)
#     context = "\n".join(list(content))
    
#     print(f"\n> Retrieved {len(content)} document chunks from {len(filenames)} unique documents")
#     print(f"Total context length: {len(context)} characters")
    
#     # Format history for prompt
#     formatted_history = ""
#     if history:
#         formatted_history = "\n".join([
#             f"{msg.get('role', 'user').title()}: {msg.get('content', '')}" 
#             for msg in history if msg.get('content')
#         ])
    
#     prompt = (
#        f"""
#     You are a helpful assistant specialized in answering questions related to Sri Lankan law. Use the provided context to generate accurate and relevant responses. 
#     If the context does not contain sufficient information, refine the query to better match available documents and use refined query as the query in {retrieve_doc(query)} and get relevant content. 
#     Provide clear and concise answers based on the context but do not fabricate information and your response should be easy to understand by laymans. If users ask for legal advice, recommend consulting a qualified legal professional.
#     If the user asks more professional or technical questions, provide answers in a professional tone with more domain specifically.
#     If the context is not useful, generate a response by doing a web-search on Sri Lankan law and link the sources you used.
#     If you cannot find an answer, Use Sri Lankan constitution as the primary source of law and refer to it in your answer https://www.parliament.lk/files/pdf/constitution.pdf. 
#     Always end your response with a friendly question to keep the conversation going.
#     Use the following pieces of context to answer the question at the end. If you use any piece of context, cite it using [filename] after the sentence where it is used. If multiple pieces of context support your answer, cite all relevant filenames.
#     {context}
#     Use the following conversation history as reference to maintain context and continuity in the conversation:
#     {formatted_history}
#     Provide your answer in {language}.
#     Question: {query}
#     Answer:
# """
#     )
#     try:
#         print(f"\n> Sending prompt to Gemini API")
#         response = gemini_client.generate_content(prompt)
#         if hasattr(response, "text") and response.text:
#             print(f"Generated Response: {response.text}")
#             return response.text
#         else:
#             print(f"No response text generated")
#             return "Sorry, something went wrong. Please try again later."
#     except Exception as e:
#         print(f"Error generating response: {e}")
#         return "Sorry, something went wrong. Please try again later."
    
