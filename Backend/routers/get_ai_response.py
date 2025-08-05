from fastapi import APIRouter
from services.llm_handler import generate_response
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
    print(f"Response: {response}")
    if not response:
        return {"error": "No response generated. Please try again."}
    return {"response": response}