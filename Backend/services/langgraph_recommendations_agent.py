"""
LangGraph-based Recommendations Agent

This module generates personalized document recommendations based on
user preferences and query history.
"""

import os
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, END

from config.llm_config import get_langchain_llm, get_provider_info
from services.langchain_retriever import create_hybrid_retriever

load_dotenv()

# Initialize LLM based on configuration
llm = get_langchain_llm(temperature=0.5)
provider_info = get_provider_info()
print(f"🤖 Recommendations Agent using: {provider_info['provider']} ({provider_info['model']})")


class RecommendationState(TypedDict):
    """State for recommendation generation."""
    username: str
    preferences: List[str]
    history: List[str]
    language: str
    search_query: str
    recommendations: List[Dict[str, Any]]
    error: str


def analyze_interests_node(state: RecommendationState) -> RecommendationState:
    """Analyze user interests and generate search query."""
    print(f"🔍 Analyzing user interests")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at understanding user interests in legal topics.

Analyze the user's query history and preferences to generate a comprehensive search query
that will retrieve relevant legal documents.

The search query should:
1. Identify main legal topics and areas of interest
2. Include relevant legal terminology
3. Cover related subtopics and adjacent areas
4. Be specific enough to find relevant documents
5. Be broad enough to capture diverse but related content

Examples:

History: ["Urban Council budget procedures", "Municipal governance", "Local government amendments"]
Query: "local government law, municipal administration, urban council regulations, budget procedures, governance frameworks, administrative compliance"

History: ["Cybercrime penalties", "Digital evidence collection", "Suspect rights during interrogation"]  
Query: "criminal law, cybercrime regulations, digital forensics, evidence procedures, suspect rights, law enforcement practices, criminal procedure code"

History: ["Company director obligations", "Shareholder dispute resolution", "Business entity registration"]
Query: "corporate law, company governance, director duties, shareholder rights, business registration, commercial regulations, corporate compliance"

Generate ONLY the search query, nothing else."""),
        ("human", """Username: {username}
Preferences: {preferences}
Query History: {history}

Generate search query:""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        search_query = chain.invoke({
            "username": state['username'],
            "preferences": ", ".join(state['preferences']) if state['preferences'] else "general legal topics",
            "history": "\n".join(state['history']) if state['history'] else "No history"
        })
        
        state['search_query'] = search_query.strip()
        print(f"✓ Generated search query: {state['search_query'][:100]}...")
    
    except Exception as e:
        print(f"✗ Interest analysis failed: {e}")
        # Fallback to basic query
        if state['history']:
            state['search_query'] = " ".join(state['history'][:3])
        else:
            state['search_query'] = "Sri Lankan legal documents regulations"
        state['error'] = str(e)
    
    return state


def retrieve_recommendations_node(state: RecommendationState) -> RecommendationState:
    """Retrieve relevant documents based on search query."""
    print(f"📚 Retrieving recommendations")
    
    try:
        retriever = create_hybrid_retriever(k=10)
        docs = retriever.invoke(state['search_query'])
        
        recommendations = []
        for doc in docs:
            filename = doc.metadata.get('name', doc.metadata.get('filename', 'Unknown'))
            doc_type = doc.metadata.get('type', 'document')
            
            recommendations.append({
                "filename": filename,
                "type": doc_type,
                "preview": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            })
        
        state['recommendations'] = recommendations
        print(f"✓ Retrieved {len(recommendations)} recommendations")
    
    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        state['recommendations'] = []
        state['error'] = str(e)
    
    return state


def rank_recommendations_node(state: RecommendationState) -> RecommendationState:
    """Rank and filter recommendations for relevance."""
    print(f"⭐ Ranking recommendations")
    
    if not state['recommendations']:
        return state
    
    # For now, keep top recommendations (already ranked by retriever)
    # Could add additional LLM-based ranking here
    state['recommendations'] = state['recommendations'][:5]
    
    print(f"✓ Finalized {len(state['recommendations'])} top recommendations")
    return state


def create_recommendations_graph() -> StateGraph:
    """
    Create and compile the recommendations graph.
    
    Returns:
        Compiled StateGraph for generating recommendations
    """
    workflow = StateGraph(RecommendationState)
    
    # Add nodes
    workflow.add_node("analyze_interests", analyze_interests_node)
    workflow.add_node("retrieve", retrieve_recommendations_node)
    workflow.add_node("rank", rank_recommendations_node)
    
    # Define edges
    workflow.set_entry_point("analyze_interests")
    workflow.add_edge("analyze_interests", "retrieve")
    workflow.add_edge("retrieve", "rank")
    workflow.add_edge("rank", END)
    
    app = workflow.compile()
    return app


# Create global graph instance
recommendations_graph = create_recommendations_graph()


def generate_recommendations(
    username: str,
    preferences: List[str] = None,
    history: List[str] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generate document recommendations for a user.
    
    Args:
        username: User identifier
        preferences: List of user preferences/topics
        history: List of previous queries
        language: Language code
    
    Returns:
        Dict with recommendations and metadata
    """
    print(f"\n{'='*60}")
    print(f"🎯 Generating Recommendations")
    print(f"{'='*60}")
    print(f"User: {username}")
    print(f"Preferences: {preferences}")
    print(f"History items: {len(history) if history else 0}")
    
    initial_state = {
        "username": username,
        "preferences": preferences or [],
        "history": history or [],
        "language": language,
        "search_query": "",
        "recommendations": [],
        "error": ""
    }
    
    try:
        result = recommendations_graph.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"✓ Recommendations Generated")
        print(f"{'='*60}\n")
        
        return {
            "recommendations": result["recommendations"],
            "search_query": result["search_query"],
            "success": True
        }
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Recommendation Generation Failed: {e}")
        print(f"{'='*60}\n")
        
        return {
            "recommendations": [],
            "search_query": "",
            "success": False,
            "error": str(e)
        }
