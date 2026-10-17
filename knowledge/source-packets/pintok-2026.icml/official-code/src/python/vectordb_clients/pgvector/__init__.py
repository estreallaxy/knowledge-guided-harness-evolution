"""
pgvector Client for DPDKTokenizer

A comprehensive PostgreSQL/pgvector client for vector database operations.
"""

from .client import PgVectorClient, PgVectorConfig

__all__ = ['PgVectorClient', 'PgVectorConfig']
__version__ = '1.0.0'