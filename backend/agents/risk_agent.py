"""
Risk Assessment Agent
Evaluates potential risks and red flags in legal documents.
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


class RiskInfo(BaseModel):
    """Model for risk information."""
    risk_type: str = Field(description="Type of risk (e.g., vague language, liability concern, missing protection)")
    description: str = Field(description="Description of the specific risk identified")
    severity: str = Field(description="Risk severity level: High, Medium, or Low")
    details: str = Field(description="Additional details about the risk and its potential impact")


RISK_IDENTIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal risk assessment expert with extensive experience in contract review.
Your task is to identify potential risks, red flags, and concerning provisions in legal documents.

Identify and categorize risks including:
- Risky terms that could expose parties to liability
- Vague or ambiguous language that could lead to disputes
- Liability concerns (unlimited liability, one-sided indemnification)
- Missing protections (lack of limitation of liability, no termination rights)
- Unfair or one-sided provisions
- Compliance and regulatory risks

For each risk identified:
1. Describe the specific risk
2. Label the severity as High, Medium, or Low
3. Explain the potential impact
4. Note any missing protections

Return a structured list of risks with their severity levels."""),
    ("human", "Perform a comprehensive risk assessment of the following legal document. Identify risky terms, vague language, liability concerns, and missing protections:\n\n{document_content}")
])


def risk_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifies risky terms, vague language, liability concerns, and missing protections.
    Each risk is labeled as High, Medium, or Low severity.
    
    Args:
        state: LangGraph state dictionary containing 'context' key with document text
        
    Returns:
        Updated state with 'risks' key containing a list of risk dictionaries
    """
    context = state.get("context", "")
    if not context:
        return {**state, "risks": []}
    
    llm = _get_llm()
    json_parser = JsonOutputParser(pydantic_object=RiskInfo)
    chain = RISK_IDENTIFICATION_PROMPT | llm | json_parser
    
    try:
        risks = chain.invoke({"document_content": context})
        # Ensure we return a list even if a single dict is returned
        if isinstance(risks, dict):
            risks = [risks]
        elif not isinstance(risks, list):
            risks = []
        return {**state, "risks": risks}
    except Exception as e:
        # Fallback to string parsing if JSON parsing fails
        str_parser = StrOutputParser()
        str_chain = RISK_IDENTIFICATION_PROMPT | llm | str_parser
        result = str_chain.invoke({"document_content": context})
        return {**state, "risks": [{"risk_type": "General Assessment", "description": result, "severity": "Medium", "details": ""}]}


# --- Existing class-based implementation below ---

class RiskAgent:
    """Agent responsible for assessing risks in legal documents."""
    
    def __init__(self, llm):
        """
        Initialize the Risk Assessment Agent.
        
        Args:
            llm: Language model instance for risk analysis
        """
        self.llm = llm
        self.assessment_chain = RISK_IDENTIFICATION_PROMPT | llm | StrOutputParser()
    
    def assess_risks(self, document_content: str) -> Dict[str, Any]:
        """
        Perform a comprehensive risk assessment of the document.
        
        Args:
            document_content: The full text content of the document
            
        Returns:
            Dictionary containing risk assessment results
        """
        try:
            assessment = self.assessment_chain.invoke({"document_content": document_content})
            return {
                "success": True,
                "risk_assessment": assessment,
                "document_analyzed": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "risk_assessment": None
            }
    
    async def aassess_risks(self, document_content: str) -> Dict[str, Any]:
        """
        Asynchronously perform a comprehensive risk assessment.
        
        Args:
            document_content: The full text content of the document
            
        Returns:
            Dictionary containing risk assessment results
        """
        try:
            assessment = await self.assessment_chain.ainvoke({"document_content": document_content})
            return {
                "success": True,
                "risk_assessment": assessment,
                "document_analyzed": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "risk_assessment": None
            }
    
    def evaluate_specific_risk(self, clause_text: str, risk_category: str) -> Dict[str, Any]:
        """
        Evaluate a specific risk category for a given clause.
        
        Args:
            clause_text: The clause text to evaluate
            risk_category: The risk category to focus on
            
        Returns:
            Dictionary containing specific risk evaluation
        """
        specific_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a legal expert specializing in {risk_category} risk assessment.
Provide a detailed evaluation including:
- Specific risk factors
- Likelihood of risk materializing
- Potential impact
- Mitigation strategies"""),
            ("human", f"Evaluate the {risk_category} risks in this clause:\n\n{clause_text}")
        ])
        
        try:
            chain = specific_prompt | self.llm | StrOutputParser()
            evaluation = chain.invoke({})
            return {
                "success": True,
                "risk_category": risk_category,
                "clause_text": clause_text,
                "evaluation": evaluation
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "evaluation": None
            }