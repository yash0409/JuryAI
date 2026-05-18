# Jury - Legal Document Analyzer

An AI-powered legal document analysis tool built with FastAPI, LangGraph agents, and Next.js. Upload legal PDFs and get automated summaries, clause extraction, risk analysis, and explanations powered by Groq's LLaMa 3.1 8B model.

## Features

- **Document Upload**: Upload PDF legal documents for analysis
- **Automated Analysis**: Multi-agent workflow that provides:
  - Document summarization
  - Key clause extraction
  - Risk identification
  - Plain-language explanations
- **Clause Source Tags**: Automatically detects and displays clause references (e.g., "Clause 3.1", "§ 2.5") as source tags
- **Chat Assistant**: Ask questions about your document with RAG-powered responses

## Quick Start

### Terminal 1: Backend Server

```bash
cd backend && uvicorn main:app --reload
```

### Terminal 2: Frontend Server

```bash
cd frontend && npm run dev
```

> **Note**: You need a Groq API key. Update `backend/.env` with your key before starting:
> ```
> GROQ_API_KEY=your_key_here
> ```
> Get one at [Groq Console](https://console.groq.com/keys).

## Project Structure

```
jury/
├── backend/
│   ├── agents/           # LangGraph AI agents
│   │   ├── summarizer.py
│   │   ├── clause_agent.py
│   │   ├── risk_agent.py
│   │   └── explainer.py
│   ├── graph/            # LangGraph workflow
│   │   └── workflow.py
│   ├── routes/           # API routes
│   ├── services/         # Core services
│   │   ├── pdf_loader.py
│   │   ├── vector_store.py
│   │   └── retrieval.py
│   ├── .env              # Environment variables (create this)
│   ├── main.py           # FastAPI entry point
│   └── requirements.txt
└── frontend/
    ├── app/              # Next.js app directory
    │   ├── analysis/     # Analysis results page
    │   └── upload/       # Document upload page
    ├── components/       # Reusable UI components
    └── lib/              # Utilities
```

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /upload` - Upload a PDF document
- `POST /analyze` - Analyze a document
- `POST /chat` - Chat with a document

## Tech Stack

**Backend:**
- FastAPI
- LangGraph / LangChain
- ChromaDB (vector database)
- Groq API (Mistral Saba 24B model)

**Frontend:**
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
