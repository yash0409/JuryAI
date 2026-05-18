"""
Retrieval Service
Handles document retrieval and RAG (Retrieval-Augmented Generation) operations.
"""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document analysis assistant. Use the following context from retrieved documents 
to answer questions accurately. If the answer cannot be found in the context, state that clearly.

Always base your responses on the provided context and indicate when you're making inferences."""),
    ("human", "Context from documents:\n{context}\n\nQuestion: {question}\n\nPlease provide a comprehensive answer based on the context.")
])


class RetrievalService:
    """Service for document retrieval and RAG operations."""
    
    def __init__(self, vector_store, llm):
        """
        Initialize the Retrieval Service.
        
        Args:
            vector_store: VectorStore instance for document search
            llm: Language model instance for generating answers
        """
        self.vector_store = vector_store
        self.llm = llm
        self.rag_chain = RAG_PROMPT | llm | StrOutputParser()
    
    def retrieve_and_answer(
        self, 
        query: str, 
        n_results: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant documents and generate an answer.
        
        Args:
            query: The question or query text
            n_results: Number of documents to retrieve
            filter_metadata: Optional metadata filter
            
        Returns:
            Dictionary containing the answer and retrieved documents
        """
        try:
            # Search for relevant documents
            search_results = self.vector_store.search(query, n_results, filter_metadata)
            
            if not search_results.get("success"):
                return {
                    "success": False,
                    "error": search_results.get("error", "Search failed"),
                    "answer": None,
                    "sources": []
                }
            
            # Extract documents from search results
            documents = search_results.get("results", {}).get("documents", [[]])[0]
            distances = search_results.get("results", {}).get("distances", [[]])[0]
            metadatas = search_results.get("results", {}).get("metadatas", [[]])[0]
            
            # Create context from retrieved documents
            context = "\n\n".join([f"[Document {i+1}]:\n{doc}" for i, doc in enumerate(documents)])
            
            # Generate answer using RAG
            answer = self.rag_chain.invoke({"context": context, "question": query})
            
            # Prepare sources information
            sources = []
            for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                sources.append({
                    "document_index": i + 1,
                    "content": doc[:300] + "..." if len(doc) > 300 else doc,
                    "metadata": metadata,
                    "relevance_score": distances[i] if i < len(distances) else None
                })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "query": query,
                "documents_retrieved": len(documents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": None,
                "sources": []
            }
    
    async def aretrieve_and_answer(
        self, 
        query: str, 
        n_results: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously retrieve relevant documents and generate an answer.
        
        Args:
            query: The question or query text
            n_results: Number of documents to retrieve
            filter_metadata: Optional metadata filter
            
        Returns:
            Dictionary containing the answer and retrieved documents
        """
        try:
            # Search for relevant documents
            search_results = self.vector_store.search(query, n_results, filter_metadata)
            
            if not search_results.get("success"):
                return {
                    "success": False,
                    "error": search_results.get("error", "Search failed"),
                    "answer": None,
                    "sources": []
                }
            
            # Extract documents from search results
            documents = search_results.get("results", {}).get("documents", [[]])[0]
            distances = search_results.get("results", {}).get("distances", [[]])[0]
            metadatas = search_results.get("results", {}).get("metadatas", [[]])[0]
            
            # Create context from retrieved documents
            context = "\n\n".join([f"[Document {i+1}]:\n{doc}" for i, doc in enumerate(documents)])
            
            # Generate answer using RAG
            answer = await self.rag_chain.ainvoke({"context": context, "question": query})
            
            # Prepare sources information
            sources = []
            for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                sources.append({
                    "document_index": i + 1,
                    "content": doc[:300] + "..." if len(doc) > 300 else doc,
                    "metadata": metadata,
                    "relevance_score": distances[i] if i < len(distances) else None
                })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "query": query,
                "documents_retrieved": len(documents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": None,
                "sources": []
            }
    
    def retrieve_similar(self, text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Retrieve documents similar to the given text.
        
        Args:
            text: Text to find similar documents for
            n_results: Number of results to return
            
        Returns:
            Dictionary containing similar documents
        """
        try:
            results = self.vector_store.search(text, n_results)
            
            if not results.get("success"):
                return {
                    "success": False,
                    "error": results.get("error", "Search failed"),
                    "documents": []
                }
            
            documents = results.get("results", {}).get("documents", [[]])[0]
            distances = results.get("results", {}).get("distances", [[]])[0]
            metadatas = results.get("results", {}).get("metadatas", [[]])[0]
            
            similar_docs = []
            for doc, metadata, distance in zip(documents, metadatas, distances):
                similar_docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance  # Convert distance to similarity
                })
            
            return {
                "success": True,
                "documents": similar_docs,
                "query": text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "documents": []
            }


def retrieve_context(query: str, collection_name: str, top_k: int = 5) -> str:
    """
    Retrieve context by embedding the query and querying the ChromaDB collection.
    
    Args:
        query: The query text to search for
        collection_name: Name of the ChromaDB collection to query
        top_k: Number of similar chunks to retrieve (default: 5)
        
    Returns:
        A single string with retrieved chunks joined by "\n---\n" separator
    """
    import chromadb
    from sentence_transformers import SentenceTransformer
    
    # Initialize the embedding model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Get the collection
    collection = client.get_collection(name=collection_name)
    
    # Generate query embedding
    query_embedding = embedding_model.encode([query]).tolist()
    
    # Query the collection for similar chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    # Extract documents from results
    documents = results.get("documents", [[]])[0]
    
    # Join with separator
    context = "\n---\n".join(documents)
    
    return context
