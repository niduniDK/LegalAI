from fastapi import APIRouter
from services.llm_handler import generate_response
from services.get_relevant_docs import get_pdfs
from pydantic import BaseModel

router = APIRouter()

class GetAIResponseRequest(BaseModel):
    query: str
    history: list = []

@router.post("/get_ai_response")
def get_ai_response(request: GetAIResponseRequest):
    query = request.query
    history = request.history
    response = generate_response(query, history)

    files = get_pdfs(query, top_k=3)
    # print(f"Response: {response}")
    if not response:
        return {"error": "No response generated. Please try again."}
    return {"response": response, "files":files}