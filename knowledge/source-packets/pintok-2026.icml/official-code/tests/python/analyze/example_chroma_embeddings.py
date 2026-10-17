#!/usr/bin/env python3
"""
Example usage of custom ChromaDB embedding functions with BERTEncoder.

This example shows how to use the custom ChromaDB embedding functions
that leverage the BERTEncoder from the tokenization comparison system.
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import chromadb
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src/python'))
    from utils.chroma_embeddings import (
        BERTEmbeddingFunction,
        TinyBERTEmbeddingFunction,
        CustomBERTEmbeddingFunction,
        create_bert_embedding_function,
        get_tinybert_embedding_function,
        get_custom_bert_embedding_function
    )
    
    def example_basic_usage():
        """Basic example using TinyBERT embedding function"""
        print("=== Basic Usage Example ===")
        
        # Create ChromaDB client
        client = chromadb.Client()
        
        # Create embedding function using our custom BERTEncoder
        embedding_fn = get_tinybert_embedding_function(force_cpu=True)
        
        # Create collection with custom embedding function
        collection = client.create_collection(
            name="test_collection",
            embedding_function=embedding_fn
        )
        
        # Add some documents
        documents = [
            "This is a document about natural language processing.",
            "Machine learning models require careful tokenization.",
            "BERT embeddings provide rich semantic representations.",
            "Vector databases enable efficient similarity search."
        ]
        
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        print("Adding documents to ChromaDB...")
        collection.add(
            documents=documents,
            ids=ids
        )
        
        # Query the collection
        query_text = "How do machine learning models work?"
        print(f"\nQuerying: '{query_text}'")
        
        results = collection.query(
            query_texts=[query_text],
            n_results=2
        )
        
        print("Top 2 similar documents:")
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            print(f"  {i+1}. {doc} (distance: {distance:.4f})")
        
        print("Basic usage example completed!")
        
    def example_custom_model():
        """Example using a custom BERT model"""
        print("\n=== Custom Model Example ===")
        
        # Create ChromaDB client
        client = chromadb.Client()
        
        # Create custom embedding function with specific model
        # Note: Using TinyBERT as the actual model for this example
        embedding_fn = CustomBERTEmbeddingFunction(
            model_name="huawei-noah/TinyBERT_General_4L_312D",
            force_cpu=True,
            pooling_strategy="mean"
        )
        
        # Create collection
        collection = client.create_collection(
            name="custom_model_collection",
            embedding_function=embedding_fn
        )
        
        # Add documents
        documents = [
            "DPDK provides high-performance packet processing.",
            "Tokenization is crucial for NLP applications.",
            "ChromaDB enables vector similarity search."
        ]
        
        collection.add(
            documents=documents,
            ids=["dpdk_doc", "nlp_doc", "chroma_doc"]
        )
        
        # Query
        results = collection.query(
            query_texts=["What is high-performance computing?"],
            n_results=1
        )
        
        print(f"Most similar document: {results['documents'][0][0]}")
        print("Custom model example completed!")
        
    def example_factory_function():
        """Example using the factory function"""
        print("\n=== Factory Function Example ===")
        
        # Create embedding function using factory
        embedding_fn = create_bert_embedding_function(
            encoder_type="tinybert",
            force_cpu=True,
            pooling_strategy="cls"  # Use CLS token pooling
        )
        
        # Test the embedding function directly
        test_texts = [
            "Hello world!",
            "This is a test document.",
            "Another example text for embeddings."
        ]
        
        print("Generating embeddings for test texts...")
        embeddings = embedding_fn(test_texts)
        
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Each embedding has {len(embeddings[0])} dimensions")
        print(f"First embedding sample: {embeddings[0][:5]}...")  # Show first 5 values
        
        print("Factory function example completed!")
        
    def example_batch_processing():
        """Example showing batch processing capabilities"""
        print("\n=== Batch Processing Example ===")
        
        # Create embedding function
        embedding_fn = BERTEmbeddingFunction(
            encoder_type="tinybert",
            force_cpu=True,
            pooling_strategy="mean",
            auto_initialize=True
        )
        
        # Large batch of texts to demonstrate batch processing
        large_batch = [
            f"This is document number {i} about various topics in NLP and machine learning."
            for i in range(20)
        ]
        
        print(f"Processing batch of {len(large_batch)} documents...")
        
        import time
        start_time = time.time()
        batch_embeddings = embedding_fn(large_batch)
        end_time = time.time()
        
        print(f"Processed {len(batch_embeddings)} embeddings in {end_time - start_time:.3f} seconds")
        print(f"Average time per document: {(end_time - start_time) / len(large_batch):.4f} seconds")
        
        print("Batch processing example completed!")
        
    def main():
        """Run all examples"""
        print("ChromaDB Custom Embedding Functions Example")
        print("=" * 50)
        
        try:
            example_basic_usage()
            example_custom_model()
            example_factory_function()
            example_batch_processing()
            
            print(f"\n{'='*50}")
            print("All examples completed successfully!")
            print(f"{'='*50}")
            
        except Exception as e:
            print(f"Error running examples: {e}")
            import traceback
            traceback.print_exc()
            
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure ChromaDB and required dependencies are installed:")
    print("pip install chromadb transformers torch")
    print("Also ensure you're running from the correct directory with the utils package.")
