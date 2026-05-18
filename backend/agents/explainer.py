"""
Legal Explainer Agent
Provides plain-language explanations of legal terms and concepts.
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


EXPLAINER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal explainer expert who translates complex legal language into clear, 
easy-to-understand explanations for non-lawyers.

Your explanations should:
- Use simple, everyday language
- Provide real-world examples when helpful
- Explain the practical implications
- Highlight what the reader should pay attention to
- Avoid legal jargon where possible, or explain it when necessary

Target audience: Business professionals and individuals without legal training."""),
    ("human", "Explain the following legal text in simple terms:\n\n{text_to_explain}")
])


PLAIN_ENGLISH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal language simplification expert. Your task is to rewrite complex 
legal text into plain, simple English that anyone can understand.

Guidelines:
- Replace legal jargon with everyday words
- Break long, complex sentences into shorter, clearer ones
- Use active voice instead of passive voice
- Explain any legal concepts that have no simple equivalent
- Keep the original meaning intact while making it accessible
- Write at a level that someone without legal training can easily understand

Your goal is to make the legal text comprehensible to a general audience."""),
    ("human", "Rewrite the following legal text into plain, simple English:\n\n{document_content}")
])


def explainer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rewrites the most complex legal language from the context into plain simple English.
    
    Args:
        state: LangGraph state dictionary containing 'context' key with document text
        
    Returns:
        Updated state with 'explanation' key containing the simplified explanation
    """
    context = state.get("context", "")
    if not context:
        return {**state, "explanation": "No document context provided."}
    
    llm = _get_llm()
    chain = PLAIN_ENGLISH_PROMPT | llm | StrOutputParser()
    explanation = chain.invoke({"document_content": context})
    
    return {**state, "explanation": explanation}


# --- Existing class-based implementation below ---

class ExplainerAgent:
    """Agent responsible for explaining legal concepts in plain language."""
    
    def __init__(self, llm):
        """
        Initialize the Explainer Agent.
        
        Args:
            llm: Language model instance for generating explanations
        """
        self.llm = llm
        self.explanation_chain = EXPLAINER_PROMPT | llm | StrOutputParser()
    
    def explain(self, text_to_explain: str) -> Dict[str, Any]:
        """
        Provide a plain-language explanation of legal text.
        
        Args:
            text_to_explain: The legal text or concept to explain
            
        Returns:
            Dictionary containing the explanation and metadata
        """
        try:
            explanation = self.explanation_chain.invoke({"text_to_explain": text_to_explain})
            return {
                "success": True,
                "explanation": explanation,
                "original_text": text_to_explain[:200] + "..." if len(text_to_explain) > 200 else text_to_explain
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "explanation": None
            }
    
    async def aexplain(self, text_to_explain: str) -> Dict[str, Any]:
        """
        Asynchronously provide a plain-language explanation.
        
        Args:
            text_to_explain: The legal text or concept to explain
            
        Returns:
            Dictionary containing the explanation and metadata
        """
        try:
            explanation = await self.explanation_chain.ainvoke({"text_to_explain": text_to_explain})
            return {
                "success": True,
                "explanation": explanation,
                "original_text": text_to_explain[:200] + "..." if len(text_to_explain) > 200 else text_to_explain
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "explanation": None
            }
    
    def explain_term(self, legal_term: str) -> Dict[str, Any]:
        """
        Explain a specific legal term or concept.
        
        Args:
            legal_term: The legal term to explain
            
        Returns:
            Dictionary containing the term explanation
        """
        term_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal dictionary expert. Provide clear, concise definitions 
of legal terms with practical examples."""),
            ("human", f"Explain the legal term '{legal_term}' in simple language with an example.")
        ])
        
        try:
            chain = term_prompt | self.llm | StrOutputParser()
            explanation = chain.invoke({})
            return {
                "success": True,
                "term": legal_term,
                "explanation": explanation
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "explanation": None
            }