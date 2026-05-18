"""
Vector Store Service
Manages vector embeddings and storage using ChromaDB.
"""

from typing import Dict, Any, List, Optional
import os


class VectorStore:
    """Service for managing vector embeddings using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "legal_documents"):
        """
        Initialize the Vector Store.
        
        Args:
            persist_directory: Directory to persist the vector store
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._chromadb_available = False
        self._sentence_transformers_available = False
        
        try:
            import chromadb
            from chromadb.config import Settings
            self.chromadb = chromadb
            self.Settings = Settings
            self._chromadb_available = True
        except ImportError:
            pass
        
        try:
            from sentence_transformers import SentenceTransformer
            self.SentenceTransformer = SentenceTransformer
            self._sentence_transformers_available = True
        except ImportError:
            pass
        
        self.client = None
        self.collection = None
        self.embedding_model = None
    
    def initialize(self, model_name: str = "all-MiniLM-L6-v2") -> Dict[str, Any]:
        """
        Initialize the vector store and embedding model.
        
        Args:
            model_name: Name of the sentence transformer model
            
        Returns:
            Dictionary with initialization status
        """
        if not self._chromadb_available:
            return {"success": False, "error": "chromadb library is not installed"}
        
        if not self._sentence_transformers_available:
            return {"success": False, "error": "sentence-transformers library is not installed"}
        
        try:
            # Initialize ChromaDB client with persistence
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = self.chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Legal document embeddings"}
            )
            
            # Initialize embedding model
            self.embedding_model = self.SentenceTransformer(model_name)
            
            return {
                "success": True,
                "message": "Vector store initialized successfully",
                "collection_name": self.collection_name,
                "model_name": model_name
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            Dictionary with operation status
        """
        if not self.client or not self.collection or not self.embedding_model:
            return {"success": False, "error": "Vector store not initialized"}
        
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "success": True,
                "documents_added": len(documents),
                "total_documents": self.collection.count()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            Dictionary with search results
        """
        if not self.client or not self.collection or not self.embedding_model:
            return {"success": False, "error": "Vector store not initialized"}
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=filter_metadata
            )
            
            return {
                "success": True,
                "results": results,
                "query": query
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_collection(self) -> Dict[str, Any]:
        """
        Delete the current collection.
        
        Returns:
            Dictionary with operation status
        """
        if not self.client:
            return {"success": False, "error": "Vector store not initialized"}
        
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            
            return {
                "success": True,
                "message": f"Collection '{self.collection_name}' deleted"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents, or 0 if not initialized
        """
        if not self.collection:
            return 0
        
        try:
            return self.collection.count()
        except Exception:
            return 0


def embed_and_store(chunks: list[str], collection_name: str) -> None:
    """
    Embed chunks using sentence-transformers and store them in a ChromaDB collection.
    
    Args:
        chunks: List of text chunks to embed and store
        collection_name: Name of the ChromaDB collection to store in
    """
    import chromadb
    from sentence_transformers import SentenceTransformer
    
    # Initialize the embedding model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Get or create collection
    collection = client.get_or_create_collection(name=collection_name)
    
    # Generate embeddings for all chunks
    embeddings = embedding_model.encode(chunks).tolist()
    
    # Create IDs for each chunk
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    # Add to collection
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=ids
    )


def get_collection(collection_name: str):
    """
    Get an existing ChromaDB collection.
    
    Args:
        collection_name: Name of the collection to retrieve
        
    Returns:
        The ChromaDB collection object
    """
    import chromadb
    
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Get the collection
    collection = client.get_collection(name=collection_name)
    
    return collection
