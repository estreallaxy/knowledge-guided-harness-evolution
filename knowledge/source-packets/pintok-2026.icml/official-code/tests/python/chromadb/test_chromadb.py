#!/usr/bin/env python3
"""
Test suite for ChromaDB client

This test suite covers all functionality of the ChromaDB client including:
- Connection management
- Collection operations
- Document operations
- Error handling
- Metadata filtering
"""

import pytest
import tempfile
import shutil
import os
import sys
from typing import List, Dict, Any

# Add the src/python directory to Python path for imports (prioritize over test directory)
src_python_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src', 'python')
src_python_path = os.path.abspath(src_python_path)
# Remove any existing path to avoid conflicts
if src_python_path in sys.path:
    sys.path.remove(src_python_path)
# Insert at the beginning to prioritize over test directory
sys.path.insert(0, src_python_path)

try:
    from vectordb_clients.chromadb import ChromaDBClient, ChromaConfig, create_default_client
    from chromadb.utils import embedding_functions
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback import for testing
    from vectordb_clients.chromadb.client import ChromaDBClient, ChromaConfig, create_default_client
    from chromadb.utils import embedding_functions

class TestChromaDBClient:
    """Test suite for ChromaDB client functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        # Force in-memory client by setting host to None
        config = ChromaConfig(
            host=None,
            port=None,
            is_persistent=False
        )
        client = ChromaDBClient(config)
        # Set up default embedding function for tests
        client._default_embedding_function = embedding_functions.DefaultEmbeddingFunction()
        yield client
        if client:
            client.disconnect()
    
    @pytest.fixture
    def persistent_client(self):
        """Create a persistent test client"""
        temp_dir = tempfile.mkdtemp()
        config = ChromaConfig(
            is_persistent=True,
            persist_directory=temp_dir
        )
        client = ChromaDBClient(config)
        yield client
        client.disconnect()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_client_initialization(self):
        """Test client initialization and connection"""
        # Test in-memory client
        config = ChromaConfig(
            host=None,
            port=None,
            is_persistent=False
        )
        client = ChromaDBClient(config)
        assert client is not None
        assert client.health_check() is True
        client.disconnect()
        
        # Test persistent client
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ChromaConfig(
                is_persistent=True,
                persist_directory=temp_dir
            )
            client = ChromaDBClient(config)
            assert client is not None
            assert client.health_check() is True
            client.disconnect()
    
    def test_collection_operations(self, client):
        """Test collection create, list, delete operations"""
        collection_name = "test_collection"
        
        # Test collection creation
        assert client.create_collection(collection_name) is True
        
        # Test listing collections
        collections = client.list_collections()
        assert collection_name in collections
        
        # Test getting collection
        collection = client.get_collection(collection_name)
        assert collection is not None
        
        # Test collection info
        info = client.get_collection_info(collection_name)
        assert info is not None
        assert info["name"] == collection_name
        assert info["count"] == 0
        
        # Test collection deletion
        assert client.delete_collection(collection_name) is True
        collections = client.list_collections()
        assert collection_name not in collections
    
    def test_document_operations(self, client):
        """Test document add, query, update, delete operations"""
        collection_name = "test_docs"
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        client.create_collection(collection_name, embedding_function=embedding_fn)
        
        # Test adding documents
        documents = [
            "First test document",
            "Second test document", 
            "Third test document"
        ]
        metadatas = [
            {"category": "test", "id": 1},
            {"category": "test", "id": 2},
            {"category": "example", "id": 3}
        ]
        ids = ["doc1", "doc2", "doc3"]
        
        assert client.add_documents(
            collection_name, 
            documents, 
            metadatas=metadatas, 
            ids=ids
        ) is True
        
        # Test getting documents
        results = client.get_documents(collection_name)
        assert results is not None
        assert len(results["ids"]) == 3
        
        # Test getting specific documents
        results = client.get_documents(collection_name, ids=["doc1", "doc2"])
        assert results is not None
        assert len(results["ids"]) == 2
        
        # Test querying documents
        query_results = client.query_documents(
            collection_name,
            query_texts=["test document"],
            n_results=2
        )
        assert query_results is not None
        assert len(query_results["ids"][0]) <= 2
        
        # Test updating documents
        updated_docs = ["Updated first document"]
        updated_metadata = [{"category": "updated", "id": 1}]
        assert client.update_documents(
            collection_name,
            ["doc1"],
            documents=updated_docs,
            metadatas=updated_metadata
        ) is True
        
        # Verify update
        results = client.get_documents(collection_name, ids=["doc1"])
        assert "Updated" in results["documents"][0]
        assert results["metadatas"][0]["category"] == "updated"
        
        # Test deleting documents
        assert client.delete_documents(collection_name, ["doc1"]) is True
        
        # Verify deletion
        results = client.get_documents(collection_name)
        assert len(results["ids"]) == 2
        assert "doc1" not in results["ids"]
    
    def test_metadata_filtering(self, client):
        """Test metadata filtering functionality"""
        collection_name = "filtered_collection"
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        client.create_collection(collection_name, embedding_function=embedding_fn)
        
        # Add documents with metadata
        documents = [
            "Python programming",
            "Java development",
            "Python scripting",
            "Java enterprise"
        ]
        metadatas = [
            {"language": "python", "difficulty": "beginner"},
            {"language": "java", "difficulty": "intermediate"},
            {"language": "python", "difficulty": "advanced"},
            {"language": "java", "difficulty": "beginner"}
        ]
        
        client.add_documents(collection_name, documents, metadatas=metadatas)
        
        # Test filtering by single metadata field
        results = client.get_documents(
            collection_name,
            where={"language": "python"}
        )
        assert len(results["ids"]) == 2
        
        # Test filtering by multiple metadata fields
        results = client.get_documents(
            collection_name,
            where={"$and": [{"language": "java"}, {"difficulty": "beginner"}]}
        )
        assert len(results["ids"]) == 1
        
        # Test query with metadata filter
        query_results = client.query_documents(
            collection_name,
            query_texts=["programming"],
            where={"language": "python"},
            n_results=5
        )
        assert len(query_results["ids"][0]) == 2
    
    def test_error_handling(self, client):
        """Test error handling scenarios"""
        # Test operations on non-existent collection
        assert client.get_collection("nonexistent") is None
        assert client.query_documents("nonexistent", query_texts=["test"]) is None
        assert client.get_collection_info("nonexistent") is None
        
        # Create a test collection for error testing
        collection_name = "error_test"
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        client.create_collection(collection_name, embedding_function=embedding_fn)
        
        # Test invalid parameters
        assert client.add_documents(
            collection_name,
            documents=["doc1", "doc2"],
            metadatas=[{"key": "value"}]  # Wrong length
        ) is False
        
        # Test that empty documents should fail (ChromaDB requires non-empty lists)
        assert client.add_documents(
            collection_name,
            documents=[],  # Empty documents
            metadatas=[]
        ) is False  # Should fail with empty lists
        
        # Test invalid query parameters
        results = client.query_documents(
            collection_name,
            query_texts=None,
            query_embeddings=None
        )
        # ChromaDB should handle this gracefully
        
        # Test operations without connection
        client.disconnect()
        assert client.health_check() is False
    
    def test_persistent_storage(self, persistent_client):
        """Test persistent storage functionality"""
        collection_name = "persistent_test"
        
        # Create collection and add documents
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        persistent_client.create_collection(collection_name, embedding_function=embedding_fn)
        documents = ["Persistent document 1", "Persistent document 2"]
        ids = ["persist1", "persist2"]
        
        assert persistent_client.add_documents(
            collection_name, 
            documents, 
            ids=ids
        ) is True
        
        # Verify documents were added
        results = persistent_client.get_documents(collection_name)
        assert len(results["ids"]) == 2
        
        # Test collection info
        info = persistent_client.get_collection_info(collection_name)
        assert info["count"] == 2
    
    def test_advanced_queries(self, client):
        """Test advanced query functionality"""
        collection_name = "advanced_queries"
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        client.create_collection(collection_name, embedding_function=embedding_fn)
        
        # Add documents with rich metadata
        documents = [
            "Machine learning fundamentals",
            "Deep learning with neural networks",
            "Natural language processing",
            "Computer vision applications",
            "Reinforcement learning algorithms"
        ]
        
        metadatas = [
            {"topic": "ml", "difficulty": 1, "year": 2023},
            {"topic": "dl", "difficulty": 3, "year": 2022},
            {"topic": "nlp", "difficulty": 2, "year": 2023},
            {"topic": "cv", "difficulty": 2, "year": 2022},
            {"topic": "rl", "difficulty": 4, "year": 2023}
        ]
        
        client.add_documents(collection_name, documents, metadatas=metadatas)
        
        # Test complex metadata queries
        results = client.get_documents(
            collection_name,
            where={
                "$and": [
                    {"year": 2023},
                    {"difficulty": {"$lte": 2}}
                ]
            }
        )
        assert len(results["ids"]) == 2  # ml and nlp documents
        
        # Test limit and offset
        results = client.get_documents(
            collection_name,
            limit=2,
            offset=1
        )
        assert len(results["ids"]) == 2
        
        # Test include parameters
        results = client.get_documents(
            collection_name,
            include=["documents"]
        )
        assert "documents" in results
        # Note: ChromaDB may still return other fields with None values even when not requested
        # This is expected behavior
    
    def test_collection_metadata(self, client):
        """Test collection metadata functionality"""
        collection_name = "metadata_test"
        collection_metadata = {
            "description": "Test collection with metadata",
            "version": "1.0",
            "created_by": "test_suite"
        }
        
        # Create collection with metadata
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        assert client.create_collection(
            collection_name, 
            metadata=collection_metadata,
            embedding_function=embedding_fn
        ) is True
        
        # Verify collection metadata
        info = client.get_collection_info(collection_name)
        assert info["metadata"] == collection_metadata
    
    def test_large_batch_operations(self, client):
        """Test operations with larger batches of documents"""
        collection_name = "batch_test"
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        client.create_collection(collection_name, embedding_function=embedding_fn)
        
        # Create a larger batch of documents
        batch_size = 100
        documents = [f"Document number {i}" for i in range(batch_size)]
        metadatas = [{"index": i, "batch": "test"} for i in range(batch_size)]
        ids = [f"doc_{i}" for i in range(batch_size)]
        
        # Test batch addition
        assert client.add_documents(
            collection_name,
            documents,
            metadatas=metadatas,
            ids=ids
        ) is True
        
        # Verify all documents were added
        results = client.get_documents(collection_name)
        assert len(results["ids"]) == batch_size
        
        # Test batch query
        query_results = client.query_documents(
            collection_name,
            query_texts=["Document number"],
            n_results=10
        )
        assert len(query_results["ids"][0]) == 10
        
        # Test batch deletion
        delete_ids = [f"doc_{i}" for i in range(0, 10)]
        assert client.delete_documents(collection_name, delete_ids) is True
        
        # Verify deletion
        results = client.get_documents(collection_name)
        assert len(results["ids"]) == batch_size - 10

def test_config_variations():
    """Test different configuration options"""
    # Test default config
    config = ChromaConfig()
    assert config.host == "localhost"
    assert config.port == 8000
    assert config.is_persistent is False
    
    # Test custom config
    config = ChromaConfig(
        host="custom.host",
        port=9000,
        is_persistent=True,
        persist_directory="/tmp/test",
        auth_token="test_token",
        ssl=True
    )
    assert config.host == "custom.host"
    assert config.port == 9000
    assert config.is_persistent is True
    assert config.auth_token == "test_token"
    assert config.ssl is True

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
