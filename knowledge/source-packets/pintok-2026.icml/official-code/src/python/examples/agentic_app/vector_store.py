import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from vectordb_clients.chromadb.client import ChromaDBClient, ChromaConfig
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import uuid
from config import config

logger = logging.getLogger(__name__)

class CustomEmbeddingFunction:
    """Custom embedding function using sentence-transformers"""
    
    def __init__(self, model_name: Optional[str] = config.EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name, device=config.EMBEDDING_DEVICE)
        logger.info(f"Loaded embedding model: {self.model_name}")
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

class VectorStore:
    """Vector store manager using ChromaDB with custom client"""
    
    def __init__(self):
        self.chroma_config = ChromaConfig(
            host=config.CHROMA_HOST,
            port=config.CHROMA_PORT,
            persist_directory=config.CHROMA_PERSIST_DIR,
            is_persistent=config.CHROMA_IS_PERSISTENT
        )
        self.client = ChromaDBClient(self.chroma_config)
        self.embedding_function = CustomEmbeddingFunction()
        logger.info("Vector store initialized")
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection"""
        try:
            # Check if collection exists
            collections = self.client.list_collections()
            if collection_name in [col.name for col in collections]:
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Create collection with custom embedding function
            success = self.client.create_collection(
                collection_name,
                embedding_function=self.embedding_function
            )
            if success:
                logger.info(f"Created collection: {collection_name}")
            return success
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ) -> List[str]:
        """Add documents to the collection"""
        try:
            # Create collection if it doesn't exist
            self.create_collection(collection_name)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Prepare metadatas
            if metadatas is None:
                metadatas = [{} for _ in documents]
            
            # Add documents
            success = self.client.add_documents(
                collection_name=collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            if success:
                logger.info(f"Added {len(documents)} documents to {collection_name}")
                return ids
            else:
                logger.error("Failed to add documents")
                return []
                
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return []
    
    def query_documents(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 3,
        where: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Query documents from the collection"""
        try:
            results = self.client.query_documents(
                collection_name=collection_name,
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            if results:
                logger.info(f"Retrieved {len(results.get('documents', [[]])[0])} documents")
                return {
                    'documents': results.get('documents', [[]])[0],
                    'metadatas': results.get('metadatas', [[]])[0],
                    'distances': results.get('distances', [[]])[0],
                    'ids': results.get('ids', [[]])[0]
                }
            return {'documents': [], 'metadatas': [], 'distances': [], 'ids': []}
            
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return {'documents': [], 'metadatas': [], 'distances': [], 'ids': []}
    
    def delete_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            success = self.client.delete_documents(
                collection_name=collection_name,
                ids=[doc_id]
            )
            if success:
                logger.info(f"Deleted document {doc_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            collection = self.client.get_collection(collection_name)
            if collection:
                return {
                    'name': collection.name,
                    'count': collection.count(),
                    'metadata': collection.metadata
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
