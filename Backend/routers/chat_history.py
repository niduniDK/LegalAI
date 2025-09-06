import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import ChatSession, ChatHistory
from schemas.auth import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionWithHistory,
    ChatHistoryResponse, ChatMessage, MessageResponse
)
from routers.auth import get_current_user
from database.models import User

router = APIRouter(tags=["Chat History"])

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    session_name = session_data.session_name or f"Chat Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    new_session = ChatSession(
        user_email=current_user.email,
        session_name=session_name
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current user."""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_email == current_user.email
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionWithHistory)
async def get_chat_session_with_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session with its message history."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_email == current_user.email
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get chat history for this session
    messages = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at.asc()).all()
    
    # Convert to response format
    session_dict = {
        "id": session.id,
        "session_name": session.session_name,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": messages
    }
    
    return session_dict

@router.post("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
async def add_message_to_session(
    session_id: int,
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a message to a chat session."""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_email == current_user.email
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Create new message
    new_message = ChatHistory(
        session_id=session_id,
        user_email=current_user.email,
        message_role=message.role,
        message_content=message.content,
        message_metadata=json.dumps(message.metadata) if message.metadata else None
    )
    
    db.add(new_message)
    
    # Update session's updated_at timestamp
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    return new_message

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: int,
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a chat session (e.g., rename)."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_email == current_user.email
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    if session_data.session_name:
        session.session_name = session_data.session_name
    
    db.commit()
    db.refresh(session)
    
    return session

@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_email == current_user.email
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Delete all messages in the session (CASCADE should handle this)
    db.query(ChatHistory).filter(ChatHistory.session_id == session_id).delete()
    
    # Delete the session
    db.delete(session)
    db.commit()
    
    return MessageResponse(message="Chat session deleted successfully")

@router.get("/messages/recent", response_model=List[ChatHistoryResponse])
async def get_recent_messages(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent chat messages for the user."""
    messages = db.query(ChatHistory).filter(
        ChatHistory.user_email == current_user.email
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    return messages

@router.delete("/messages/{message_id}", response_model=MessageResponse)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific message."""
    message = db.query(ChatHistory).filter(
        ChatHistory.id == message_id,
        ChatHistory.user_email == current_user.email
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    db.delete(message)
    db.commit()
    
    return MessageResponse(message="Message deleted successfully")

@router.delete("/clear-history", response_model=MessageResponse)
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all chat history for the user."""
    # Delete all messages
    db.query(ChatHistory).filter(ChatHistory.user_email == current_user.email).delete()
    
    # Delete all sessions
    db.query(ChatSession).filter(ChatSession.user_email == current_user.email).delete()
    
    db.commit()
    
    return MessageResponse(message="Chat history cleared successfully")
