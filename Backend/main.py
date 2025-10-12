import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import get_ai_response
from routers import handle_search
from routers import get_recommmendations
from routers import auth
from routers import chat_history
from routers import generate_summary
from config.langsmith_config import configure_langsmith

# Initialize LangSmith tracing
configure_langsmith()

app = FastAPI(
    title="LegalAI API - Powered by LangGraph",
    description="AI-powered legal assistant API with LangGraph state machines, RAG, and LangSmith observability",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_history.router, prefix="/chat-history", tags=["Chat History"])
app.include_router(get_ai_response.router, prefix="/chat", tags=["AI Chat"])
app.include_router(handle_search.router, prefix="/get_docs", tags=["Document Search"])
app.include_router(get_recommmendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(generate_summary.router, prefix="/summary", tags=["Summary Generation"])

@app.get("/")
async def root():
    return {
        "message": "LegalAI API is running",
        "framework": "LangGraph + LangChain",
        "features": [
            "RAG-based legal Q&A",
            "Multi-language support",
            "Document summarization",
            "Personalized recommendations",
            "LangSmith observability"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LegalAI API",
        "langchain": "enabled",
        "langgraph": "enabled"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)