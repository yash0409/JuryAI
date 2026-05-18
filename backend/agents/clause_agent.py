"""
Clause Analysis Agent
Identifies and analyzes specific clauses in legal documents.
"""

import os
from typing import Dict, Any, List

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field


def _get_llm():
    """Get the Groq LLM instance."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )


class ClauseInfo(BaseModel):
    """Model for clause information."""
    clause_number: str = Field(description="The clause number or section identifier (e.g., 'Clause 3.1', 'Section 5')")
    description: str = Field(description="One-line description of what this clause means")


CLAUSE_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal clause identification expert. 
Your task is to identify the 5 most important clauses in legal documents.

For each clause, provide:
1. The clause number or section identifier (e.g., 'Clause 3.1', 'Section 5', 'Article II')
2. A one-line description of what this clause means

Focus on the most critical clauses such as:
- Termination clauses
- Liability and indemnification
- Confidentiality agreements
- Dispute resolution
- Payment terms
- Intellectual property
- Non-compete agreements
- Amendment procedures

Return ONLY the 5 most important clauses."""),
    ("human", "Extract the 5 most important clauses from the following legal document:\n\n{document_content}")
])


def clause_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the 5 most important clauses from the legal document context.
    Each clause includes a clause number and one-line description.
    
    Args:
        state: LangGraph state dictionary containing 'context' key with document text
        
    Returns:
        Updated state with 'clauses' key containing a list of clause dictionaries
    """
    context = state.get("context", "")
    if not context:
        return {**state, "clauses": []}
    
    llm = _get_llm()
    json_parser = JsonOutputParser(pydantic_object=ClauseInfo)
    chain = CLAUSE_EXTRACTION_PROMPT | llm | json_parser
    
    try:
        clauses = chain.invoke({"document_content": context})
        # Ensure we return a list even if a single dict is returned
        if isinstance(clauses, dict):
            clauses = [clauses]
        elif not isinstance(clauses, list):
            clauses = []
        return {**state, "clauses": clauses}
    except Exception as e:
        # Fallback to string parsing if JSON parsing fails
        str_parser = StrOutputParser()
        str_chain = CLAUSE_EXTRACTION_PROMPT | llm | str_parser
        result = str_chain.invoke({"document_content": context})
        return {**state, "clauses": [{"clause_number": "N/A", "description": result}]}


# --- Existing class-based implementation below ---

class ClauseAgent:
    """Agent responsible for identifying and analyzing clauses in legal documents."""
    
    def __init__(self, llm):
        """
        Initialize the Clause Agent.
        
        Args:
            llm: Language model instance for clause analysis
        """
        self.llm = llm
        self.json_parser = JsonOutputParser(pydantic_object=ClauseInfo)
        self.identification_chain = CLAUSE_EXTRACTION_PROMPT | llm | StrOutputParser()
    
    def identify_clauses(self, document_content: str) -> Dict[str, Any]:
        """
        Identify and analyze clauses in the document.
        
        Args:
            document_content: The full text content of the document
            
        Returns:
            Dictionary containing identified clauses and metadata
        """
        try:
            clauses = self.identification_chain.invoke({"document_content": document_content})
            return {
                "success": True,
                "clauses": clauses,
                "clause_count": len(clauses.split('\n')) if clauses else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "clauses": None
            }
    
    async def aidentify_clauses(self, document_content: str) -> Dict[str, Any]:
        """
        Asynchronously identify and analyze clauses in the document.
        
        Args:
            document_content: The full text content of the document
            
        Returns:
            Dictionary containing identified clauses and metadata
        """
        try:
            clauses = await self.identification_chain.ainvoke({"document_content": document_content})
            return {
                "success": True,
                "clauses": clauses,
                "clause_count": len(clauses.split('\n')) if clauses else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "clauses": None
            }
    
    def analyze_specific_clause(self, clause_text: str, clause_type: str) -> Dict[str, Any]:
        """
        Provide detailed analysis of a specific clause.
        
        Args:
            clause_text: The text of the specific clause
            clause_type: The type of clause being analyzed
            
        Returns:
            Dictionary containing detailed analysis
        """
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a legal expert specializing in {clause_type} clauses.
Provide a detailed analysis including:
- Legal implications
- Potential risks
- Recommendations for review"""),
            ("human", f"Analyze this {clause_type} clause:\n\n{clause_text}")
        ])
        
        try:
            chain = analysis_prompt | self.llm | StrOutputParser()
            analysis = chain.invoke({})
            return {
                "success": True,
                "clause_type": clause_type,
                "clause_text": clause_text,
                "analysis": analysis
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }