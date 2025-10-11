import pandas as pd
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from services.get_doc_chunks import get_doc_chunks

from database.connection import get_db
from database.models import ChatSession, ChatHistory, User
from routers.auth import get_current_user

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
gemini_client = genai.GenerativeModel("gemini-2.0-flash")

router = APIRouter()

class FileNameRequest(BaseModel):
    file_name: str

class SummaryRequest(BaseModel):
    file_name: str
    language: str = "en"

@router.post("/summary")
def get_summary(file: FileNameRequest):
    file_name = file.file_name.replace(".pdf", ".txt").replace("/", "-")
    print(f"Getting summary for file: {file_name}")
    
    try:
        # Check if summary.csv exists
        csv_path = "docs/summary.csv"
        if not os.path.exists(csv_path):
            print(f"Summary CSV not found at {csv_path}")
            # Return default summary
            default_summary = "This is an official legal document from the Sri Lankan government portal containing important regulatory information and procedural guidelines."
            return {"summary": default_summary, "status": "default", "message": "Using default summary"}
            
        summary_df = pd.read_csv(csv_path)
        print(f"Loaded CSV with {len(summary_df)} rows")
        
        # Look for the file in the CSV
        matching_rows = summary_df[summary_df['name'] == file_name]
        
        if len(matching_rows) > 0:
            summary_text = matching_rows['summary'].iloc[0]
            
            if pd.notna(summary_text):
                print(f"Found summary for {file_name}")
                return {"summary": str(summary_text), "status": "success"}
        
        # If no specific summary found, return default
        print(f"No summary found for file: {file_name}")
        default_summary = "This is an official legal document from the Sri Lankan government portal containing important regulatory information and procedural guidelines."
        return {"summary": default_summary, "status": "default", "message": "No specific summary found"}
        
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        # Return default summary on error
        default_summary = "This document contains important legal information."
        return {"summary": default_summary, "status": "error", "message": str(e)}

@router.post("/highlights")
def get_highlights(file: FileNameRequest):
    file_name = file.file_name.replace(".pdf", ".txt").replace("/", "-")
    print(f"Getting highlights for file: {file_name}")
    
    try:
        # Check if summary.csv exists
        csv_path = "docs/summary.csv"
        if not os.path.exists(csv_path):
            print(f"Summary CSV not found at {csv_path}")
            # Return default highlights
            default_highlights = [
                "This document contains key legal provisions enacted by the Parliament of Sri Lanka",
                "It includes important regulatory information and procedural guidelines",
                "The document may contain statutory requirements and compliance measures"
            ]
            return {"highlights": default_highlights, "status": "default", "message": "Using default highlights"}
            
        summary = pd.read_csv(csv_path)
        print(f"Loaded CSV with {len(summary)} rows")
        
        # Look for the file in the CSV
        matching_rows = summary[summary['name'] == file_name]
        
        if len(matching_rows) > 0:
            summary_text = matching_rows['summary'].iloc[0]
            file_type = matching_rows['type'].iloc[0]

            try:
                content = get_doc_chunks(file_name, file_type)
                if content:
                    print(f"Retrieved {len(content)} content chunks")
                    # Only show first few chunks to avoid too much output
                    if len(content) > 3:
                        print(f"Content preview: {content[:3]}...")
                    else:
                        print(f"Content: {content}")
                else:
                    print("No content retrieved from get_doc_chunks")
                    content = []
            except Exception as e:
                print(f"Error getting document chunks: {e}")
                content = []

            if pd.notna(summary_text):
                # Split summary into key highlights
                highlights = [h.strip() for h in str(summary_text).split('.') if h.strip()]
                
                # Add content chunks if available, but limit the number
                if content:
                    # Limit content to first 5 chunks and truncate each to 200 chars
                    limited_content = []
                    for chunk in content[:5]:
                        if isinstance(chunk, str) and chunk.strip():
                            truncated = chunk.strip()[:200]
                            if len(chunk.strip()) > 200:
                                truncated += "..."
                            limited_content.append(truncated)
                    highlights.extend(limited_content)

                print(f"Found {len(highlights)} highlights for {file_name}")
                return {"highlights": highlights, "status": "success"}
        
        # If no specific summary found, return default
        print(f"No summary found for file: {file_name}")
        default_highlights = [
            "This document contains key legal provisions enacted by the Parliament of Sri Lanka",
            "It includes important regulatory information and procedural guidelines",
            "The document may contain statutory requirements and compliance measures"
        ]
        return {"highlights": default_highlights, "status": "default", "message": "No specific summary found"}
        
    except Exception as e:
        print(f"Error retrieving highlights: {e}")
        # Return default highlights on error
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
    Generate a comprehensive summary of a document using LLM and save as chat session
    """
    try:
        # First get highlights
        highlights_data = get_highlights(FileNameRequest(file_name=request.file_name))
        highlights = highlights_data.get("highlights", [])

        print(highlights)
        
        # Create a summary query for the LLM with language support
        language_instruction = ""
        if request.language == "si":
            language_instruction = "Please respond in Sinhala (සිංහල)."
        elif request.language == "ta":
            language_instruction = "Please respond in Tamil (தமிழ்)."
        else:
            language_instruction = "Please respond in English."
            
        prompt = f"""{language_instruction}
        
        Generate a comprehensive summary of the document '{request.file_name}' based on the following key highlights:
        
        {' '.join(highlights)}
        
        Please provide:
        1. A brief overview of the document's purpose
        2. Key legal provisions and requirements
        3. Important procedural information
        4. Compliance or regulatory aspects
        5. Any significant implications for citizens or businesses
        
        Format the response in a clear, structured manner that's easy to understand. No need of saying that you are unable to access the 
        external documents, including the PDF you provided, "2023/8/10-2023_E.pdf." Therefore, you cannot provide a comprehensive summary 
        based on its content."""
        
        response = gemini_client.generate_content(prompt)
        summary = response.text if hasattr(response, "text") and response.text else "Sorry, something went wrong. Please try again later."
        
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
                "language": request.language
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
                "response_type": "document_summary"
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
            "session_id": None,
            "session_name": None
        }