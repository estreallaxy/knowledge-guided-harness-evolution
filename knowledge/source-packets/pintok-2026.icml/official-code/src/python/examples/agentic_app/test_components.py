#!/usr/bin/env python3
"""
Comprehensive test of all RAG application features
"""

import asyncio
import json
from vector_store import VectorStore
from llm_service import LLMService
from rag_workflow import RAGWorkflow
from utils import create_sample_documents, DocumentProcessor

async def test_vector_store():
    """Test vector store functionality"""
    print("Testing Vector Store...")
    
    try:
        vs = VectorStore()
        
        # Test collection creation
        success = vs.create_collection("test_collection")
        print(f"Collection creation: {'Success' if success else 'Failed'}")
        
        # Test document addition
        sample_docs = create_sample_documents()
        documents = [doc["content"] for doc in sample_docs]
        metadatas = [doc["metadata"] for doc in sample_docs]
        
        ids = vs.add_documents("test_collection", documents, metadatas)
        print(f"Document addition: {len(ids)} documents added")
        
        # Test querying
        results = vs.query_documents("test_collection", "What is FastAPI?", n_results=2)
        print(f"Document querying: {len(results['documents'])} documents retrieved")
        
        # Test collection info
        info = vs.get_collection_info("test_collection")
        print(f"Collection info: {info.get('count', 0)} documents in collection")
        
        return True
        
    except Exception as e:
        print(f"Vector store test failed: {e}")
        return False

async def test_llm_service():
    """Test LLM service functionality"""
    print("\nTesting LLM Service...")
    
    try:
        llm = LLMService()
        
        # Test connection
        connected = llm.test_connection()
        print(f"Connection test: {'Connected' if connected else 'Failed'}")
        
        if connected:
            # Test RAG chain
            rag_chain = llm.create_rag_chain()
            response = await rag_chain.ainvoke({
                "context": "FastAPI is a modern web framework for Python.",
                "question": "What is FastAPI?"
            })
            print(f"RAG chain test: Response generated ({'OK' if response else 'FAIL'})")
            
            # Test chat chain
            chat_chain = llm.create_chat_chain()
            chat_response = await chat_chain.ainvoke({
                "context": "Python is a programming language.",
                "message": "Tell me about Python",
                "chat_history": ""
            })
            print(f"Chat chain test: Response generated ({'OK' if chat_response else 'FAIL'})")
        
        return connected
        
    except Exception as e:
        print(f"LLM service test failed: {e}")
        return False

async def test_rag_workflow():
    """Test RAG workflow functionality"""
    print("\nTesting RAG Workflow...")
    
    try:
        vs = VectorStore()
        llm = LLMService()
        workflow = RAGWorkflow(vs, llm)
        
        # Test query processing
        result = await workflow.process_query(
            question="What is FastAPI used for?",
            collection_name="test_collection",
            top_k=2
        )
        
        print(f"Query processing: {'Success' if result['success'] else 'Failed'}")
        print(f"   Answer length: {len(result['answer'])} characters")
        print(f"   Retrieved docs: {len(result['retrieved_docs'])}")
        print(f"   Reasoning steps: {len(result['reasoning_steps'])}")
        
        # Test chat processing
        chat_result = await workflow.process_chat(
            message="Hello, can you help me with web development?",
            session_id="test_session",
            collection_name="test_collection"
        )
        
        print(f"Chat processing: {'Success' if chat_result['success'] else 'Failed'}")
        
        return result['success'] and chat_result['success']
        
    except Exception as e:
        print(f"RAG workflow test failed: {e}")
        return False

def test_document_processor():
    """Test document processing utilities"""
    print("\nTesting Document Processor...")
    
    try:
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
        # Test text chunking
        long_text = "This is a test sentence. " * 20
        chunks = processor.chunk_text(long_text)
        print(f"Text chunking: {len(chunks)} chunks created")
        
        # Test text cleaning
        dirty_text = "  This   has\n\nexcessive   whitespace  "
        clean_text = processor.clean_text(dirty_text)
        print(f"Text cleaning: {'Success' if clean_text.strip() else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"Document processor test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("RAG Application Component Tests")
    print("=" * 40)
    
    tests = [
        ("Document Processor", test_document_processor),
        ("Vector Store", test_vector_store),
        ("LLM Service", test_llm_service),
        ("RAG Workflow", test_rag_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All component tests passed!")
        print("\nNext steps:")
        print("1. Run './start.sh' to start the application")
        print("2. Run 'python test_app.py' to test the web API")
        print("3. Visit http://localhost:8080/static/index.html for the web interface")
    else:
        print(f"{total - passed} tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
