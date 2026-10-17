from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Document(BaseModel):
    """Document model for ingestion"""
    content: str = Field(..., description="The text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    doc_id: Optional[str] = Field(None, description="Unique document identifier")

class DocumentResponse(BaseModel):
    """Response model for document operations"""
    doc_id: str
    status: str
    message: str

class AddDocumentsRequest(BaseModel):
    """Request model for adding multiple documents"""
    documents: List[Document]
    collection_name: str = Field(default="rag_collection", description="ChromaDB collection name")

class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    question: str = Field(..., description="The question to answer")
    top_k: int = Field(default=3, description="Number of documents to retrieve")
    collection_name: str = Field(default="rag_collection", description="ChromaDB collection name")
    include_sources: bool = Field(default=True, description="Include source documents in response")

class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Session identifier for conversation tracking")
    collection_name: str = Field(default="rag_collection", description="ChromaDB collection name")
    top_k: int = Field(default=3, description="Number of documents to retrieve for context")

class QueryResponse(BaseModel):
    """Response model for queries"""
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_steps: List[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    response: str
    session_id: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_steps: List[str] = Field(default_factory=list)

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
