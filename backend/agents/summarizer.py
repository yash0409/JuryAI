"""
Document Summarizer Agent
Generates concise summaries of legal documents.
"""

import os
from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def _get_llm():
    """Get the Groq LLM instance."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )


SUMMARIZER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document summarization expert. 
Your task is to create clear, concise summaries of legal documents while preserving key information.

Focus on:
- Main parties involved
- Key terms and conditions
- Important dates and deadlines
- Obligations and rights
- Critical clauses

Provide a well-structured summary that captures the essence of the document in approximately 150 words."""),
    ("human", "Please summarize the following legal document in about 150 words:\n\n{document_content}")
])


def summarizer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarizes the legal document context in approximately 150 words.
    
    Args:
        state: LangGraph state dictionary containing 'context' key with document text
        
    Returns:
        Updated state with 'summary' key containing the generated summary
    """
    context = state.get("context", "")
    if not context:
        return {**state, "summary": "No document context provided."}
    
    llm = _get_llm()
    chain = SUMMARIZER_PROMPT | llm | StrOutputParser()
    summary = chain.invoke({"document_content": context})
    
    return {**state, "summary": summary}


# --- Existing class-based implementation below ---

class SummarizerAgent:
    """Agent responsible for summarizing legal documents."""
    
    def __init__(self, llm):
        """
        Initialize the Summarizer Agent.
        
        Args:
            llm: Language model instance for generating summaries
        """
        self.llm = llm
        self.chain = SUMMARIZER_PROMPT | llm | StrOutputParser()
    
    def summarize(self, document_content: str) -> Dict[str, Any]:
        """
        Generate a summary of the provided document content.
        
        Args:
            document_content: The full text content of the document
            
        Returns:
            Dictionary containing the summary and metadata
        """
        try:
            summary = self.chain.invoke({"document_content": document_content})
            return {
                "success": True,
                "summary": summary,
                "original_length": len(document_content),
                "summary_length": len(summary)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": None
            }
    
    async def asummmarize(self, document_content: str) -> Dict[str, Any]:
        """
        Asynchronously generate a summary of the provided document content.
        
        Args:
            document_content: The full text content of the document
            
        Returns:
            Dictionary containing the summary and metadata
        """
        try:
            summary = await self.chain.ainvoke({"document_content": document_content})
            return {
                "success": True,
                "summary": summary,
                "original_length": len(document_content),
                "summary_length": len(summary)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": None
            }