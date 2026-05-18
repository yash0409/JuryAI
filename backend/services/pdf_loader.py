"""
PDF Loader Service
Handles loading and extracting text from PDF documents.
"""

from typing import Dict, Any, List
from pathlib import Path
import io


class PDFLoader:
    """Service for loading and extracting text from PDF documents."""
    
    def __init__(self):
        """Initialize the PDF Loader."""
        self._pypdf_available = False
        try:
            from pypdf import PdfReader
            self.PdfReader = PdfReader
            self._pypdf_available = True
        except ImportError:
            pass
    
    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Load a PDF file and extract its text content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not self._pypdf_available:
            return {
                "success": False,
                "error": "pypdf library is not installed",
                "content": None,
                "metadata": None
            }
        
        try:
            reader = self.PdfReader(file_path)
            text_content = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            
            metadata = {
                "total_pages": len(reader.pages),
                "file_path": file_path,
                "file_name": Path(file_path).name
            }
            
            return {
                "success": True,
                "content": full_text,
                "metadata": metadata,
                "pages": text_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "metadata": None
            }
    
    def load_pdf_from_bytes(self, file_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Load a PDF from bytes data.
        
        Args:
            file_bytes: Raw bytes of the PDF file
            filename: Name of the file (for metadata)
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not self._pypdf_available:
            return {
                "success": False,
                "error": "pypdf library is not installed",
                "content": None,
                "metadata": None
            }
        
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = self.PdfReader(pdf_file)
            text_content = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            
            metadata = {
                "total_pages": len(reader.pages),
                "file_name": filename
            }
            
            return {
                "success": True,
                "content": full_text,
                "metadata": metadata,
                "pages": text_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "metadata": None
            }
    
    def get_page_count(self, file_path: str) -> int:
        """
        Get the number of pages in a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Number of pages, or -1 if error
        """
        if not self._pypdf_available:
            return -1
        
        try:
            reader = self.PdfReader(file_path)
            return len(reader.pages)
        except Exception:
            return -1


def load_and_chunk_pdf(file_path: str) -> list[str]:
    """
    Read a PDF file, extract text page by page, and split into chunks.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of chunk strings, each containing approximately 500 words
        with a 50-word overlap between consecutive chunks
    """
    loader = PDFLoader()
    result = loader.load_pdf(file_path)
    
    if not result.get("success") or not result.get("content"):
        return []
    
    full_text = result["content"]
    return _chunk_text(full_text, chunk_size=500, overlap=50)


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into chunks of approximately chunk_size words with overlap.
    
    Args:
        text: The full text to chunk
        chunk_size: Target number of words per chunk (default: 500)
        overlap: Number of overlapping words between chunks (default: 50)
        
    Returns:
        List of text chunks
    """
    # Split text into words
    words = text.split()
    
    if not words:
        return []
    
    # If the entire text is smaller than chunk_size, return it as a single chunk
    if len(words) <= chunk_size:
        return [" ".join(words)]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        
        # Move start position forward by (chunk_size - overlap)
        start = end - overlap
        
        # If we've reached or passed the end, break
        if start >= len(words):
            break
    
    return chunks
