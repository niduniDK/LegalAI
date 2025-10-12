import pandas as pd
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv

from services.langgraph_summary_agent import (
    generate_document_summary as langgraph_summary,
    generate_document_highlights as langgraph_highlights
)
from services.get_doc_chunks import get_doc_chunks

from database.connection import get_db
from database.models import ChatSession, ChatHistory, User
from routers.auth import get_current_user

load_dotenv()

router = APIRouter()

class FileNameRequest(BaseModel):
    file_name: str

class SummaryRequest(BaseModel):
    file_name: str
    language: str = "en"

@router.post("/summary")
def get_summary(file: FileNameRequest):
    """
    Get or generate document summary using LangGraph agent.
    First checks CSV cache, then generates using AI if not found.
    """
    file_name = file.file_name.replace(".pdf", ".txt").replace("/", "-")
    print(f"Getting summary for file: {file_name}")
    
    try:
        # Check if summary.csv exists
        csv_path = "docs/summary.csv"
        if os.path.exists(csv_path):
            summary_df = pd.read_csv(csv_path)
            print(f"Loaded CSV with {len(summary_df)} rows")
            
            # Look for the file in the CSV
            matching_rows = summary_df[summary_df['name'] == file_name]
            
            if len(matching_rows) > 0:
                summary_text = matching_rows['summary'].iloc[0]
                
                if pd.notna(summary_text):
                    print(f"Found summary for {file_name} in cache")
                    return {"summary": str(summary_text), "status": "success", "source": "cache"}
        
        # If not in cache, generate using LangGraph
        print(f"Generating summary using LangGraph agent")
        file_type = "unknown"
        if "bill" in file_name.lower():
            file_type = "bill"
        elif "act" in file_name.lower():
            file_type = "act"
        elif "gazette" in file_name.lower():
            file_type = "gazette"
        
        result = langgraph_summary(file_name, file_type, "en")
        
        return {
            "summary": result["summary"],
            "status": "success" if result["success"] else "generated_with_errors",
            "source": "langgraph"
        }
        
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        default_summary = "This is an official legal document from the Sri Lankan government portal containing important regulatory information."
        return {"summary": default_summary, "status": "error", "message": str(e)}

@router.post("/highlights")
def get_highlights(file: FileNameRequest):
    """
    Get or generate document highlights using LangGraph agent.
    First checks CSV cache, then generates using AI if not found.
    """
    file_name = file.file_name.replace(".pdf", ".txt").replace("/", "-")
    print(f"Getting highlights for file: {file_name}")
    
    try:
        # Check if summary.csv exists
        csv_path = "docs/summary.csv"
        if os.path.exists(csv_path):
            summary = pd.read_csv(csv_path)
            print(f"Loaded CSV with {len(summary)} rows")
            
            # Look for the file in the CSV
            matching_rows = summary[summary['name'] == file_name]
            
            if len(matching_rows) > 0:
                summary_text = matching_rows['summary'].iloc[0]
                
                if pd.notna(summary_text):
                    # Split summary into key highlights
                    highlights = [h.strip() for h in str(summary_text).split('.') if h.strip()]
                    print(f"Found {len(highlights)} highlights for {file_name} in cache")
                    return {"highlights": highlights[:7], "status": "success", "source": "cache"}
        
        # If not in cache, generate using LangGraph
        print(f"Generating highlights using LangGraph agent")
        file_type = "unknown"
        if "bill" in file_name.lower():
            file_type = "bill"
        elif "act" in file_name.lower():
            file_type = "act"
        elif "gazette" in file_name.lower():
            file_type = "gazette"
        
        result = langgraph_highlights(file_name, file_type, "en")
        
        return {
            "highlights": result["highlights"],
            "status": "success" if result["success"] else "generated_with_errors",
            "source": "langgraph"
        }
        
    except Exception as e:
        print(f"Error retrieving highlights: {e}")
        default_highlights = [
            "This document contains key legal provisions",
            "It includes important regulatory information",
            "The document may contain statutory requirements"
        ]
        return {"highlights": default_highlights, "status": "error", "message": str(e)}

@router.post("/generate")
def generate_document_summary(
    request: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive summary of a document using LangGraph and save as chat session.
    """
    try:
        file_name = request.file_name.replace(".pdf", ".txt").replace("/", "-")
        
        # Determine file type
        file_type = "unknown"
        if "bill" in file_name.lower():
            file_type = "bill"
        elif "act" in file_name.lower():
            file_type = "act"
        elif "gazette" in file_name.lower():
            file_type = "gazette"
        
        # Generate summary using LangGraph
        result = langgraph_summary(file_name, file_type, request.language)
        summary = result["summary"]
        
        # Generate highlights
        highlights_result = langgraph_highlights(file_name, file_type, request.language)
        highlights = highlights_result.get("highlights", [])
        
        # Create a new chat session for this document summary
        session_name = f"Document Summary: {request.file_name}"
        new_session = ChatSession(
            user_email=current_user.email,
            session_name=session_name
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        # Add the user's initial query (implicit)
        user_message = ChatHistory(
            session_id=new_session.id,
            user_email=current_user.email,
            message_role="user",
            message_content="Give a summary on this document",
            message_metadata=json.dumps({
                "document_filename": request.file_name,
                "request_type": "summary",
                "language": request.language,
                "agent": "langgraph"
            })
        )
        
        db.add(user_message)
        
        # Add the AI's summary response
        ai_message = ChatHistory(
            session_id=new_session.id,
            user_email=current_user.email,
            message_role="assistant",
            message_content=summary,
            message_metadata=json.dumps({
                "document_filename": request.file_name,
                "highlights_count": len(highlights),
                "language": request.language,
                "response_type": "document_summary",
                "agent": "langgraph"
            })
        )
        
        db.add(ai_message)
        
        # Update session's updated_at timestamp
        new_session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ai_message)
        
        return {
            "summary": summary,
            "highlights": highlights,
            "filename": request.file_name,
            "language": request.language,
            "status": "success",
            "session_id": new_session.id,
            "session_name": session_name
        }
        
    except Exception as e:
        print(f"Error generating document summary: {e}")
        return {
            "summary": "Sorry, I encountered an error while generating the document summary. Please try again.",
            "highlights": [],
            "filename": request.file_name,
            "language": request.language,
            "status": "error",
            "error": str(e),
            "session_id": None,
            "session_name": None
        }