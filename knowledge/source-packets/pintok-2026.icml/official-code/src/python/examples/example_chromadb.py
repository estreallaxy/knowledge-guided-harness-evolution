#!/usr/bin/env python3
"""
Example usage of the ChromaDB client for DPDKTokenizer

This script demonstrates how to use the ChromaDB client for:
- Creating collections
- Adding documents
- Querying documents  
- Managing vector embeddings
"""

import sys
import os
from typing import List, Dict, Any

# Add the vectordb package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vectordb_clients.chromadb import ChromaDBClient, ChromaConfig, create_default_client

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
default_ef = DefaultEmbeddingFunction()


def basic_usage_example():
    """Demonstrate basic ChromaDB operations"""
    print("=== Basic ChromaDB Usage Example ===")
    
    # Create client (in-memory for this example)
    client = create_default_client("DPDKTokenizer/my_chroma_data/")
    
    # Check connection
    if not client.health_check():
        print("Failed to connect to ChromaDB")
        return False
    
    print("Connected to ChromaDB")
    
    # Create a collection
    collection_name = "example_documents"
    if client.create_collection(collection_name, metadata={"description": "Example collection"}, embedding_function=default_ef):
        print(f"Created collection: {collection_name}")
    
    # Add some documents
    documents = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is transforming the world",
        "ChromaDB is a powerful vector database",
        "DPDK enables high-performance packet processing",
        "Natural language processing with transformers"
    ]
    
    metadatas = [
        {"category": "animals", "length": len(documents[0])},
        {"category": "technology", "length": len(documents[1])},
        {"category": "database", "length": len(documents[2])},
        {"category": "networking", "length": len(documents[3])},
        {"category": "ai", "length": len(documents[4])}
    ]
    
    if client.add_documents(collection_name, documents, metadatas=metadatas):
        print(f"Added {len(documents)} documents")
    
    # Query documents
    query_results = client.query_documents(
        collection_name,
        query_texts=["machine learning artificial intelligence"],
        n_results=3
    )
    
    if query_results:
        print(f"Query returned {len(query_results['ids'][0])} results")
        for i, (doc, distance) in enumerate(zip(query_results['documents'][0], query_results['distances'][0])):
            print(f"  {i+1}. {doc[:50]}... (distance: {distance:.3f})")
    
    # Get collection info
    info = client.get_collection_info(collection_name)
    if info:
        print(f"Collection info: {info['count']} documents")
    
    # List all collections
    collections = client.list_collections()
    print(f"Collections: {collections}")
    
    return True

def persistent_storage_example():
    """Demonstrate persistent storage"""
    print("\n=== Persistent Storage Example ===")
    
    # Create persistent client
    persist_dir = "./chroma_db"
    config = ChromaConfig(
        is_persistent=True,
        persist_directory=persist_dir
    )
    client = ChromaDBClient(config)
    
    collection_name = "persistent_docs"
    
    # Create collection if it doesn't exist
    client.create_collection(collection_name)
    
    # Add documents with custom IDs
    documents = [
        "This document will persist across sessions",
        "Vector databases enable semantic search",
        "Embeddings capture semantic meaning"
    ]
    
    ids = ["doc_1", "doc_2", "doc_3"]
    
    client.add_documents(collection_name, documents, ids=ids)
    print(f"Added documents to persistent storage: {persist_dir}")
    
    # Query the persistent collection
    results = client.get_documents(collection_name)
    if results:
        print(f"Retrieved {len(results['ids'])} documents from persistent storage")
    
    client.disconnect()
    return True

def metadata_filtering_example():
    """Demonstrate metadata filtering capabilities"""
    print("\n=== Metadata Filtering Example ===")
    
    client = create_default_client()
    collection_name = "filtered_docs"
    
    # Create collection
    client.create_collection(collection_name)
    
    # Add documents with rich metadata
    documents = [
        "Python programming tutorial",
        "Java development guide", 
        "C++ performance optimization",
        "JavaScript web development",
        "Rust systems programming"
    ]
    
    metadatas = [
        {"language": "python", "difficulty": "beginner", "year": 2023},
        {"language": "java", "difficulty": "intermediate", "year": 2022},
        {"language": "cpp", "difficulty": "advanced", "year": 2023},
        {"language": "javascript", "difficulty": "beginner", "year": 2023},
        {"language": "rust", "difficulty": "advanced", "year": 2022}
    ]
    
    client.add_documents(collection_name, documents, metadatas=metadatas)
    
    # Query with metadata filters
    print("Querying for beginner-level documents from 2023:")
    results = client.query_documents(
        collection_name,
        query_texts=["programming tutorial"],
        where={"$and": [{"difficulty": "beginner"}, {"year": 2023}]},
        n_results=5
    )
    
    if results:
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            print(f"  - {doc} ({metadata})")
    
    # Get documents with specific criteria
    print("\nGetting all advanced-level documents:")
    results = client.get_documents(
        collection_name,
        where={"difficulty": "advanced"},
        include=["documents", "metadatas"]
    )
    
    if results:
        for doc, metadata in zip(results['documents'], results['metadatas']):
            print(f"  - {doc} ({metadata})")
    
    return True

def update_and_delete_example():
    """Demonstrate update and delete operations"""
    print("\n=== Update and Delete Example ===")
    
    client = create_default_client()
    collection_name = "mutable_docs"
    
    # Create collection
    client.create_collection(collection_name)
    
    # Add initial documents
    documents = ["Original document 1", "Original document 2"]
    ids = ["doc1", "doc2"]
    metadatas = [{"version": 1}, {"version": 1}]
    
    client.add_documents(collection_name, documents, metadatas=metadatas, ids=ids)
    print("Added initial documents")
    
    # Update documents
    updated_docs = ["Updated document 1", "Updated document 2"]
    updated_metadata = [{"version": 2}, {"version": 2}]
    
    if client.update_documents(collection_name, ids, documents=updated_docs, metadatas=updated_metadata):
        print("Updated documents")
    
    # Verify updates
    results = client.get_documents(collection_name, ids=ids)
    if results:
        print("Updated documents:")
        for doc, metadata in zip(results['documents'], results['metadatas']):
            print(f"  - {doc} (version: {metadata['version']})")
    
    # Delete one document
    if client.delete_documents(collection_name, ["doc1"]):
        print("Deleted document 1")
    
    # Verify deletion
    remaining = client.get_documents(collection_name)
    if remaining:
        print(f"Remaining documents: {len(remaining['ids'])}")
    
    return True

def error_handling_example():
    """Demonstrate error handling"""
    print("\n=== Error Handling Example ===")
    
    client = create_default_client()
    
    # Try to get non-existent collection
    result = client.get_collection("nonexistent_collection")
    print(f"Non-existent collection handling: {result is None}")
    
    # Try to query non-existent collection
    result = client.query_documents("nonexistent", query_texts=["test"])
    print(f"Query non-existent collection: {result is None}")
    
    # Try invalid operations
    collection_name = "error_test"
    client.create_collection(collection_name)
    
    # Try to add documents with mismatched metadata length
    result = client.add_documents(
        collection_name,
        documents=["doc1", "doc2"],
        metadatas=[{"key": "value"}]  # Wrong length
    )
    print(f"Mismatched metadata length handling: {not result}")
    
    return True

def main():
    """Run all examples"""
    print("ChromaDB Client Examples")
    print("=" * 50)
    
    try:
        # Run examples
        basic_usage_example()
        #persistent_storage_example()
        #metadata_filtering_example()
        #update_and_delete_example()
        #error_handling_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
