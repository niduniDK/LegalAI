from fastapi import APIRouter
from pydantic import BaseModel
from services.get_relevant_docs import get_pdfs

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/search")
def handle_search(request: SearchRequest):
    query = request.query
    print(f"\n> SEARCH HANDLER: Processing search query: '{query}'")
    pdf_urls = get_pdfs(query)
    print(f"Search Returned {len(pdf_urls)} PDF URLs")
    return pdf_urls