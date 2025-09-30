from fastapi import APIRouter
from services.llm_handler import generate_response
from services.get_relevant_docs import get_pdfs
from services.translator import translate
from pydantic import BaseModel

router = APIRouter()

class GetAIResponseRequest(BaseModel):
    query: str
    history: list = []
    language: str

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