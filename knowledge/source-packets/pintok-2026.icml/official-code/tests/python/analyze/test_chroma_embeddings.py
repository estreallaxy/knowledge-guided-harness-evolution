#!/usr/bin/env python3
"""
Test suite for custom ChromaDB embedding functions using BERTEncoder.

This test suite verifies that the custom embedding functions work correctly
and are compatible with ChromaDB.
"""

import sys
import os
import tempfile
import shutil

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src/python'))

try:
    import chromadb
    from utils.chroma_embeddings import (
        BERTEmbeddingFunction,
        TinyBERTEmbeddingFunction,
        create_bert_embedding_function,
        get_tinybert_embedding_function
    )
    import numpy as np
    
    class TestBERTEmbeddingFunctions:
        """Test suite for BERT embedding functions"""
        
        def __init__(self):
            self.temp_dir = None
            
        def setup(self):
            """Set up test environment"""
            self.temp_dir = tempfile.mkdtemp()
            print(f"Using temporary directory: {self.temp_dir}")
            
        def teardown(self):
            """Clean up test environment"""
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                
        def test_embedding_function_initialization(self):
            """Test that embedding functions can be initialized"""
            print("Testing embedding function initialization...")
            
            # Test basic initialization
            embed_fn = BERTEmbeddingFunction(
                encoder_type="tinybert",
                force_cpu=True,
                auto_initialize=False  # Don't auto-initialize to speed up test
            )
            assert embed_fn.encoder_type == "tinybert"
            assert embed_fn.force_cpu is True
            assert embed_fn.bert_encoder is None  # Not initialized yet
            
            print("Embedding function initialization test passed")
            
        def test_embedding_generation(self):
            """Test that embeddings can be generated"""
            print("Testing embedding generation...")
            
            embed_fn = TinyBERTEmbeddingFunction(force_cpu=True)
            
            # Test single text
            single_text = "This is a test sentence."
            single_embedding = embed_fn([single_text])
            
            assert len(single_embedding) == 1
            assert isinstance(single_embedding[0], list)
            assert len(single_embedding[0]) > 0  # Should have some dimensions
            
            # Test batch of texts
            batch_texts = [
                "First test sentence.",
                "Second test sentence.",
                "Third test sentence."
            ]
            batch_embeddings = embed_fn(batch_texts)
            
            assert len(batch_embeddings) == 3
            assert all(isinstance(emb, list) for emb in batch_embeddings)
            assert all(len(emb) == len(batch_embeddings[0]) for emb in batch_embeddings)  # Same dimensions
            
            print("Embedding generation test passed")
            
        def test_chromadb_integration(self):
            """Test integration with ChromaDB"""
            print("Testing ChromaDB integration...")
            
            # Create ChromaDB client
            client = chromadb.Client()
            
            # Create embedding function
            embed_fn = get_tinybert_embedding_function(force_cpu=True)
            
            # Create collection
            collection = client.create_collection(
                name="test_integration",
                embedding_function=embed_fn
            )
            
            # Add documents
            documents = [
                "Natural language processing is fascinating.",
                "Machine learning requires good data.",
                "Vector databases enable similarity search."
            ]
            ids = ["doc1", "doc2", "doc3"]
            
            collection.add(
                documents=documents,
                ids=ids
            )
            
            # Verify documents were added
            all_docs = collection.get()
            assert len(all_docs['ids']) == 3
            assert set(all_docs['ids']) == set(ids)
            
            # Test querying
            results = collection.query(
                query_texts=["What is machine learning?"],
                n_results=2
            )
            
            assert len(results['ids'][0]) == 2
            assert len(results['documents'][0]) == 2
            assert len(results['distances'][0]) == 2
            
            print("ChromaDB integration test passed")
            
        def test_pooling_strategies(self):
            """Test different pooling strategies"""
            print("Testing different pooling strategies...")
            
            test_text = "This is a test sentence for pooling."
            
            # Test different pooling strategies
            strategies = ["mean", "cls", "max"]
            embeddings = {}
            
            for strategy in strategies:
                embed_fn = create_bert_embedding_function(
                    encoder_type="tinybert",
                    force_cpu=True,
                    pooling_strategy=strategy
                )
                
                embedding = embed_fn([test_text])
                embeddings[strategy] = embedding[0]
                
                assert len(embedding) == 1
                assert len(embedding[0]) > 0
                
            # Verify that different strategies produce different embeddings
            # (they should be different unless by coincidence)
            mean_emb = np.array(embeddings["mean"])
            cls_emb = np.array(embeddings["cls"])
            max_emb = np.array(embeddings["max"])
            
            # Check that embeddings are not identical (very unlikely to be identical)
            assert not np.allclose(mean_emb, cls_emb, atol=1e-6)
            assert not np.allclose(mean_emb, max_emb, atol=1e-6)
            assert not np.allclose(cls_emb, max_emb, atol=1e-6)
            
            print("Pooling strategies test passed")
            
        def test_consistency(self):
            """Test that same input produces same output"""
            print("Testing embedding consistency...")
            
            embed_fn = TinyBERTEmbeddingFunction(force_cpu=True)
            
            test_text = "This is a consistency test."
            
            # Generate embedding twice
            embedding1 = embed_fn([test_text])
            embedding2 = embed_fn([test_text])
            
            # Should be identical (or very close due to floating point precision)
            emb1_array = np.array(embedding1[0])
            emb2_array = np.array(embedding2[0])
            
            assert np.allclose(emb1_array, emb2_array, atol=1e-6)
            
            print("Embedding consistency test passed")
            
        def run_all_tests(self):
            """Run all tests"""
            print("Running BERT Embedding Functions Test Suite")
            print("=" * 50)
            
            try:
                self.setup()
                
                self.test_embedding_function_initialization()
                self.test_embedding_generation()
                self.test_chromadb_integration()
                self.test_pooling_strategies()
                self.test_consistency()
                
                print("\n" + "=" * 50)
                print("All tests passed successfully!")
                print("=" * 50)
                
            except Exception as e:
                print(f"Test failed: {e}")
                import traceback
                traceback.print_exc()
                
            finally:
                self.teardown()
                
    def main():
        """Run the test suite"""
        test_suite = TestBERTEmbeddingFunctions()
        test_suite.run_all_tests()
        
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure ChromaDB and required dependencies are installed:")
    print("pip install chromadb transformers torch numpy")
    print("Also ensure you're running from the correct directory with the utils package.")
