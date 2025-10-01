import os
from dotenv import load_dotenv
import google.generativeai as genai
from .query_processor import retrieve_doc

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
gemini_client = genai.GenerativeModel("gemini-2.0-flash")

def generate_response(query: str, language, history: list = []) -> str:

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
    
    prompt = (
       f"""
    You are a helpful assistant specialized in answering questions related to Sri Lankan law. Use the provided context to generate accurate and relevant responses. 
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
    Provide your answer in {language}.
    Question: {query}
    Answer:
"""
    )
    try:
        print(f"\n> Sending prompt to Gemini API")
        response = gemini_client.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            print(f"Generated Response: {response.text}")
            return response.text
        else:
            print(f"No response text generated")
            return "Sorry, something went wrong. Please try again later."
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, something went wrong. Please try again later."
    
