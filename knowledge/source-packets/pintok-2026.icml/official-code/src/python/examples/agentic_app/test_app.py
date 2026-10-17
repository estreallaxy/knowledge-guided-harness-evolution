#!/usr/bin/env python3
"""
Example script to test the RAG application
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("Health check passed")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def add_sample_documents():
    """Add sample documents to test the system"""
    print("\nAdding sample documents...")
    
    sample_docs = [
        {
            "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. Some of the activities computers with artificial intelligence are designed for include speech recognition, learning, planning, and problem solving.",
            "metadata": {"source": "ai_intro.txt", "topic": "artificial_intelligence"}
        },
        {
            "content": "Machine Learning is a subset of artificial intelligence (AI) that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.",
            "metadata": {"source": "ml_intro.txt", "topic": "machine_learning"}
        },
        {
            "content": "Deep Learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised. Deep learning architectures such as deep neural networks, deep belief networks, and recurrent neural networks have been applied to fields including computer vision, speech recognition, natural language processing, and audio recognition.",
            "metadata": {"source": "dl_intro.txt", "topic": "deep_learning"}
        },
        {
            "content": "Natural Language Processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.",
            "metadata": {"source": "nlp_intro.txt", "topic": "natural_language_processing"}
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/documents",
            json={
                "documents": sample_docs,
                "collection_name": "test_collection"
            }
        )
        response.raise_for_status()
        print("Sample documents added successfully")
        print(f"Added {len(sample_docs)} documents")
        return True
    except Exception as e:
        print(f"Failed to add documents: {e}")
        return False

def test_query():
    """Test the RAG query endpoint"""
    print("\nTesting RAG query...")
    
    query = "What is the difference between machine learning and deep learning?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={
                "question": query,
                "top_k": 3,
                "collection_name": "test_collection",
                "include_sources": True
            }
        )
        response.raise_for_status()
        result = response.json()
        
        print("Query successful")
        print(f"Question: {query}")
        print(f"Answer: {result['answer']}")
        print(f"Sources: {len(result['sources'])} documents retrieved")
        print(f"Reasoning steps: {len(result['reasoning_steps'])}")
        
        return True
    except Exception as e:
        print(f"Query failed: {e}")
        return False

def test_chat():
    """Test the chat endpoint"""
    print("\nTesting chat functionality...")
    
    session_id = "test_session_123"
    messages = [
        "Hello! Can you tell me about artificial intelligence?",
        "What are some applications of machine learning?",
        "How does deep learning differ from traditional machine learning?"
    ]
    
    try:
        for i, message in enumerate(messages):
            print(f"\nUser: {message}")
            
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "message": message,
                    "session_id": session_id,
                    "collection_name": "test_collection",
                    "top_k": 2
                }
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"Assistant: {result['response']}")
            print(f"Sources used: {len(result['sources'])}")
            
            time.sleep(1)  # Small delay between messages
        
        print("Chat test completed successfully")
        return True
        
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

def test_collections():
    """Test collection management"""
    print("\nTesting collection management...")
    
    try:
        # List collections
        response = requests.get(f"{BASE_URL}/collections")
        response.raise_for_status()
        collections = response.json()
        
        print(f"Collections retrieved: {collections['collections']}")
        
        # Get collection info
        if "test_collection" in collections["collections"]:
            response = requests.get(f"{BASE_URL}/documents/test_collection")
            response.raise_for_status()
            info = response.json()
            
            print(f"Collection info: {info['document_count']} documents")
        
        return True
        
    except Exception as e:
        print(f"Collection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("RAG Application Test Suite")
    print("=" * 40)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            break
        except:
            if i == 29:
                print("Server is not responding. Make sure the application is running.")
                return
            time.sleep(1)
    
    tests = [
        test_health,
        add_sample_documents,
        test_collections,
        test_query,
        test_chat
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Your RAG application is working correctly.")
    else:
        print(f"{total - passed} tests failed. Check the output above for details.")
    
    print("\nNext Steps:")
    print("- Visit http://localhost:8080/docs for interactive API documentation")
    print("- Try the endpoints with your own data")
    print("- Customize the configuration in config.py")

if __name__ == "__main__":
    main()
