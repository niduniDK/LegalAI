import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import get_ai_response
from routers import handle_search
from routers import get_recommmendations
from routers import auth
from routers import chat_history
from routers import generate_summary
from config.langsmith_config import configure_langsmith
from database.connection import test_connection

# Initialize observability tracing
configure_langsmith()

app = FastAPI(
    title="LegalAI API",
    description="AI-powered legal assistant API for Sri Lankan law with RAG and multi-language support",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Check database connection and system health on startup."""
    print("\n" + "="*60)
    print("🚀 LegalAI API Starting Up")
    print("="*60)
    
    # Test database connection
    print("🔍 Testing database connection...")
    if test_connection():
        print("✅ Database connected successfully!")
    else:
        print("⚠️  WARNING: Database connection failed!")
        print("   The application will start but database operations will fail.")
        print("   Please check your database credentials in .env file.")
    
    # Pre-load retriever and embeddings model
    print("\n📚 Pre-loading document retrieval system...")
    try:
        from services.langchain_retriever import initialize_retriever
        initialize_retriever()
        print("✅ Retriever pre-loaded successfully!")
    except Exception as e:
        print(f"⚠️  WARNING: Failed to pre-load retriever: {e}")
        print("   Retriever will be loaded on first query.")
    
    print("="*60 + "\n")

# Configure CORS - comma-separated allowed origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
)

# Parse origins from comma-separated string
allowed_origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]

print(f"🔒 CORS configured for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        "features": [
            "RAG-based legal Q&A",
            "Multi-language support",
            "Document summarization",
            "Personalized recommendations"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with database and LLM provider status."""
    from database.connection import engine
    from sqlalchemy import text
    from config.llm_config import get_provider_info
    from services.langchain_retriever import get_cache_status
    
    # Check database connection
    db_status = "disconnected"
    db_error = None
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = "error"
        db_error = str(e)[:100]
    
    # Get LLM provider info
    provider_info = get_provider_info()
    
    # Get retriever cache status
    cache_status = get_cache_status()
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "LegalAI API",
        "database": {
            "status": db_status,
            "error": db_error
        },
        "llm": {
            "provider": provider_info["provider"],
            "model": provider_info["model"]
        },
        "retriever": {
            "cached": cache_status["retriever_cached"],
            "embeddings_cached": cache_status["embeddings_cached"],
            "document_sources": cache_status["document_sources"]
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)