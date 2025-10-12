from fastapi import APIRouter
from services.langgraph_agent import run_legal_ai_agent_async
from services.get_relevant_docs import get_pdfs
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

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
    session_id: Optional[str] = "default"

@router.post("/get_ai_response")
async def get_ai_response(request: GetAIResponseRequest):
    """
    Get AI response with RAG.
    
    Supports:
    - Multi-turn conversations with context
    - Multi-language queries (English, Sinhala, Tamil)
    - Automatic source citation
    - Session-based conversation memory
    """
    query = request.query
    history = request.history
    language = request.language
    session_id = request.session_id or f"session_{hash(query[:20])}"

    # Convert history to proper format
    formatted_history = []
    if history:
        for msg in history:
            if isinstance(msg, dict):
                formatted_history.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

    # Run AI agent
    result = await run_legal_ai_agent_async(
        query=query,
        language=language,
        history=formatted_history,
        session_id=session_id
    )

    # Get PDF files for citations
    files = get_pdfs(query, language, top_k=3)
    
    if not result.get("success"):
        return {
            "error": result.get("error", "No response generated. Please try again."),
            "response": result.get("response", ""),
            "files": []
        }
    
    return {
        "response": result["response"],
        "files": files,
        "citations": result.get("citations", []),
        "session_id": session_id
    }