#!/usr/bin/env python3
"""
TODO: TEST!
Example usage of PgVectorClient for DPDKTokenizer

This example demonstrates how to use the PgVectorClient to:
- Connect to PostgreSQL with pgvector extension
- Create vector tables with metadata
- Add and search vectors
- Perform metadata filtering
- Manage vector data lifecycle

Prerequisites:
- PostgreSQL server running with pgvector extension
- Required Python packages: psycopg2-binary, numpy
"""

import numpy as np
from vectordb_clients.pgvector import PgVectorClient, PgVectorConfig

def main():
    """Example demonstrating pgvector client usage"""
    
    # Configuration for PostgreSQL connection
    config = PgVectorConfig(
        host="localhost",
        port=5432,
        database="vectordb",
        user="postgres",
        password="password",
        schema="public"
    )
    
    # Initialize client
    print("Initializing PgVector client...")
    client = PgVectorClient(config)
    
    try:
        # Test connection
        if not client.is_connected():
            print("Failed to connect to PostgreSQL")
            return
        
        print("Connected to PostgreSQL with pgvector")
        
        # Create a vector table for document embeddings
        table_name = "document_embeddings"
        vector_dimension = 384  # Common dimension for sentence transformers
        
        print(f"\nCreating table '{table_name}' with {vector_dimension}D vectors...")
        
        # Define custom metadata columns
        metadata_columns = {
            "document_type": "TEXT",
            "created_by": "TEXT",
            "priority": "INTEGER"
        }
        
        success = client.create_table(
            table_name=table_name,
            vector_dimension=vector_dimension,
            metadata_columns=metadata_columns,
            index_type="ivfflat",  # Use IVFFlat index for better performance
            index_lists=100
        )
        
        if not success:
            print("Failed to create table")
            return
        
        print("Table created successfully")
        
        # List all tables
        tables = client.list_tables()
        print(f"\nAvailable tables: {tables}")
        
        # Get table information
        table_info = client.get_table_info(table_name)
        if table_info:
            print(f"\nTable info for '{table_name}':")
            print(f"  - Vector dimension: {table_info['vector_dimension']}")
            print(f"  - Row count: {table_info['row_count']}")
            print(f"  - Columns: {len(table_info['columns'])}")
        
        # Generate sample vectors and data
        print("\nAdding sample vectors...")
        
        # Sample document vectors (normally these would come from a sentence transformer)
        sample_vectors = [
            np.random.rand(vector_dimension).tolist(),
            np.random.rand(vector_dimension).tolist(),
            np.random.rand(vector_dimension).tolist(),
            np.random.rand(vector_dimension).tolist(),
            np.random.rand(vector_dimension).tolist()
        ]
        
        sample_contents = [
            "Machine learning models for natural language processing",
            "Deep learning architectures and neural networks",
            "Computer vision and image recognition systems",
            "Reinforcement learning and autonomous agents",
            "Data science and statistical analysis methods"
        ]
        
        sample_metadatas = [
            {"document_type": "research", "created_by": "alice", "priority": 1, "category": "ml"},
            {"document_type": "tutorial", "created_by": "bob", "priority": 2, "category": "dl"},
            {"document_type": "article", "created_by": "charlie", "priority": 1, "category": "cv"},
            {"document_type": "paper", "created_by": "alice", "priority": 3, "category": "rl"},
            {"document_type": "guide", "created_by": "bob", "priority": 2, "category": "ds"}
        ]
        
        sample_ids = [f"doc_{i+1}" for i in range(len(sample_vectors))]
        
        # Add vectors to the table
        success = client.add_vectors(
            table_name=table_name,
            vectors=sample_vectors,
            contents=sample_contents,
            metadatas=sample_metadatas,
            ids=sample_ids
        )
        
        if success:
            print("Vectors added successfully")
        else:
            print("Failed to add vectors")
            return
        
        # Count vectors in the table
        count = client.count_vectors(table_name)
        print(f"\nTotal vectors in table: {count}")
        
        # Search for similar vectors
        print("\nSearching for similar vectors...")
        
        # Use the first vector as query
        query_vector = sample_vectors[0]
        
        # Simple similarity search
        results = client.search_vectors(
            table_name=table_name,
            query_vector=query_vector,
            limit=3,
            distance_metric="cosine"
        )
        
        print(f"Found {len(results)} similar vectors:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. ID: {result['id']}")
            print(f"     Content: {result['content'][:50]}...")
            print(f"     Distance: {result['distance']:.4f}")
            print(f"     Metadata: {result['metadata']}")
            print()
        
        # Search with metadata filtering
        print("Searching with metadata filter (priority = 1)...")
        
        filtered_results = client.search_vectors(
            table_name=table_name,
            query_vector=query_vector,
            limit=5,
            where_filter={"priority": 1},
            distance_metric="cosine"
        )
        
        print(f"Found {len(filtered_results)} vectors with priority = 1:")
        for result in filtered_results:
            print(f"  - {result['id']}: {result['metadata']['category']}")
        
        # Search with complex metadata filtering
        print("\nSearching with complex filter (created_by = 'alice' AND priority >= 1)...")
        
        complex_results = client.search_vectors(
            table_name=table_name,
            query_vector=query_vector,
            limit=5,
            where_filter={
                "created_by": "alice",
                "priority": {"$gte": 1}
            },
            distance_metric="cosine"
        )
        
        print(f"Found {len(complex_results)} vectors matching complex filter:")
        for result in complex_results:
            print(f"  - {result['id']}: {result['metadata']}")
        
        # Get a specific vector by ID
        print("\nRetrieving specific vector...")
        vector_data = client.get_vector(table_name, "doc_1")
        if vector_data:
            print(f"Vector 'doc_1':")
            print(f"  Content: {vector_data['content']}")
            print(f"  Metadata: {vector_data['metadata']}")
            print(f"  Created: {vector_data['created_at']}")
        
        # Update a vector
        print("\nUpdating vector metadata...")
        success = client.update_vector(
            table_name=table_name,
            id="doc_1",
            metadata={"document_type": "updated_research", "created_by": "alice", "priority": 1, "category": "ml", "updated": True}
        )
        
        if success:
            print("Vector updated successfully")
            
            # Verify the update
            updated_vector = client.get_vector(table_name, "doc_1")
            if updated_vector:
                print(f"Updated metadata: {updated_vector['metadata']}")
        
        # Count vectors with specific metadata
        count_priority_1 = client.count_vectors(table_name, {"priority": 1})
        print(f"\nVectors with priority = 1: {count_priority_1}")
        
        count_by_alice = client.count_vectors(table_name, {"created_by": "alice"})
        print(f"Vectors created by Alice: {count_by_alice}")
        
        # Delete a specific vector
        print("\nDeleting vector 'doc_5'...")
        success = client.delete_vector(table_name, "doc_5")
        if success:
            print("Vector deleted successfully")
            
            # Verify deletion
            final_count = client.count_vectors(table_name)
            print(f"Remaining vectors: {final_count}")
        
        # Delete vectors by metadata filter
        print("\nDeleting vectors with priority >= 3...")
        deleted_count = client.delete_vectors(
            table_name=table_name,
            where_filter={"priority": {"$gte": 3}}
        )
        print(f"Deleted {deleted_count} vectors")
        
        # Final count
        final_count = client.count_vectors(table_name)
        print(f"Final vector count: {final_count}")
        
        # Example of batch operations
        print("\nDemonstrating batch operations...")
        
        # Add more vectors in batch
        batch_vectors = [np.random.rand(vector_dimension).tolist() for _ in range(10)]
        batch_contents = [f"Batch document {i+1}" for i in range(10)]
        batch_metadatas = [{"document_type": "batch", "batch_id": i//5, "priority": (i % 3) + 1} for i in range(10)]
        batch_ids = [f"batch_{i+1}" for i in range(10)]
        
        success = client.add_vectors(
            table_name=table_name,
            vectors=batch_vectors,
            contents=batch_contents,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        
        if success:
            print("Batch vectors added successfully")
            
            # Count by batch_id
            batch_0_count = client.count_vectors(table_name, {"batch_id": 0})
            batch_1_count = client.count_vectors(table_name, {"batch_id": 1})
            print(f"Batch 0 vectors: {batch_0_count}")
            print(f"Batch 1 vectors: {batch_1_count}")
            
            # Delete entire batch
            deleted_batch = client.delete_vectors(
                table_name=table_name,
                where_filter={"document_type": "batch"}
            )
            print(f"Deleted {deleted_batch} batch vectors")
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up - optionally delete the test table
        print(f"\nCleaning up...")
        # client.delete_table(table_name)  # Uncomment to delete test table
        client.disconnect()
        print("Disconnected from PostgreSQL")

if __name__ == "__main__":
    main()
