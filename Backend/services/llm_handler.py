import os
from dotenv import load_dotenv
import google.generativeai as genai
from .query_processor import process_query

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
gemini_client = genai.GenerativeModel("gemini-2.0-flash")

def generate_response(query: str, history: list = []) -> str:

    content = process_query(query)
    context = "\n".join(list(content))
    
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
        response = gemini_client.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            print(f"Generated response: {response.text}")
            return response.text
        else:
            return "Sorry, something went wrong. Please try again later."
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, something went wrong. Please try again later."
    

if __name__ == "__main__":
    query = "What are the main objectives of the Jayanthipura association in community welfare and environment?"
    response = generate_response(query)
    print(f"Response: {response}")