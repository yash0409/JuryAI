"""
Analysis Routes
API endpoints for document analysis.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
import os

router = APIRouter()

# In-memory storage for demo purposes
# In production, use a proper database
document_store = {}


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload a PDF document for analysis.
    
    Returns:
        Document ID and basic information
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Generate a simple document ID
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Store document
        document_store[doc_id] = {
            "filename": file.filename,
            "content_bytes": content,
            "status": "uploaded",
            "analysis": None
        }
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "message": "Document uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.post("/analyze/{document_id}")
async def analyze_document(document_id: str) -> Dict[str, Any]:
    """
    Analyze an uploaded document.
    
    This endpoint triggers the full analysis workflow including:
    - Document summarization
    - Clause identification
    - Risk assessment
    - Plain language explanations
    
    Returns:
        Analysis results
    """
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = document_store[document_id]
    
    try:
        # Import services for document processing
        from services.pdf_loader import PDFLoader
        
        # Load PDF content
        loader = PDFLoader()
        result = loader.load_pdf_from_bytes(doc["content_bytes"], doc["filename"])
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {result.get('error')}")
        
        document_content = result["content"]
        metadata = result["metadata"]
        
        # Store processed content
        doc["content_text"] = document_content
        doc["metadata"] = metadata
        doc["status"] = "processing"
        
        # Initialize agents (in production, these should be initialized once at startup)
        from agents.summarizer import SummarizerAgent
        from agents.clause_agent import ClauseAgent
        from agents.risk_agent import RiskAgent
        from agents.explainer import ExplainerAgent
        from graph.workflow import DocumentAnalysisWorkflow
        
        # Note: In production, LLM should be properly initialized with API keys
        # This is a placeholder - actual implementation would use environment variables
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1)
        except Exception:
            # Fallback for demo without API key
            from langchain_core.language_models.fake import FakeListLLM
            llm = FakeListLLM(responses=[
                "This is a demo response. Configure Google Generative AI API key for real analysis.",
                "Demo clause analysis",
                "Demo risk assessment",
                "Demo explanation"
            ])
        
        # Initialize agents
        summarizer = SummarizerAgent(llm)
        clause_agent = ClauseAgent(llm)
        risk_agent = RiskAgent(llm)
        explainer = ExplainerAgent(llm)
        
        # Create and run workflow
        workflow = DocumentAnalysisWorkflow(
            summarizer=summarizer,
            clause_agent=clause_agent,
            risk_agent=risk_agent,
            explainer=explainer
        )
        
        # Execute analysis
        analysis_result = workflow.run(document_content, metadata)
        
        # Store analysis
        doc["analysis"] = analysis_result
        doc["status"] = "completed"
        
        return {
            "success": True,
            "document_id": document_id,
            "analysis": analysis_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analysis/{document_id}")
async def get_analysis(document_id: str) -> Dict[str, Any]:
    """
    Get the analysis results for a document.
    
    Returns:
        Analysis results if available
    """
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = document_store[document_id]
    
    if doc.get("analysis") is None:
        return {
            "success": True,
            "document_id": document_id,
            "status": doc.get("status", "unknown"),
            "message": "Analysis not yet completed. Please run analysis first.",
            "analysis": None
        }
    
    return {
        "success": True,
        "document_id": document_id,
        "status": doc.get("status"),
        "analysis": doc["analysis"]
    }


@router.post("/analyze-text")
async def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text content directly without file upload.
    
    This endpoint is useful for analyzing text copied from documents.
    
    Returns:
        Analysis results
    """
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text content is required")
    
    try:
        # Initialize agents
        from agents.summarizer import SummarizerAgent
        from agents.clause_agent import ClauseAgent
        from agents.risk_agent import RiskAgent
        from agents.explainer import ExplainerAgent
        from graph.workflow import DocumentAnalysisWorkflow
        
        # Note: In production, LLM should be properly initialized with API keys
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1)
        except Exception:
            from langchain_core.language_models.fake import FakeListLLM
            llm = FakeListLLM(responses=[
                "This is a demo response. Configure Google Generative AI API key for real analysis.",
                "Demo clause analysis",
                "Demo risk assessment",
                "Demo explanation"
            ])
        
        # Initialize agents
        summarizer = SummarizerAgent(llm)
        clause_agent = ClauseAgent(llm)
        risk_agent = RiskAgent(llm)
        explainer = ExplainerAgent(llm)
        
        # Create and run workflow
        workflow = DocumentAnalysisWorkflow(
            summarizer=summarizer,
            clause_agent=clause_agent,
            risk_agent=risk_agent,
            explainer=explainer
        )
        
        # Execute analysis
        analysis_result = workflow.run(text, {"source": "direct_text_input"})
        
        return {
            "success": True,
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/documents")
async def list_documents() -> Dict[str, Any]:
    """
    List all uploaded documents.
    
    Returns:
        List of documents with their status
    """
    documents = []
    for doc_id, doc in document_store.items():
        documents.append({
            "document_id": doc_id,
            "filename": doc.get("filename", "unknown"),
            "status": doc.get("status", "unknown"),
            "has_analysis": doc.get("analysis") is not None
        })
    
    return {
        "success": True,
        "documents": documents,
        "total_count": len(documents)
    }


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> Dict[str, Any]:
    """
    Delete a document and its analysis.
    
    Returns:
        Deletion status
    """
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        del document_store[document_id]
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")