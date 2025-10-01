from fastapi import APIRouter
from services.llm_handler import generate_response
from services.get_relevant_docs import get_pdfs
from services.translator import translate
from pydantic import BaseModel
from typing import List, Optional, Any

router = APIRouter()

class MessageModel(BaseModel):
    id: str
    content: str
    role: str
    timestamp: Optional[str] = None

class GetAIResponseRequest(BaseModel):
    query: str
    history: List[Any] = []  # Changed to allow any structure for backward compatibility
    language: str = "en"

@router.post("/get_ai_response")
def get_ai_response(request: GetAIResponseRequest):
    query = request.query
    history = request.history
    language = request.language

    if language != "en":
        print(f"Translating query from {language} to English")
        query = translate(query, src_language=language, target_language="en")
        print(f"Translated query: {query}")

    response = generate_response(query, language, history)


    files = get_pdfs(query, language,top_k=3)
    # print(f"Response: {response}")
    if not response:
        return {"error": "No response generated. Please try again."}
    return {"response": response, "files":files}