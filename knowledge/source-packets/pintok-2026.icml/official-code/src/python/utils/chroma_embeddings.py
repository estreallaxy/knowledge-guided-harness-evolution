"""
Custom ChromaDB embedding functions using BERTEncoder.

This module provides ChromaDB-compatible embedding functions that use
the BERTEncoder from the compare_tokenizers pipeline for consistent
embedding generation across the tokenization comparison system.
"""

from typing import List, Union
import numpy as np

try:
    from chromadb.api.types import EmbeddingFunction, Embeddings
    HAS_CHROMADB = True
except ImportError:
    # Fallback types for when ChromaDB is not available
    HAS_CHROMADB = False
    EmbeddingFunction = object
    Embeddings = List[List[float]]

from .encoders import BERTEncoder


class BERTEmbeddingFunction(EmbeddingFunction):
    """
    ChromaDB embedding function using BERTEncoder from compare_tokenizers.
    
    This provides consistent BERT embeddings for use in ChromaDB vector storage,
    using the same encoder that's used in the tokenization comparison pipelines.
    """
    
    def __init__(
        self, 
        encoder_type: str = "tinybert", 
        model_name: str = None, 
        force_cpu: bool = False,
        pooling_strategy: str = "mean",
        auto_initialize: bool = True
    ):
        """
        Initialize the BERT embedding function.
        
        Args:
            encoder_type: Type of BERT encoder ("tinybert")
            model_name: Specific model name to use (optional)
            force_cpu: Force CPU usage instead of GPU
            pooling_strategy: Pooling strategy ("mean", "cls", "max")
            auto_initialize: Whether to initialize the encoder immediately
        """
        self.encoder_type = encoder_type
        self.model_name = model_name
        self.force_cpu = force_cpu
        self.pooling_strategy = pooling_strategy
        self.bert_encoder = None
        
        if auto_initialize:
            self.initialize()
    
    def initialize(self):
        """Initialize the BERT encoder."""
        if self.bert_encoder is None:
            self.bert_encoder = BERTEncoder(
                encoder_type=self.encoder_type,
                model_name=self.model_name,
                force_cpu=self.force_cpu
            )
            self.bert_encoder.initialize()
    
    def __call__(self, input: Union[List[str], str]) -> Embeddings:
        """
        Generate embeddings for input texts.
        
        Args:
            input: Single text string or list of text strings
            
        Returns:
            List of embeddings (list of floats for each text)
        """
        if self.bert_encoder is None:
            self.initialize()
        
        # Handle single string input
        if isinstance(input, str):
            input = [input]
        
        # Convert texts to token IDs
        token_ids_list = []
        for text in input:
            token_ids = self.bert_encoder.text_to_token_ids(text)
            token_ids_list.append(token_ids)
        
        # Generate embeddings
        if len(token_ids_list) == 1:
            # Single text
            embeddings = self.bert_encoder.encode_with_pooling(
                token_ids_list[0], 
                self.pooling_strategy
            )
            # Convert to list format expected by ChromaDB
            return [embeddings.cpu().numpy().flatten().tolist()]
        else:
            # Batch processing
            batch_embeddings = self.bert_encoder.encode_batch_with_pooling(
                token_ids_list, 
                self.pooling_strategy
            )
            # Convert to list format expected by ChromaDB
            return [emb.cpu().numpy().flatten().tolist() for emb in batch_embeddings]


class TinyBERTEmbeddingFunction(BERTEmbeddingFunction):
    """
    Convenience class for TinyBERT embeddings.
    
    Pre-configured BERTEmbeddingFunction using TinyBERT model.
    """
    
    def __init__(self, force_cpu: bool = False, pooling_strategy: str = "mean"):
        """
        Initialize TinyBERT embedding function.
        
        Args:
            force_cpu: Force CPU usage instead of GPU
            pooling_strategy: Pooling strategy ("mean", "cls", "max")
        """
        super().__init__(
            encoder_type="tinybert",
            force_cpu=force_cpu,
            pooling_strategy=pooling_strategy
        )


class CustomBERTEmbeddingFunction(BERTEmbeddingFunction):
    """
    Custom BERT embedding function for specific model names.
    
    Allows using any HuggingFace BERT-compatible model as an embedding function.
    """
    
    def __init__(
        self, 
        model_name: str, 
        force_cpu: bool = False, 
        pooling_strategy: str = "mean"
    ):
        """
        Initialize custom BERT embedding function.
        
        Args:
            model_name: HuggingFace model name (e.g., "bert-base-uncased")
            force_cpu: Force CPU usage instead of GPU
            pooling_strategy: Pooling strategy ("mean", "cls", "max")
        """
        super().__init__(
            encoder_type="tinybert",  # Base encoder type
            model_name=model_name,
            force_cpu=force_cpu,
            pooling_strategy=pooling_strategy
        )


def create_bert_embedding_function(
    encoder_type: str = "tinybert",
    model_name: str = None,
    force_cpu: bool = False,
    pooling_strategy: str = "mean"
) -> BERTEmbeddingFunction:
    """
    Factory function to create BERT embedding functions.
    
    Args:
        encoder_type: Type of BERT encoder ("tinybert")
        model_name: Specific model name to use (optional)
        force_cpu: Force CPU usage instead of GPU
        pooling_strategy: Pooling strategy ("mean", "cls", "max")
        
    Returns:
        BERTEmbeddingFunction: Configured embedding function
        
    Example:
        >>> # Create TinyBERT embedding function
        >>> embed_fn = create_bert_embedding_function("tinybert")
        >>> 
        >>> # Create custom model embedding function
        >>> embed_fn = create_bert_embedding_function(
        ...     model_name="bert-base-uncased",
        ...     pooling_strategy="cls"
        ... )
    """
    return BERTEmbeddingFunction(
        encoder_type=encoder_type,
        model_name=model_name,
        force_cpu=force_cpu,
        pooling_strategy=pooling_strategy
    )


# Convenience instances for common use cases
def get_tinybert_embedding_function(force_cpu: bool = False) -> TinyBERTEmbeddingFunction:
    """
    Get a pre-configured TinyBERT embedding function.
    
    Args:
        force_cpu: Force CPU usage instead of GPU
        
    Returns:
        TinyBERTEmbeddingFunction: Ready-to-use TinyBERT embedding function
    """
    return TinyBERTEmbeddingFunction(force_cpu=force_cpu)


def get_custom_bert_embedding_function(
    model_name: str, 
    force_cpu: bool = False
) -> CustomBERTEmbeddingFunction:
    """
    Get a custom BERT embedding function for a specific model.
    
    Args:
        model_name: HuggingFace model name
        force_cpu: Force CPU usage instead of GPU
        
    Returns:
        CustomBERTEmbeddingFunction: Ready-to-use custom BERT embedding function
    """
    return CustomBERTEmbeddingFunction(model_name=model_name, force_cpu=force_cpu)
