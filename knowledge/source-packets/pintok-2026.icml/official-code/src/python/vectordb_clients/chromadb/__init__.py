"""
ChromaDB integration package for DPDKTokenizer

This package provides a comprehensive ChromaDB client for managing vector databases
with integration to the DPDK tokenizer utilities.
"""

from .client import ChromaDBClient, ChromaConfig, create_default_client, create_server_client

__version__ = "1.0.0"
__author__ = "XXXXX"

__all__ = [
    "ChromaDBClient",
    "ChromaConfig", 
    "create_default_client",
    "create_server_client"
]