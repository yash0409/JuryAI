import os
import tempfile
import logging
import traceback
from pathlib import Path
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from typing import TypedDict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

from services.pdf_loader import load_and_chunk_pdf
from services.vector_store import embed_and_store
from services.retrieval import retrieve_context


app = FastAPI(
    title="VerdictIQ Legal Document Analyzer",
    description="AI-powered legal document analysis using LangGraph agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(tempfile.gettempdir()) / "verdictiq_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Pydantic models ──────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    collection_id: str
    query: str

class ChatRequest(BaseModel):
    collection_id: str
    message: str


# ── LangGraph state ──────────────────────────────────────────────────────────

class GraphState(TypedDict):
    query: str
    context: str
    summary: str
    clauses: str
    risks: str
    explanation: str


# ── Helper: get LLM (small model = higher free tier limit) ───────────────────

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",   # 1M tokens/day free vs 100k for 70b
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
        max_tokens=500,                  # keep each agent response short
    )


# ── Workflow nodes ────────────────────────────────────────────────────────────

def make_retriever_node(collection_id: str):
    def retriever_node(state: GraphState) -> GraphState:
        context = retrieve_context(
            state.get("query", "analyze this document"),
            collection_name=collection_id,
            top_k=4,
        )
        # Limit context to 2000 chars to save tokens
        return {"context": context[:2000]}
    return retriever_node


def summarizer_node(state: GraphState) -> GraphState:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a legal document summarizer. Summarize the following legal text in 100-150 words. Be concise and clear."),
        ("human", "Document text:\n{context}"),
    ])
    chain = prompt | llm | StrOutputParser()
    summary = chain.invoke({"context": state["context"]})
    return {"summary": summary}


def clause_node(state: GraphState) -> GraphState:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a legal clause extractor. Extract the 5 most important clauses from the text. Format each as:\nClause X.X: [one line description]"),
        ("human", "Document text:\n{context}"),
    ])
    chain = prompt | llm | StrOutputParser()
    clauses = chain.invoke({"context": state["context"]})
    return {"clauses": clauses}


def risk_node(state: GraphState) -> GraphState:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a legal risk analyst. Identify risky clauses, vague language, and missing protections. Label each as High or Medium risk. Keep it under 200 words."),
        ("human", "Document text:\n{context}"),
    ])
    chain = prompt | llm | StrOutputParser()
    risks = chain.invoke({"context": state["context"]})
    return {"risks": risks}


def explainer_node(state: GraphState) -> GraphState:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a legal explainer. Rewrite the most complex legal language from the text in plain simple English that a non-lawyer can understand. Keep it under 200 words."),
        ("human", "Document text:\n{context}"),
    ])
    chain = prompt | llm | StrOutputParser()
    explanation = chain.invoke({"context": state["context"]})
    return {"explanation": explanation}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "VerdictIQ Legal Document Analyzer API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        content = await file.read()
        safe_filename = file.filename.replace(" ", "_").replace("/", "_")
        file_path = UPLOAD_DIR / safe_filename

        with open(file_path, "wb") as f:
            f.write(content)

        chunks = load_and_chunk_pdf(str(file_path))

        if not chunks:
            raise HTTPException(status_code=500, detail="Failed to extract content from PDF")

        collection_name = Path(file.filename).stem.replace(" ", "_").replace(".", "_")
        embed_and_store(chunks, collection_name)

        logger.info(f"Uploaded and embedded: {collection_name} ({len(chunks)} chunks)")
        return {"collection_id": collection_name}

    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/analyze")
async def analyze_document(request: AnalyzeRequest):
    try:
        collection_id = request.collection_id
        query = request.query or "Analyze this legal document"
        logger.info(f"Starting analysis for collection_id: {collection_id}")

        initial_state: GraphState = {
            "query": query,
            "context": "",
            "summary": "",
            "clauses": "",
            "risks": "",
            "explanation": "",
        }

        # Build workflow fresh each request so collection_id is captured correctly
        workflow = StateGraph(GraphState)
        workflow.add_node("retriever", make_retriever_node(collection_id))
        workflow.add_node("summarizer", summarizer_node)
        workflow.add_node("clause_agent", clause_node)
        workflow.add_node("risk_agent", risk_node)
        workflow.add_node("explainer", explainer_node)

        workflow.add_edge(START, "retriever")
        workflow.add_edge("retriever", "summarizer")
        workflow.add_edge("summarizer", "clause_agent")
        workflow.add_edge("clause_agent", "risk_agent")
        workflow.add_edge("risk_agent", "explainer")
        workflow.add_edge("explainer", END)

        compiled = workflow.compile()
        result = compiled.invoke(initial_state)
        logger.info("Workflow completed successfully")

        return {
            "summary": result.get("summary", ""),
            "clauses": result.get("clauses", ""),
            "risks": result.get("risks", ""),
            "explain": result.get("explanation", ""),  # frontend expects "explain" key
        }

    except Exception as e:
        error_msg = traceback.format_exc()
        logger.error(f"Error in /analyze: {error_msg}")
        return JSONResponse(status_code=500, content={"detail": str(e), "traceback": error_msg})


@app.post("/chat")
async def chat_with_document(request: ChatRequest):
    try:
        collection_id = request.collection_id
        message = request.message

        if not message:
            return JSONResponse(status_code=400, content={"detail": "Message cannot be empty"})

        logger.info(f"Chat request — collection: {collection_id}, message: {message}")

        context = retrieve_context(message, collection_name=collection_id, top_k=4)
        context = context[:2000]  # limit tokens

        if not context:
            return {"response": "I couldn't find relevant information in the document to answer your question."}

        llm = get_llm()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal assistant. Answer the user's question based only on the document context below.
Be concise (under 150 words). Cite clause numbers when relevant.

Context:
{context}"""),
            ("human", "{question}"),
        ])

        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": message})

        logger.info("Chat response generated successfully")
        return {"response": response}

    except Exception as e:
        error_msg = traceback.format_exc()
        logger.error(f"Error in /chat: {error_msg}")
        return JSONResponse(status_code=500, content={"detail": str(e), "traceback": error_msg})