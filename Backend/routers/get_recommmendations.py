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
    prefrerences: list[str] = []
    language: str

# history_db = {
#     "user_1": [
#         "How is the composition of Municipal Councils determined according to the amendments?",
#         "How does the Act amend the composition of Urban Councils?",
#         "What happens if a Pradeshiya Sabha fails to pass a budget within two weeks?"
#     ],
#     "user_2" : [
#         "What is the effect if an Urban Council fails to pass its budget within the given timeframe?",
#         "In case of inconsistency between Sinhala and Tamil texts of the Act, which version prevails?",
#         "What departments or authorities are responsible for the publication and implementation of this Act?"
#     ]
# }

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


def generate_search_query(history):
    prompt = f"""
        You are an intelligent agent for generating document search queries based on user query history. Based on the user's chat history, create a comprehensive search query that incorporates the user's interests and can retrieve relevant legal documents.
        
        history: {history}
        query:
    
        For example,
       1) history: [
            "What is the effect if an Urban Council fails to pass its budget within the given timeframe?",
            "In case of inconsistency between Sinhala and Tamil texts of the Act, which version prevails?",
            "What departments or authorities are responsible for the publication and implementation of this Act?"
        ]
        query: "Find legal documents related to local government law, administrative procedures, statutory regulations, legal governance, and law interpretation compliance for Urban Councils and municipal administration"
    
        2) history: [
            "What are the penalties for cybercrime under the Computer Crimes Act?",
            "How is evidence collected and presented in a criminal trial?",
            "What rights does a suspect have during police interrogation?"
        ]
        query: "Retrieve documents on criminal law, cybercrime regulations, legal procedures, rights of suspects, and law enforcement practices in Sri Lanka"

        3) history: [
            "What are the obligations of directors under the Companies Act?",
            "How are shareholder disputes resolved in Sri Lanka?",
            "What is the process for registering a new business entity?"
        ]
        query: "Search for corporate law documents covering commercial regulations, company governance, shareholder rights, and business registration procedures"
        
        4) history: [
            "Which authority has the power to amend the Constitution?",
            "How are conflicts between central and provincial governments resolved?",
            "What legal remedies exist against administrative decisions?"
        ]
        query: "Find constitutional law and administrative law documents on separation of powers, government authority, and legal remedies and appeals processes"

        5) history: [
            "How do I register a trademark in Sri Lanka?",
            "What protections are available under copyright law?",
            "What are the penalties for patent infringement?"
        ]
        query: "Retrieve intellectual property law documents including trademark and copyright regulations, patent law, legal protections for creations, and enforcement of IP rights"
    
        6) history: [
            "What is the procedure for filing a divorce petition?",
            "How is child custody determined in family disputes?",
            "What are the grounds for alimony in Sri Lanka?"
        ]
        query: "Search for family law documents covering divorce procedures, child custody regulations, matrimonial law, and spousal support requirements"
     provide only the search query as a single comprehensive string without adding any starting or ending text
    """
    response = query_llama(prompt)
    print(f"LLama response: {response}")
    return response

@router.post("/get_recommendations")
def get_recommendations(user: Recommendation):
    user_id = user.username
    history = user.prefrerences
    language = user.language

    print(f"Fetching recommendations for user: {user_id}")

    search_query = generate_search_query(history)
    print(f"Generated search query: {search_query}")

    recommended_docs = get_pdfs(search_query, language, top_k=5)
    print(f"Generated {len(recommended_docs)} recommendations for user {user_id}")
    print(f"Recommended document URLs: {recommended_docs}")

    return recommended_docs