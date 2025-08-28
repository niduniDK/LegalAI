import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import get_ai_response
from routers import handle_search
from routers import get_recommmendations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(get_ai_response.router, prefix="/chat")
app.include_router(handle_search.router, prefix="/get_docs")
app.include_router(get_recommmendations.router, prefix="/recommendations")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)