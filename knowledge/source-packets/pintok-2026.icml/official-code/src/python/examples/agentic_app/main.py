from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import logging
from contextlib import asynccontextmanager

from models import (
    Document, DocumentResponse, AddDocumentsRequest, QueryRequest, 
    ChatRequest, QueryResponse, ChatResponse, HealthResponse, ErrorResponse
)
from config import config
from vector_store import VectorStore
from llm_service import LLMService
from rag_workflow import RAGWorkflow

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
vector_store = None
llm_service = None
rag_workflow = None

# Session storage for chat (in production, use Redis or similar)
chat_sessions: Dict[str, List[Dict[str, Any]]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global vector_store, llm_service, rag_workflow
    
    logger.info("Starting RAG application...")
    
    # Initialize services
    try:
        vector_store = VectorStore()
        llm_service = LLMService()
        rag_workflow = RAGWorkflow(vector_store, llm_service)
        
        # Test connections
        logger.info("Testing service connections...")
        
        # Test Ollama connection
        if not llm_service.test_connection():
            logger.warning("Could not connect to Ollama. Please ensure Ollama is running.")
        
        logger.info("RAG application started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG application...")

app = FastAPI(
    title="RAG Application",
    description="A RAG application using LangGraph, ChromaDB, Ollama, and FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler: {exc}")
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc),
        timestamp=datetime.now()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "vector_store": "healthy" if vector_store else "unavailable",
        "llm_service": "healthy" if llm_service and llm_service.test_connection() else "unavailable",
        "rag_workflow": "healthy" if rag_workflow else "unavailable"
    }
    
    return HealthResponse(
        status="healthy" if all(status == "healthy" for status in services.values()) else "degraded",
        timestamp=datetime.now(),
        services=services
    )

@app.post("/documents", response_model=List[DocumentResponse])
async def add_documents(request: AddDocumentsRequest):
    """Add documents to the vector store"""
    try:
        logger.info(f"Adding {len(request.documents)} documents to collection '{request.collection_name}'")
        
        documents = []
        metadatas = []
        ids = []
        
        for doc in request.documents:
            documents.append(doc.content)
            metadatas.append(doc.metadata)
            if doc.doc_id:
                ids.append(doc.doc_id)
            else:
                import uuid
                ids.append(str(uuid.uuid4()))
        
        added_ids = vector_store.add_documents(
            collection_name=request.collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        if not added_ids:
            raise HTTPException(status_code=500, detail="Failed to add documents")
        
        responses = [
            DocumentResponse(
                doc_id=doc_id,
                status="success",
                message="Document added successfully"
            )
            for doc_id in added_ids
        ]
        
        return responses
        
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{collection_name}")
async def list_documents(collection_name: str):
    """List documents in a collection"""
    try:
        info = vector_store.get_collection_info(collection_name)
        if not info:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return {
            "collection_name": collection_name,
            "document_count": info.get("count", 0),
            "metadata": info.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{collection_name}/{doc_id}")
async def delete_document(collection_name: str, doc_id: str):
    """Delete a document"""
    try:
        success = vector_store.delete_document(collection_name, doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
        
        return {"message": f"Document {doc_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Perform a RAG query"""
    try:
        logger.info(f"Processing RAG query: {request.question}")
        
        result = await rag_workflow.process_query(
            question=request.question,
            collection_name=request.collection_name,
            top_k=request.top_k
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Query processing failed")
        
        sources = []
        if request.include_sources:
            sources = [
                {
                    "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "metadata": doc["metadata"],
                    "distance": doc["distance"],
                    "rank": doc["rank"]
                }
                for doc in result["retrieved_docs"]
            ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            retrieved_docs=result["retrieved_docs"] if request.include_sources else [],
            reasoning_steps=result["reasoning_steps"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the RAG system"""
    try:
        logger.info(f"Processing chat message for session {request.session_id}")
        
        # Get chat history
        chat_history = chat_sessions.get(request.session_id, [])
        
        # Process the message
        result = await rag_workflow.process_chat(
            message=request.message,
            session_id=request.session_id,
            collection_name=request.collection_name,
            top_k=request.top_k,
            chat_history=chat_history
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Chat processing failed")
        
        # Update chat history
        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []
        
        chat_sessions[request.session_id].extend([
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": result["response"], "timestamp": datetime.now().isoformat()}
        ])
        
        # Keep only last 10 exchanges
        if len(chat_sessions[request.session_id]) > 20:
            chat_sessions[request.session_id] = chat_sessions[request.session_id][-20:]
        
        sources = [
            {
                "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                "metadata": doc["metadata"],
                "distance": doc["distance"],
                "rank": doc["rank"]
            }
            for doc in result["retrieved_docs"]
        ]
        
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id,
            sources=sources,
            reasoning_steps=result["reasoning_steps"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Chat with streaming response"""
    async def generate_stream():
        try:
            # This is a simplified streaming implementation
            # In a real implementation, you'd stream from the LLM
            result = await chat(request)
            
            # Simulate streaming by yielding chunks
            words = result.response.split()
            for i, word in enumerate(words):
                chunk = {
                    "content": word + " ",
                    "done": i == len(words) - 1,
                    "metadata": {
                        "session_id": request.session_id,
                        "reasoning_steps": result.reasoning_steps if i == len(words) - 1 else []
                    }
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)  # Small delay for streaming effect
            
        except Exception as e:
            error_chunk = {
                "error": str(e),
                "done": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/collections")
async def list_collections():
    """List all collections"""
    try:
        collections = vector_store.list_collections()
        return {"collections": collections}
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session"""
    try:
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
