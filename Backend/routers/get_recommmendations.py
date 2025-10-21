from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.langgraph_recommendations_agent import generate_recommendations
from services.get_relevant_docs import get_pdfs

router = APIRouter()

class Recommendation(BaseModel):
    username: str
    preferences: list[str] = []
    language: str

@router.post("/get_recommendations")
def get_recommendations_endpoint(request: Recommendation):
    """
    Get personalized document recommendations.
    
    This endpoint:
    1. Analyzes user preferences and query history
    2. Generates an intelligent search query
    3. Retrieves relevant legal documents
    4. Returns ranked recommendations
    """
    username = request.username
    preferences = request.preferences
    language = request.language

    print(f"\n> GET_RECOMMENDATIONS: Processing for user: {username}")
    print(f"> Preferences: {preferences}")

    # TODO: Retrieve actual user history from database
    # For now, using preferences as proxy for history
    history = preferences if preferences else []

    # Generate recommendations
    result = generate_recommendations(
        username=username,
        preferences=preferences,
        history=history,
        language=language
    )

    if not result.get("success"):
        return {
            "recommendations": [],
            "message": "Unable to generate recommendations at this time.",
            "error": result.get("error", "Unknown error")
        }

    # Convert recommendations to PDF URLs
    pdf_urls = []
    for rec in result["recommendations"]:
        filename = rec.get("filename", "")
        if filename:
            # Extract document info from filename
            name_split = filename.split('.')[0]
            try:
                name = name_split[:-7].replace("-", "/")
                year = name_split[-7:-2]
                lang = name_split[-1]

                if language == "en":
                    lang = "E"
                elif language == "si":
                    lang = "S"
                elif language == "ta":
                    lang = "T"

                url = f"https://documents.gov.lk/view/{name}{year}_{lang}.pdf"
                pdf_urls.append({
                    "url": url,
                    "filename": filename,
                    "type": rec.get("type", "document"),
                    "preview": rec.get("preview", "")
                })
            except Exception as e:
                print(f"Error generating URL for {filename}: {e}")
                continue

    print(f"> Generated {len(pdf_urls)} recommendation URLs")
    
    return {
        "recommendations": pdf_urls,
        "search_query": result.get("search_query", ""),
        "count": len(pdf_urls)
    }
