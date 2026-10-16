from __future__ import annotations

import threading

import torch
from sentence_transformers import SentenceTransformer

# Global model cache for singleton pattern
_sentence_transformer_model: SentenceTransformer | None = None
_model_lock = threading.Lock()


def get_sentence_embedding(sentence: str) -> torch.Tensor:
    global _sentence_transformer_model
    with _model_lock:
        if _sentence_transformer_model is None:
            _sentence_transformer_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = _sentence_transformer_model.encode(sentence, show_progress_bar=False)
    return torch.tensor(embeddings)
