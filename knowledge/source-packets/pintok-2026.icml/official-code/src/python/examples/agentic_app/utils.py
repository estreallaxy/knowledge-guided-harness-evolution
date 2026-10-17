#!/usr/bin/env python3
"""
Document processing utilities for the RAG application
"""

import os
import re
from typing import List, Dict, Any
from pathlib import Path
import mimetypes

class DocumentProcessor:
    """Utility class for processing documents before adding to vector store"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to find a good breaking point (sentence end)
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + self.chunk_size - 100, start)
                search_text = text[search_start:end]
                
                # Find the last sentence ending
                sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', search_text)]
                if sentence_ends:
                    end = search_start + sentence_ends[-1]
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_text_file(self, file_path: str) -> Dict[str, Any]:
        """Process a text file into chunks with metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = self.chunk_text(content)
            
            base_metadata = {
                'source': os.path.basename(file_path),
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'mime_type': mimetypes.guess_type(file_path)[0] or 'text/plain'
            }
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = base_metadata.copy()
                doc_metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                
                documents.append({
                    'content': chunk,
                    'metadata': doc_metadata
                })
            
            return {
                'documents': documents,
                'success': True,
                'message': f'Processed {len(chunks)} chunks from {file_path}'
            }
            
        except Exception as e:
            return {
                'documents': [],
                'success': False,
                'message': f'Error processing {file_path}: {str(e)}'
            }
    
    def process_directory(self, directory_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """Process all files in a directory"""
        if extensions is None:
            extensions = ['.txt', '.md', '.py', '.js', '.html', '.json']
        
        directory = Path(directory_path)
        if not directory.exists():
            return {
                'documents': [],
                'success': False,
                'message': f'Directory {directory_path} does not exist'
            }
        
        all_documents = []
        processed_files = []
        failed_files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                result = self.process_text_file(str(file_path))
                
                if result['success']:
                    all_documents.extend(result['documents'])
                    processed_files.append(str(file_path))
                else:
                    failed_files.append(str(file_path))
        
        return {
            'documents': all_documents,
            'success': True,
            'message': f'Processed {len(processed_files)} files, {len(failed_files)} failed',
            'processed_files': processed_files,
            'failed_files': failed_files
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        return text.strip()

def create_sample_documents() -> List[Dict[str, Any]]:
    """Create sample documents for testing"""
    return [
        {
            "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. It's designed to be easy to use and learn, with great editor support and automatic API documentation.",
            "metadata": {"source": "fastapi_intro", "topic": "web_framework", "language": "python"}
        },
        {
            "content": "LangGraph is a library for building stateful, multi-actor applications with LLMs. It provides a way to coordinate multiple AI agents and manage complex workflows with state persistence and error handling.",
            "metadata": {"source": "langgraph_intro", "topic": "ai_framework", "language": "python"}
        },
        {
            "content": "ChromaDB is an open-source embedding database that makes it easy to build AI applications with embeddings. It provides a simple interface for storing, querying, and managing vector embeddings with metadata filtering capabilities.",
            "metadata": {"source": "chromadb_intro", "topic": "vector_database", "language": "python"}
        },
        {
            "content": "Ollama is a tool that makes it easy to run large language models locally. It provides a simple API for downloading, running, and interacting with various open-source models like Llama 2, Mistral, and others.",
            "metadata": {"source": "ollama_intro", "topic": "llm_inference", "language": "general"}
        }
    ]

if __name__ == "__main__":
    # Example usage
    processor = DocumentProcessor()
    
    # Create sample documents
    sample_docs = create_sample_documents()
    print(f"Created {len(sample_docs)} sample documents")
    
    # Test text chunking
    long_text = "This is a very long text. " * 100
    chunks = processor.chunk_text(long_text)
    print(f"Split long text into {len(chunks)} chunks")
    
    # Test directory processing (if current directory has files)
    result = processor.process_directory(".", ['.py', '.md', '.txt'])
    print(f"Directory processing result: {result['message']}")
