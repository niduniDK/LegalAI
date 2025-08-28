from fastapi import APIRouter
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from services.get_relevant_docs import get_pdfs

load_dotenv()

router = APIRouter()

class Recommendation(BaseModel):
    username: str

history_db = {
    "user_1": [
        "How is the composition of Municipal Councils determined according to the amendments?",
        "How does the Act amend the composition of Urban Councils?",
        "What happens if a Pradeshiya Sabha fails to pass a budget within two weeks?"
    ],
    "user_2" : [
        "What is the effect if an Urban Council fails to pass its budget within the given timeframe?",
        "In case of inconsistency between Sinhala and Tamil texts of the Act, which version prevails?",
        "What departments or authorities are responsible for the publication and implementation of this Act?"
    ]
}

GROQ_API_KEY = os.getenv("groq_api_key")
GROQ_MODEL = 'llama-3.3-70b-versatile'

def query_llama(prompt: str) -> str:
    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers = {
            'Authorization': f"Bearer {GROQ_API_KEY}",
            'Content-type': 'application/json'
        },
        json={
            'model': GROQ_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature':0.0
        }
    )

    if response.ok:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Error in API request"


def detect_user_interest(user_id):
    history = history_db[user_id]
    prompt = f"""
        You are an intelligent agent in classifying user interests based on the user query history. User history is given below to identify the user_interests.
        history: {history}
        user_interests:
    
        For example,
       1) history: [
            "What is the effect if an Urban Council fails to pass its budget within the given timeframe?",
            "In case of inconsistency between Sinhala and Tamil texts of the Act, which version prevails?",
            "What departments or authorities are responsible for the publication and implementation of this Act?"
        ]
        user_interests: [
            "Local government law",
            "Administrative procedures",
            "Statutory regulations",
            "Legal governance",
            "Law interpretation and compliance"
        ]
    
        2) history: [
            "What is the effect if an Urban Council fails to pass its budget within the given timeframe?",
            "In case of inconsistency between Sinhala and Tamil texts of the Act, which version prevails?",
            "What departments or authorities are responsible for the publication and implementation of this Act?"
        ]
        user_interests: [
            "Local government law",
            "Administrative procedures",
            "Statutory regulations",
            "Legal governance",
            "Law interpretation and compliance"
        ]

        3)history: [
            "What are the penalties for cybercrime under the Computer Crimes Act?",
            "How is evidence collected and presented in a criminal trial?",
            "What rights does a suspect have during police interrogation?"
        ]
        user_interests: [
            "Criminal law",
            "Cybercrime regulations",
            "Legal procedures",
            "Rights of suspects",
            "Law enforcement practices"
        ]
        
        4) history: [
            "What are the obligations of directors under the Companies Act?",
            "How are shareholder disputes resolved in Sri Lanka?",
            "What is the process for registering a new business entity?"
        ]
        user_interests: [
            "Corporate law",
            "Commercial regulations",
            "Company governance",
            "Shareholder rights",
            "Business registration procedures"
        ]

        5) history: [
            "Which authority has the power to amend the Constitution?",
            "How are conflicts between central and provincial governments resolved?",
            "What legal remedies exist against administrative decisions?"
        ]
        user_interests: [
            "Constitutional law",
            "Administrative law",
            "Separation of powers",
            "Government authority",
            "Legal remedies and appeals"
        ]
    
        6) history: [
            "How do I register a trademark in Sri Lanka?",
            "What protections are available under copyright law?",
            "What are the penalties for patent infringement?"
        ]
        user_interests: [
            "Intellectual property law",
            "Trademark and copyright regulations",
            "Patent law",
            "Legal protections for creations",
            "Enforcement of IP rights"
        ]
     provide only the user_interests as a list without adding any starting or ending text
    """
    response = query_llama(prompt)
    print(f"LLama response: {response}")
    return response

@router.post("/get_recommendations")
def get_recommendations(user: Recommendation):
    user_id = user.username

    print(f"Fetching recommendations for user: {user_id}")

    if user_id not in history_db:
        return {"error": "User not found"}
    
    user_interests = detect_user_interest(user_id)
    print(f"Detected user interests: {user_interests}")

    recommended_docs = get_pdfs(user_interests, top_k=5)
    print(f"Generated {len(recommended_docs)} recommendations for user {user_id}")
    print(f"Recommended document URLs: {recommended_docs}")

    return recommended_docs