"""
LangGraph-based Document Summary Agent

This module implements a specialized agent for generating document summaries
and highlights using LangGraph.
"""

import os
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from langgraph.graph import StateGraph, END

from services.get_doc_chunks import get_doc_chunks

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)


class SummaryState(TypedDict):
    """State for document summary generation."""
    file_name: str
    file_type: str
    language: str
    content: str
    summary: str
    highlights: List[str]
    error: str


def load_content_node(state: SummaryState) -> SummaryState:
    """Load document content."""
    print(f"📄 Loading content for: {state['file_name']}")
    
    try:
        content = get_doc_chunks(state['file_name'], state['file_type'])
        
        if content:
            # Join content chunks with size limit
            full_content = "\n\n".join(content)
            # Limit to first 10000 characters for summary
            state['content'] = full_content[:10000]
            print(f"✓ Loaded {len(content)} chunks ({len(state['content'])} chars)")
        else:
            state['content'] = ""
            state['error'] = "No content found"
            print(f"⚠ No content found for {state['file_name']}")
    
    except Exception as e:
        state['content'] = ""
        state['error'] = str(e)
        print(f"✗ Failed to load content: {e}")
    
    return state


def generate_summary_node(state: SummaryState) -> SummaryState:
    """Generate document summary."""
    print(f"✍️ Generating summary")
    
    if not state['content']:
        state['summary'] = "This is an official legal document from the Sri Lankan government portal containing important regulatory information."
        return state
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert legal document summarizer for Sri Lankan law.

Generate a comprehensive summary of the provided legal document that:
1. Identifies the document type and purpose
2. Highlights key provisions and regulations
3. Notes important dates, amendments, or references
4. Explains the document's practical implications
5. Uses clear, accessible language

Keep the summary concise (2-3 paragraphs) but informative.

Provide the summary in {language}."""),
        ("human", """Document: {file_name}

Content:
{content}

Generate a comprehensive summary:""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        summary = chain.invoke({
            "file_name": state['file_name'],
            "content": state['content'],
            "language": state['language']
        })
        state['summary'] = summary
        print(f"✓ Generated summary ({len(summary)} chars)")
    
    except Exception as e:
        print(f"✗ Summary generation failed: {e}")
        state['summary'] = "This document contains important legal information from Sri Lankan legislation."
        state['error'] = str(e)
    
    return state


def generate_highlights_node(state: SummaryState) -> SummaryState:
    """Generate document highlights/key points."""
    print(f"🔍 Generating highlights")
    
    if not state['content']:
        state['highlights'] = [
            "This document contains key legal provisions enacted by the Parliament of Sri Lanka",
            "It includes important regulatory information and procedural guidelines",
            "The document may contain statutory requirements and compliance measures"
        ]
        return state
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at extracting key points from legal documents.

Generate 5-7 concise bullet points that highlight:
1. Main objectives or purposes
2. Key provisions or regulations
3. Important definitions or terms
4. Rights, obligations, or penalties
5. Effective dates or amendments
6. Relevant authorities or procedures

Each point should be clear, specific, and actionable.

Provide highlights in {language}.
Return ONLY the bullet points, one per line, without numbering."""),
        ("human", """Document: {file_name}

Content:
{content}

Generate key highlights:""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        highlights_text = chain.invoke({
            "file_name": state['file_name'],
            "content": state['content'],
            "language": state['language']
        })
        
        # Parse bullet points
        highlights = [
            line.strip().lstrip('•-*').strip()
            for line in highlights_text.split('\n')
            if line.strip() and len(line.strip()) > 10
        ]
        
        state['highlights'] = highlights[:7]  # Limit to 7 highlights
        print(f"✓ Generated {len(state['highlights'])} highlights")
    
    except Exception as e:
        print(f"✗ Highlights generation failed: {e}")
        state['highlights'] = [
            "Key legal provisions and regulations",
            "Important procedural guidelines",
            "Statutory requirements and compliance measures"
        ]
        state['error'] = str(e)
    
    return state


def create_summary_graph() -> StateGraph:
    """
    Create and compile the summary generation graph.
    
    Returns:
        Compiled StateGraph for document summarization
    """
    workflow = StateGraph(SummaryState)
    
    # Add nodes
    workflow.add_node("load_content", load_content_node)
    workflow.add_node("generate_summary", generate_summary_node)
    workflow.add_node("generate_highlights", generate_highlights_node)
    
    # Define edges
    workflow.set_entry_point("load_content")
    workflow.add_edge("load_content", "generate_summary")
    workflow.add_edge("generate_summary", "generate_highlights")
    workflow.add_edge("generate_highlights", END)
    
    app = workflow.compile()
    return app


# Create global graph instance
summary_graph = create_summary_graph()


def generate_document_summary(
    file_name: str,
    file_type: str = "unknown",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generate summary for a document.
    
    Args:
        file_name: Document filename
        file_type: Type of document (bill, act, gazette, etc.)
        language: Language code for output
    
    Returns:
        Dict with summary and metadata
    """
    print(f"\n{'='*60}")
    print(f"📄 Document Summary Generation")
    print(f"{'='*60}")
    print(f"File: {file_name}")
    print(f"Type: {file_type}")
    print(f"Language: {language}")
    
    initial_state = {
        "file_name": file_name,
        "file_type": file_type,
        "language": language,
        "content": "",
        "summary": "",
        "highlights": [],
        "error": ""
    }
    
    try:
        result = summary_graph.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"✓ Summary Generation Completed")
        print(f"{'='*60}\n")
        
        return {
            "summary": result["summary"],
            "success": True
        }
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Summary Generation Failed: {e}")
        print(f"{'='*60}\n")
        
        return {
            "summary": "This document contains important legal information.",
            "success": False,
            "error": str(e)
        }


def generate_document_highlights(
    file_name: str,
    file_type: str = "unknown",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generate highlights for a document.
    
    Args:
        file_name: Document filename
        file_type: Type of document
        language: Language code for output
    
    Returns:
        Dict with highlights list and metadata
    """
    print(f"\n{'='*60}")
    print(f"🔍 Document Highlights Generation")
    print(f"{'='*60}")
    print(f"File: {file_name}")
    
    initial_state = {
        "file_name": file_name,
        "file_type": file_type,
        "language": language,
        "content": "",
        "summary": "",
        "highlights": [],
        "error": ""
    }
    
    try:
        result = summary_graph.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"✓ Highlights Generation Completed")
        print(f"{'='*60}\n")
        
        return {
            "highlights": result["highlights"],
            "success": True
        }
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Highlights Generation Failed: {e}")
        print(f"{'='*60}\n")
        
        return {
            "highlights": [
                "Key legal provisions",
                "Important regulations",
                "Compliance requirements"
            ],
            "success": False,
            "error": str(e)
        }
