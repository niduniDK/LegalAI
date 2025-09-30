from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.connection import get_db
from database.models import User, UserActivityLog, ChatSession, ChatHistory, UserPreference
from schemas.auth import (
    MessageResponse, ChatSessionCreate, ChatSessionResponse, ChatSessionWithHistory,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse
)
from pydantic import BaseModel
from services.get_relevant_docs import get_pdfs
from .auth import get_current_user

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    language: str


@router.post("/preferences", response_model=UserPreferenceResponse)
async def create_user_preference(
    preference_data: UserPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user preference."""
    # Check if preference already exists
    existing_pref = db.query(UserPreference).filter(
        UserPreference.user_email == current_user.email,
        UserPreference.preference_key == preference_data.preference_key
    ).first()
    
    print("Existing Preference:", existing_pref)
    
    
    new_pref = UserPreference(
        user_email=current_user.email,
        preference_key=preference_data.preference_key,
        preference_value=preference_data.preference_value
    )
    db.add(new_pref)
    db.commit()
    print("New Preference Created:", new_pref)
    return new_pref


@router.post("/search")
def handle_search(request: SearchRequest):
    query = request.query
    language = request.language
    print(f"\n> SEARCH HANDLER: Processing search query: '{query}'")
    pdf_urls = get_pdfs(query, language)
    print(f"Search Returned {len(pdf_urls)} PDF URLs")
    return pdf_urls