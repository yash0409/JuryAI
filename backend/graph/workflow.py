"""
Legal Document Analysis Workflow
Defines the LangGraph StateGraph for document analysis.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents.summarizer import summarizer_agent
from agents.clause_agent import clause_agent
from agents.risk_agent import risk_agent
from agents.explainer import explainer_agent
from services.retrieval import retrieve_context


class GraphState(TypedDict):
    query: str
    context: str
    summary: str
    clauses: str
    risks: str
    explanation: str


def retriever_node(state: GraphState) -> GraphState:
    """Node that retrieves context using the retrieval service."""
    query = state.get("query", "")
    # Use a default collection name; can be customized as needed
    context = retrieve_context(query, collection_name="legal_documents", top_k=5)
    return {"context": context}


def build_workflow() -> StateGraph:
    """Build and return the compiled StateGraph workflow."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("retriever_node", retriever_node)
    workflow.add_node("summarizer_agent", summarizer_agent)
    workflow.add_node("clause_agent", clause_agent)
    workflow.add_node("risk_agent", risk_agent)
    workflow.add_node("explainer_agent", explainer_agent)

    # Set entry point
    workflow.add_edge(START, "retriever_node")

    # Add edges in sequence
    workflow.add_edge("retriever_node", "summarizer_agent")
    workflow.add_edge("summarizer_agent", "clause_agent")
    workflow.add_edge("clause_agent", "risk_agent")
    workflow.add_edge("risk_agent", "explainer_agent")
    workflow.add_edge("explainer_agent", END)

    return workflow.compile()


# Export the compiled graph as `app`
app = build_workflow()