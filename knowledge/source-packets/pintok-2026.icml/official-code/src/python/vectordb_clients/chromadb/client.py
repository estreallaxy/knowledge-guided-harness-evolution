import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional, Union, Any
import logging
import uuid
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChromaConfig:
    """Configuration for ChromaDB client"""
    host: str = "localhost"
    port: int = 8000
    persist_directory: Optional[str] = None
    is_persistent: bool = False
    auth_token: Optional[str] = None
    ssl: bool = False
    headers: Optional[Dict[str, str]] = None

class ChromaDBClient:
    """
    A comprehensive ChromaDB client for managing vector databases
    
    This client provides high-level operations for:
    - Connection management
    - Collection operations (create, delete, list)
    - Document operations (add, query, update, delete)
    - Metadata management
    """
    
    def __init__(self, config: Optional[ChromaConfig] = None):
        """
        Initialize ChromaDB client
        
        Args:
            config: ChromaConfig object with connection settings
        """
        self.config = config or ChromaConfig()
        self.client = None
        self._collections = {}
        self.connect()
    
    def connect(self) -> bool:
        """
        Establish connection to ChromaDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.config.is_persistent and self.config.persist_directory:
                # Persistent client
                self.client = chromadb.PersistentClient(
                    path=self.config.persist_directory,
                    settings=Settings(
                        allow_reset=True,
                        anonymized_telemetry=False
                    )
                )
                logger.info(f"Connected to persistent ChromaDB at {self.config.persist_directory}")
            
            elif self.config.host and self.config.port:
                # HTTP client
                settings = Settings(
                    chroma_server_host=self.config.host,
                    chroma_server_http_port=str(self.config.port),
                    chroma_server_ssl_enabled=self.config.ssl,
                    anonymized_telemetry=False
                )
                
                if self.config.auth_token:
                    settings.chroma_server_auth_provider = "token"
                    settings.chroma_server_auth_credentials = self.config.auth_token
                
                if self.config.headers:
                    settings.chroma_server_headers = self.config.headers
                
                self.client = chromadb.HttpClient(
                    host=self.config.host,
                    port=self.config.port,
                    ssl=self.config.ssl,
                    headers=self.config.headers,
                    settings=settings
                )
                logger.info(f"Connected to ChromaDB server at {self.config.host}:{self.config.port}")
            
            else:
                # In-memory client
                self.client = chromadb.Client(
                    settings=Settings(
                        allow_reset=True,
                        anonymized_telemetry=False
                    )
                )
                logger.info("Connected to in-memory ChromaDB")
            
            # Test connection
            self.client.heartbeat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from ChromaDB"""
        if self.client:
            self.client = None
            self._collections.clear()
            logger.info("Disconnected from ChromaDB")
    
    def reset_database(self) -> bool:
        """
        Reset the entire database (WARNING: This deletes all data)
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            if self.client:
                self.client.reset()
                self._collections.clear()
                logger.warning("Database reset - ALL DATA DELETED")
                return True
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
    
    def create_collection(self, 
                         name: str, 
                         metadata: Optional[Dict[str, Any]] = None,
                         embedding_function=None,
                         get_or_create: bool = True) -> bool:
        """
        Create a new collection
        
        Args:
            name: Collection name
            metadata: Optional metadata for the collection
            embedding_function: Custom embedding function
            get_or_create: If True, get existing collection if it exists
            
        Returns:
            bool: True if collection created/retrieved successfully
        """
        try:
            if get_or_create:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata=metadata,
                    embedding_function=embedding_function
                )
            else:
                collection = self.client.create_collection(
                    name=name,
                    metadata=metadata,
                    embedding_function=embedding_function
                )
            
            self._collections[name] = collection
            logger.info(f"Collection '{name}' {'created' if not get_or_create else 'created/retrieved'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            return False
    
    def get_collection(self, name: str) -> Optional[Any]:
        """
        Get an existing collection
        
        Args:
            name: Collection name
            
        Returns:
            Collection object or None if not found
        """
        try:
            if name in self._collections:
                return self._collections[name]
            
            collection = self.client.get_collection(name=name)
            self._collections[name] = collection
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection '{name}': {e}")
            return None
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection
        
        Args:
            name: Collection name
            
        Returns:
            bool: True if deletion successful
        """
        try:
            self.client.delete_collection(name=name)
            if name in self._collections:
                del self._collections[name]
            logger.info(f"Collection '{name}' deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """
        List all collections
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[str],
                     metadatas: Optional[List[Dict[str, Any]]] = None,
                     ids: Optional[List[str]] = None,
                     embeddings: Optional[List[List[float]]] = None) -> bool:
        """
        Add documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs (auto-generated if None)
            embeddings: Optional pre-computed embeddings
            
        Returns:
            bool: True if documents added successfully
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return False
            
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Validate input lengths
            if metadatas and len(metadatas) != len(documents):
                logger.error("Metadatas length must match documents length")
                return False
            
            if embeddings and len(embeddings) != len(documents):
                logger.error("Embeddings length must match documents length")
                return False
            
            # Add documents
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to '{collection_name}': {e}")
            return False
    
    def query_documents(self,
                       collection_name: str,
                       query_texts: Optional[List[str]] = None,
                       query_embeddings: Optional[List[List[float]]] = None,
                       n_results: int = 10,
                       where: Optional[Dict[str, Any]] = None,
                       where_document: Optional[Dict[str, Any]] = None,
                       include: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Query documents from a collection
        
        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            query_embeddings: List of query embeddings
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions
            include: List of fields to include in results
            
        Returns:
            Query results or None if failed
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return None
            
            if include is None:
                include = ["documents", "metadatas", "distances"]
            
            results = collection.query(
                query_texts=query_texts,
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=include
            )
            
            logger.info(f"Query returned {len(results.get('ids', []))} results from '{collection_name}'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query collection '{collection_name}': {e}")
            return None
    
    def update_documents(self,
                        collection_name: str,
                        ids: List[str],
                        documents: Optional[List[str]] = None,
                        metadatas: Optional[List[Dict[str, Any]]] = None,
                        embeddings: Optional[List[List[float]]] = None) -> bool:
        """
        Update existing documents in a collection
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to update
            documents: Optional new document texts
            metadatas: Optional new metadata
            embeddings: Optional new embeddings
            
        Returns:
            bool: True if update successful
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return False
            
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"Updated {len(ids)} documents in collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update documents in '{collection_name}': {e}")
            return False
    
    def delete_documents(self, collection_name: str, ids: List[str]) -> bool:
        """
        Delete documents from a collection
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return False
            
            collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents from '{collection_name}': {e}")
            return False
    
    def get_documents(self,
                     collection_name: str,
                     ids: Optional[List[str]] = None,
                     where: Optional[Dict[str, Any]] = None,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None,
                     include: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get documents from a collection
        
        Args:
            collection_name: Name of the collection
            ids: Optional list of specific document IDs
            where: Optional metadata filter
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            include: Optional list of fields to include
            
        Returns:
            Documents or None if failed
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return None
            
            if include is None:
                include = ["documents", "metadatas"]
            
            results = collection.get(
                ids=ids,
                where=where,
                limit=limit,
                offset=offset,
                include=include
            )
            
            logger.info(f"Retrieved {len(results.get('ids', []))} documents from '{collection_name}'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get documents from '{collection_name}': {e}")
            return None
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information or None if failed
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return None
            
            count = collection.count()
            metadata = collection.metadata
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get info for collection '{collection_name}': {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if the ChromaDB connection is healthy
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if self.client:
                self.client.heartbeat()
                return True
            return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Example usage and utility functions
def create_default_client(persist_dir: Optional[str] = None) -> ChromaDBClient:
    """
    Create a ChromaDB client with default configuration
    
    Args:
        persist_dir: Optional directory for persistent storage
        
    Returns:
        ChromaDBClient instance
    """
    config = ChromaConfig(
        is_persistent=persist_dir is not None,
        persist_directory=persist_dir
    )
    return ChromaDBClient(config)

def create_server_client(host: str = "localhost", 
                        port: int = 8000,
                        auth_token: Optional[str] = None) -> ChromaDBClient:
    """
    Create a ChromaDB client for server connection
    
    Args:
        host: Server hostname
        port: Server port
        auth_token: Optional authentication token
        
    Returns:
        ChromaDBClient instance
    """
    config = ChromaConfig(
        host=host,
        port=port,
        auth_token=auth_token,
        is_persistent=False
    )
    return ChromaDBClient(config)