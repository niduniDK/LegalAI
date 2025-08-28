import os
from dotenv import load_dotenv
import google.generativeai as genai
from .query_processor import retrieve_doc

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
gemini_client = genai.GenerativeModel("gemini-2.0-flash")

def generate_response(query: str, history: list = []) -> str:

    print(f"\n> LLM HANDLER: Generating response for query: '{query}'")
    content, filenames = retrieve_doc(query)
    context = "\n".join(list(content))
    
    print(f"\n> Retrieved {len(content)} document chunks from {len(filenames)} unique documents")
    print(f"Total context length: {len(context)} characters")
    
    prompt = (
       f"""
    You are a helpful assistant provides legal information and answers to queries based on the provided context.
    Use the following context to answer the question:
    {context}
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
    

if __name__ == "__main__":
    query = "What are the main objectives of the Jayanthipura association in community welfare and environment?"
    response = generate_response(query)
    print(f"Response: {response}")