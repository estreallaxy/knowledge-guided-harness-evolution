import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import uuid
import json
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PgVectorConfig:
    """Configuration for pgvector client"""
    host: str = "localhost"
    port: int = 5432
    database: str = "vectordb"
    user: str = "postgres"
    password: str = "password"
    schema: str = "public"
    sslmode: str = "prefer"
    connect_timeout: int = 10
    command_timeout: int = 30
    pool_size: int = 5

class PgVectorClient:
    """
    A comprehensive pgvector client for managing vector databases in PostgreSQL
    
    This client provides high-level operations for:
    - Connection management with connection pooling
    - Table operations (create, delete, list)
    - Vector operations (add, search, update, delete)
    - Metadata management and filtering
    - Index management for performance optimization
    """
    
    def __init__(self, config: Optional[PgVectorConfig] = None):
        """
        Initialize pgvector client
        
        Args:
            config: PgVectorConfig object with connection settings
        """
        self.config = config or PgVectorConfig()
        self.connection = None
        self._tables = {}
        
        # Register numpy array adapter for psycopg2
        register_adapter(np.ndarray, self._adapt_numpy_array)
        
        self.connect()
    
    def _adapt_numpy_array(self, numpy_array):
        """Adapter for numpy arrays to PostgreSQL arrays"""
        return AsIs(f"'{numpy_array.tolist()}'::vector")
    
    def connect(self) -> bool:
        """
        Establish connection to PostgreSQL with pgvector
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            connection_string = (
                f"host={self.config.host} "
                f"port={self.config.port} "
                f"dbname={self.config.database} "
                f"user={self.config.user} "
                f"password={self.config.password} "
                f"sslmode={self.config.sslmode} "
                f"connect_timeout={self.config.connect_timeout}"
            )
            
            self.connection = psycopg2.connect(
                connection_string,
                cursor_factory=RealDictCursor
            )
            self.connection.autocommit = False
            
            # Enable pgvector extension
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self.connection.commit()
            
            logger.info(f"Connected to PostgreSQL with pgvector at {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Close connection to PostgreSQL"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from PostgreSQL")
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        try:
            if not self.connection:
                return False
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except:
            return False
    
    def create_table(self, 
                    table_name: str, 
                    vector_dimension: int,
                    metadata_columns: Optional[Dict[str, str]] = None,
                    index_type: str = "ivfflat",
                    index_lists: int = 100) -> bool:
        """
        Create a new vector table
        
        Args:
            table_name: Name of the table to create
            vector_dimension: Dimension of vectors to store
            metadata_columns: Dict of column_name -> column_type for metadata
            index_type: Type of index ('ivfflat' or 'hnsw')
            index_lists: Number of lists for IVFFlat index
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_connected():
                self.connect()
            
            # Sanitize table name
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            with self.connection.cursor() as cursor:
                # Build CREATE TABLE statement
                columns = [
                    "id TEXT PRIMARY KEY",
                    f"embedding vector({vector_dimension})",
                    "content TEXT",
                    "metadata JSONB DEFAULT '{}'::jsonb",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ]
                
                # Add custom metadata columns
                if metadata_columns:
                    for col_name, col_type in metadata_columns.items():
                        columns.append(f"{col_name} {col_type}")
                
                create_sql = f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    {', '.join(columns)}
                );
                """
                
                cursor.execute(create_sql)
                
                # Create vector index for similarity search
                if index_type == "ivfflat":
                    index_sql = f"""
                    CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                    ON {full_table_name} 
                    USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = {index_lists});
                    """
                elif index_type == "hnsw":
                    index_sql = f"""
                    CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                    ON {full_table_name} 
                    USING hnsw (embedding vector_cosine_ops);
                    """
                else:
                    raise ValueError(f"Unsupported index type: {index_type}")
                
                cursor.execute(index_sql)
                
                # Create metadata index for filtering
                cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_metadata_idx 
                ON {full_table_name} USING gin (metadata);
                """)
                
                self.connection.commit()
                
                self._tables[table_name] = {
                    'dimension': vector_dimension,
                    'metadata_columns': metadata_columns or {},
                    'index_type': index_type
                }
                
                logger.info(f"Created table '{table_name}' with {vector_dimension}D vectors")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create table '{table_name}': {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def delete_table(self, table_name: str) -> bool:
        """
        Delete a vector table
        
        Args:
            table_name: Name of the table to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {full_table_name};")
                self.connection.commit()
                
                if table_name in self._tables:
                    del self._tables[table_name]
                
                logger.info(f"Deleted table '{table_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete table '{table_name}': {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def list_tables(self) -> List[str]:
        """
        List all vector tables in the database
        
        Returns:
            List[str]: List of table names
        """
        try:
            if not self.is_connected():
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_type = 'BASE TABLE'
                AND EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = tables.table_name 
                    AND column_name = 'embedding'
                    AND udt_name = 'vector'
                );
                """, (self.config.schema,))
                
                tables = [row['table_name'] for row in cursor.fetchall()]
                logger.info(f"Found {len(tables)} vector tables")
                return tables
                
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        return table_name.replace('-', '_').replace(' ', '_') in self.list_tables()
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dict with table information or None if not found
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            with self.connection.cursor() as cursor:
                # Get table schema
                cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
                """, (self.config.schema, table_name))
                
                columns = cursor.fetchall()
                
                # Get vector dimension
                cursor.execute(f"""
                SELECT typmod 
                FROM pg_attribute a 
                JOIN pg_class c ON a.attrelid = c.oid 
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = %s 
                AND c.relname = %s 
                AND a.attname = 'embedding';
                """, (self.config.schema, table_name))
                
                dimension_result = cursor.fetchone()
                dimension = dimension_result['typmod'] if dimension_result else None
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {full_table_name};")
                count = cursor.fetchone()['count']
                
                return {
                    'name': table_name,
                    'columns': columns,
                    'vector_dimension': dimension,
                    'row_count': count
                }
                
        except Exception as e:
            logger.error(f"Failed to get table info for '{table_name}': {e}")
            return None
    
    def add_vectors(self, 
                   table_name: str,
                   vectors: List[List[float]],
                   contents: Optional[List[str]] = None,
                   metadatas: Optional[List[Dict[str, Any]]] = None,
                   ids: Optional[List[str]] = None) -> bool:
        """
        Add vectors to a table
        
        Args:
            table_name: Name of the table
            vectors: List of vectors to add
            contents: List of content strings
            metadatas: List of metadata dictionaries
            ids: List of IDs (generated if not provided)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            if not vectors:
                raise ValueError("No vectors provided")
            
            num_vectors = len(vectors)
            
            # Generate IDs if not provided
            if not ids:
                ids = [str(uuid.uuid4()) for _ in range(num_vectors)]
            
            # Default content and metadata if not provided
            if not contents:
                contents = [""] * num_vectors
            if not metadatas:
                metadatas = [{}] * num_vectors
            
            # Ensure all lists have the same length
            if not (len(ids) == len(vectors) == len(contents) == len(metadatas)):
                raise ValueError("All input lists must have the same length")
            
            with self.connection.cursor() as cursor:
                for i in range(num_vectors):
                    vector_str = f"'{vectors[i]}'::vector"
                    metadata_json = json.dumps(metadatas[i])
                    
                    cursor.execute(f"""
                    INSERT INTO {full_table_name} 
                    (id, embedding, content, metadata) 
                    VALUES (%s, {vector_str}, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        created_at = CURRENT_TIMESTAMP;
                    """, (ids[i], contents[i], metadata_json))
                
                self.connection.commit()
                logger.info(f"Added {num_vectors} vectors to table '{table_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add vectors to table '{table_name}': {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def search_vectors(self, 
                      table_name: str,
                      query_vector: List[float],
                      limit: int = 10,
                      where_filter: Optional[Dict[str, Any]] = None,
                      distance_metric: str = "cosine") -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            table_name: Name of the table to search
            query_vector: Query vector
            limit: Maximum number of results
            where_filter: Metadata filter conditions
            distance_metric: Distance metric ('cosine', 'l2', 'inner_product')
            
        Returns:
            List of results with vectors, metadata, and distances
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            # Choose distance operator
            if distance_metric == "cosine":
                distance_op = "<=>"
            elif distance_metric == "l2":
                distance_op = "<->"
            elif distance_metric == "inner_product":
                distance_op = "<#>"
            else:
                raise ValueError(f"Unsupported distance metric: {distance_metric}")
            
            query_vector_str = f"'{query_vector}'::vector"
            
            # Build WHERE clause for metadata filtering
            where_clause = ""
            params = []
            
            if where_filter:
                conditions = []
                for key, value in where_filter.items():
                    if isinstance(value, dict):
                        # Handle operators like {"$gte": 5}
                        for op, op_value in value.items():
                            if op == "$gte":
                                conditions.append(f"(metadata->>%s)::float >= %s")
                                params.extend([key, op_value])
                            elif op == "$lte":
                                conditions.append(f"(metadata->>%s)::float <= %s")
                                params.extend([key, op_value])
                            elif op == "$eq":
                                conditions.append(f"metadata->>%s = %s")
                                params.extend([key, str(op_value)])
                            elif op == "$ne":
                                conditions.append(f"metadata->>%s != %s")
                                params.extend([key, str(op_value)])
                            elif op == "$in":
                                placeholders = ','.join(['%s'] * len(op_value))
                                conditions.append(f"metadata->>%s IN ({placeholders})")
                                params.append(key)
                                params.extend([str(v) for v in op_value])
                    else:
                        # Simple equality
                        conditions.append(f"metadata->>%s = %s")
                        params.extend([key, str(value)])
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            sql = f"""
            SELECT id, embedding, content, metadata,
                   embedding {distance_op} {query_vector_str} AS distance
            FROM {full_table_name}
            {where_clause}
            ORDER BY embedding {distance_op} {query_vector_str}
            LIMIT %s;
            """
            
            params.append(limit)
            
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                
                # Convert results to list of dicts
                formatted_results = []
                for row in results:
                    result = {
                        'id': row['id'],
                        'embedding': list(row['embedding']) if row['embedding'] else None,
                        'content': row['content'],
                        'metadata': row['metadata'] if row['metadata'] else {},
                        'distance': float(row['distance'])
                    }
                    formatted_results.append(result)
                
                logger.info(f"Found {len(formatted_results)} similar vectors in table '{table_name}'")
                return formatted_results
                
        except Exception as e:
            logger.error(f"Failed to search vectors in table '{table_name}': {e}")
            return []
    
    def update_vector(self, 
                     table_name: str,
                     id: str,
                     vector: Optional[List[float]] = None,
                     content: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a vector by ID
        
        Args:
            table_name: Name of the table
            id: ID of the vector to update
            vector: New vector (optional)
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            updates = []
            params = []
            
            if vector is not None:
                updates.append(f"embedding = '{vector}'::vector")
            
            if content is not None:
                updates.append("content = %s")
                params.append(content)
            
            if metadata is not None:
                updates.append("metadata = %s")
                params.append(json.dumps(metadata))
            
            if not updates:
                logger.warning("No updates provided")
                return False
            
            params.append(id)  # For WHERE clause
            
            sql = f"""
            UPDATE {full_table_name} 
            SET {', '.join(updates)}, created_at = CURRENT_TIMESTAMP
            WHERE id = %s;
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows_affected = cursor.rowcount
                self.connection.commit()
                
                if rows_affected > 0:
                    logger.info(f"Updated vector with ID '{id}' in table '{table_name}'")
                    return True
                else:
                    logger.warning(f"No vector found with ID '{id}' in table '{table_name}'")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to update vector '{id}' in table '{table_name}': {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def delete_vector(self, table_name: str, id: str) -> bool:
        """
        Delete a vector by ID
        
        Args:
            table_name: Name of the table
            id: ID of the vector to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {full_table_name} WHERE id = %s;", (id,))
                rows_affected = cursor.rowcount
                self.connection.commit()
                
                if rows_affected > 0:
                    logger.info(f"Deleted vector with ID '{id}' from table '{table_name}'")
                    return True
                else:
                    logger.warning(f"No vector found with ID '{id}' in table '{table_name}'")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to delete vector '{id}' from table '{table_name}': {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def delete_vectors(self, 
                      table_name: str,
                      where_filter: Optional[Dict[str, Any]] = None,
                      ids: Optional[List[str]] = None) -> int:
        """
        Delete multiple vectors by filter or IDs
        
        Args:
            table_name: Name of the table
            where_filter: Metadata filter conditions
            ids: List of IDs to delete
            
        Returns:
            int: Number of vectors deleted
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            where_clause = ""
            params = []
            
            if ids:
                placeholders = ','.join(['%s'] * len(ids))
                where_clause = f"WHERE id IN ({placeholders})"
                params.extend(ids)
            
            elif where_filter:
                conditions = []
                for key, value in where_filter.items():
                    if isinstance(value, dict):
                        # Handle operators
                        for op, op_value in value.items():
                            if op == "$gte":
                                conditions.append(f"(metadata->>%s)::float >= %s")
                                params.extend([key, op_value])
                            elif op == "$lte":
                                conditions.append(f"(metadata->>%s)::float <= %s")
                                params.extend([key, op_value])
                            elif op == "$eq":
                                conditions.append(f"metadata->>%s = %s")
                                params.extend([key, str(op_value)])
                            elif op == "$ne":
                                conditions.append(f"metadata->>%s != %s")
                                params.extend([key, str(op_value)])
                    else:
                        conditions.append(f"metadata->>%s = %s")
                        params.extend([key, str(value)])
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            sql = f"DELETE FROM {full_table_name} {where_clause};"
            
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows_affected = cursor.rowcount
                self.connection.commit()
                
                logger.info(f"Deleted {rows_affected} vectors from table '{table_name}'")
                return rows_affected
                
        except Exception as e:
            logger.error(f"Failed to delete vectors from table '{table_name}': {e}")
            if self.connection:
                self.connection.rollback()
            return 0
    
    def get_vector(self, table_name: str, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a vector by ID
        
        Args:
            table_name: Name of the table
            id: ID of the vector to retrieve
            
        Returns:
            Dict with vector data or None if not found
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                SELECT id, embedding, content, metadata, created_at
                FROM {full_table_name} 
                WHERE id = %s;
                """, (id,))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        'id': result['id'],
                        'embedding': list(result['embedding']) if result['embedding'] else None,
                        'content': result['content'],
                        'metadata': result['metadata'] if result['metadata'] else {},
                        'created_at': result['created_at']
                    }
                else:
                    return None
                
        except Exception as e:
            logger.error(f"Failed to get vector '{id}' from table '{table_name}': {e}")
            return None
    
    def count_vectors(self, 
                     table_name: str,
                     where_filter: Optional[Dict[str, Any]] = None) -> int:
        """
        Count vectors in a table with optional filtering
        
        Args:
            table_name: Name of the table
            where_filter: Metadata filter conditions
            
        Returns:
            int: Number of vectors
        """
        try:
            if not self.is_connected():
                self.connect()
            
            table_name = table_name.replace('-', '_').replace(' ', '_')
            full_table_name = f"{self.config.schema}.{table_name}"
            
            where_clause = ""
            params = []
            
            if where_filter:
                conditions = []
                for key, value in where_filter.items():
                    if isinstance(value, dict):
                        # Handle operators
                        for op, op_value in value.items():
                            if op == "$gte":
                                conditions.append(f"(metadata->>%s)::float >= %s")
                                params.extend([key, op_value])
                            elif op == "$lte":
                                conditions.append(f"(metadata->>%s)::float <= %s")
                                params.extend([key, op_value])
                            elif op == "$eq":
                                conditions.append(f"metadata->>%s = %s")
                                params.extend([key, str(op_value)])
                    else:
                        conditions.append(f"metadata->>%s = %s")
                        params.extend([key, str(value)])
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            sql = f"SELECT COUNT(*) as count FROM {full_table_name} {where_clause};"
            
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                count = result['count'] if result else 0
                
                logger.info(f"Table '{table_name}' contains {count} vectors")
                return count
                
        except Exception as e:
            logger.error(f"Failed to count vectors in table '{table_name}': {e}")
            return 0
    
    def reset_database(self) -> bool:
        """
        Reset the database by dropping all vector tables
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            tables = self.list_tables()
            
            for table in tables:
                self.delete_table(table)
            
            logger.info("Reset database - deleted all vector tables")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
