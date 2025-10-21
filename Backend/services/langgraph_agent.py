"""
LangGraph-based Legal AI Agent

This module implements a state graph for the legal AI assistant using LangGraph.
It handles:
- Query processing and translation
- Document retrieval
- Response generation with context
- Multi-turn conversations with history
"""

import os
from typing import List, Dict, Any, Annotated, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from config.llm_config import get_langchain_llm, get_provider_info
from services.langchain_retriever import create_hybrid_retriever
# Temporarily disabled to allow initial deployment
# from services.translator import translate
try:
    from services.translator import translate
except Exception as e:
    print(f"⚠️ Translator not available: {e}")
    translate = None

load_dotenv()

# Initialize LLM based on configuration
llm = get_langchain_llm(temperature=0.3)
provider_info = get_provider_info()
print(f"🤖 LangGraph Agent using: {provider_info['provider']} ({provider_info['model']})")


class AgentState(TypedDict):
    """State for the Legal AI agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    language: str
    original_query: str
    context: str
    retrieved_docs: List[Dict[str, Any]]
    response: str
    citations: List[str]


def should_translate(state: AgentState) -> str:
    """Decide if translation is needed."""
    if state["language"] != "en":
        return "translate"
    return "retrieve"


def translate_node(state: AgentState) -> AgentState:
    """Translate query to English if needed."""
    print(f"🌐 Translating query from {state['language']} to English")
    
    try:
        translated = translate(
            state["query"],
            src_language=state["language"],
            target_language="en"
        )
        state["query"] = translated
        print(f"✓ Translated: {translated}")
    except Exception as e:
        print(f"⚠ Translation failed: {e}, using original query")
    
    return state


def retrieve_node(state: AgentState) -> AgentState:
    """Retrieve relevant documents."""
    print(f"📚 Retrieving documents for: {state['query']}")
    
    retriever = create_hybrid_retriever(k=5)
    docs = retriever.invoke(state["query"])
    
    # Extract context and metadata
    context_parts = []
    citations = []
    retrieved_docs = []
    
    for doc in docs:
        context_parts.append(doc.page_content)
        filename = doc.metadata.get('name', doc.metadata.get('filename', 'Unknown'))
        citations.append(filename)
        retrieved_docs.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    
    state["context"] = "\n\n".join(context_parts)
    state["citations"] = list(set(citations))
    state["retrieved_docs"] = retrieved_docs
    
    print(f"✓ Retrieved {len(docs)} documents")
    print(f"✓ Citations: {state['citations']}")
    
    return state


def generate_node(state: AgentState) -> AgentState:
    """Generate response using LLM with retrieved context."""
    print(f"🤖 Generating response")
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant specialized in Sri Lankan law. 

Your responsibilities:
1. Answer questions accurately using the provided context
2. Cite sources using [filename] format after relevant sentences
3. If context is insufficient, acknowledge limitations
4. Recommend consulting legal professionals for legal advice
5. Adapt your tone: professional for technical questions, accessible for general queries
6. Always end with a friendly follow-up question to continue the conversation

Context from legal documents:
{context}

Citations available: {citations}

Provide your answer in {language}."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{query}")
    ])
    
    # Create chain
    chain = (
        {
            "context": lambda x: x["context"],
            "citations": lambda x: ", ".join(x["citations"]),
            "language": lambda x: x["language"],
            "messages": lambda x: x["messages"],
            "query": lambda x: x["query"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    try:
        response = chain.invoke(state)
        state["response"] = response
        
        # Add AI message to conversation
        state["messages"].append(AIMessage(content=response))
        
        print(f"✓ Generated response ({len(response)} chars)")
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        state["response"] = "I apologize, but I encountered an error generating a response. Please try again."
        state["messages"].append(AIMessage(content=state["response"]))
    
    return state


def create_legal_ai_graph() -> StateGraph:
    """
    Create and compile the LangGraph state graph for the legal AI assistant.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("translate", translate_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    
    # Define edges
    workflow.set_conditional_entry_point(
        should_translate,
        {
            "translate": "translate",
            "retrieve": "retrieve"
        }
    )
    
    workflow.add_edge("translate", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # Compile with checkpointing for conversation memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# Create global graph instance
legal_ai_graph = create_legal_ai_graph()


def run_legal_ai_agent(
    query: str,
    language: str = "en",
    history: List[Dict[str, str]] = None,
    session_id: str = "default"
) -> Dict[str, Any]:
    """
    Run the legal AI agent with a query.
    
    Args:
        query: User's question
        language: Language code (en, si, ta)
        history: Conversation history (list of dicts with 'role' and 'content')
        session_id: Session ID for conversation continuity
    
    Returns:
        Dict with response, citations, and metadata
    """
    print(f"\n{'='*60}")
    print(f"🚀 Legal AI Agent Started")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Language: {language}")
    print(f"Session: {session_id}")
    
    # Convert history to LangChain messages
    messages = []
    if history:
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if content:
                if role == 'user':
                    messages.append(HumanMessage(content=content))
                elif role == 'assistant' or role == 'ai':
                    messages.append(AIMessage(content=content))
    
    # Add current query
    messages.append(HumanMessage(content=query))
    
    # Initial state
    initial_state = {
        "messages": messages,
        "query": query,
        "language": language,
        "original_query": query,
        "context": "",
        "retrieved_docs": [],
        "response": "",
        "citations": []
    }
    
    # Run graph
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        result = legal_ai_graph.invoke(initial_state, config)
        
        print(f"\n{'='*60}")
        print(f"✓ Legal AI Agent Completed")
        print(f"{'='*60}\n")
        
        return {
            "response": result["response"],
            "citations": result["citations"],
            "retrieved_docs": result["retrieved_docs"],
            "language": result["language"],
            "success": True
        }
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Legal AI Agent Failed: {e}")
        print(f"{'='*60}\n")
        
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "citations": [],
            "retrieved_docs": [],
            "language": language,
            "success": False,
            "error": str(e)
        }


# Async version for FastAPI
async def run_legal_ai_agent_async(
    query: str,
    language: str = "en",
    history: List[Dict[str, str]] = None,
    session_id: str = "default"
) -> Dict[str, Any]:
    """Async wrapper for the legal AI agent."""
    # For now, just call the sync version
    # TODO: Implement true async with astream
    return run_legal_ai_agent(query, language, history, session_id)
