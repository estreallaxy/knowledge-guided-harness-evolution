import json
import os
import re
import warnings
from typing import Dict, List, Tuple


try:
    import numpy as np
    import faiss
    from transformers import AutoModel, AutoTokenizer
    import torch

    _SEMANTIC_BACKEND = True
except Exception as e:
    _SEMANTIC_BACKEND = False
    _SEMANTIC_IMPORT_ERROR = str(e)


class MiniSentenceTransformer:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def encode(self, text):
        single = isinstance(text, str)
        texts = [text] if single else text
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = torch.mean(outputs.last_hidden_state, dim=1).cpu().numpy()
        return embeddings[0] if single else embeddings

    def get_sentence_embedding_dimension(self) -> int:
        return self.model.config.hidden_size


class ToolVectorSearcher:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", save_dir: str = "tool_vector_index"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

        self.tool_map: Dict[str, Dict] = {}
        self.id_map: List[str] = []
        self.query_cache = {}
        self.cache_size = 100

        self._semantic = _SEMANTIC_BACKEND
        self.index = None

        if self._semantic:
            self.model = MiniSentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            warnings.warn(
                "Semantic tool search backend unavailable; using lexical fallback. "
                f"Reason: {_SEMANTIC_IMPORT_ERROR}",
                RuntimeWarning,
            )

        self._load_index()

    def _metadata_path(self) -> str:
        return os.path.join(self.save_dir, "metadata.json")

    def _index_path(self) -> str:
        return os.path.join(self.save_dir, "faiss.index")

    def _load_metadata(self) -> None:
        meta_file = self._metadata_path()
        if not os.path.exists(meta_file):
            return
        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.tool_map = data.get("tool_map", {})
            self.id_map = data.get("id_map", [])

    def _save_metadata(self) -> None:
        with open(self._metadata_path(), "w", encoding="utf-8") as f:
            json.dump({"tool_map": self.tool_map, "id_map": self.id_map}, f, indent=2)

    def _rebuild_semantic_index(self) -> None:
        if not self._semantic:
            return

        self.index = faiss.IndexFlatIP(self.dimension)
        if not self.id_map:
            return

        embeddings = []
        for tid in self.id_map:
            desc = self.tool_map.get(tid, {}).get("description", "")
            emb = self.model.encode(desc).astype("float32")
            embeddings.append(emb)

        if embeddings:
            self.index.add(np.array(embeddings, dtype="float32"))

    def _load_index(self) -> bool:
        self._load_metadata()
        if not self._semantic:
            return True

        index_file = self._index_path()
        if os.path.exists(index_file):
            try:
                self.index = faiss.read_index(index_file)
                if self.index.ntotal == len(self.id_map):
                    return True
            except Exception as e:
                warnings.warn(f"Failed to load FAISS index: {e}")

        self._rebuild_semantic_index()
        return True

    def save(self) -> None:
        self._save_metadata()
        if self._semantic and self.index is not None and len(self.id_map) > 0:
            faiss.write_index(self.index, self._index_path())

    def add_tool(self, tool_id: str, description: str) -> None:
        if tool_id in self.tool_map:
            return

        self.tool_map[tool_id] = {
            "description": description,
            "index_pos": len(self.id_map),
        }
        self.id_map.append(tool_id)

        if self._semantic:
            emb = self.model.encode(description).astype("float32")
            self.index.add(np.expand_dims(emb, axis=0))

        self.query_cache = {}

    def remove_tool(self, tool_id: str) -> bool:
        if tool_id not in self.tool_map:
            return False

        del self.tool_map[tool_id]
        self.id_map = [tid for tid in self.id_map if tid != tool_id]
        for i, tid in enumerate(self.id_map):
            self.tool_map[tid]["index_pos"] = i

        if self._semantic:
            self._rebuild_semantic_index()

        self.query_cache = {}
        return True

    def _lexical_score(self, query: str, description: str) -> float:
        q_tokens = set(re.findall(r"[a-zA-Z0-9_]+", query.lower()))
        d_tokens = set(re.findall(r"[a-zA-Z0-9_]+", description.lower()))
        if not q_tokens or not d_tokens:
            return 0.0
        return len(q_tokens & d_tokens) / max(1, len(q_tokens))

    def search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Tuple[str, float]]:
        cache_key = (query, top_k, threshold)
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        if not self.tool_map:
            return []

        results: List[Tuple[str, float]] = []

        if self._semantic:
            query_embedding = self.model.encode(query).astype("float32")
            query_embedding = np.expand_dims(query_embedding, axis=0)
            distances, indices = self.index.search(query_embedding, top_k)
            for i, dist in zip(indices[0], distances[0]):
                if i == -1:
                    continue
                if dist < threshold:
                    continue
                results.append((self.id_map[i], float(dist)))
        else:
            for tid in self.id_map:
                desc = self.tool_map.get(tid, {}).get("description", "")
                score = self._lexical_score(query, desc)
                if score > 0:
                    results.append((tid, score))
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:top_k]

        if len(self.query_cache) >= self.cache_size:
            self.query_cache.pop(next(iter(self.query_cache)))
        self.query_cache[cache_key] = results
        return results

    def batch_add_tools(self, tools: Dict[str, str]) -> None:
        for tool_id, desc in tools.items():
            self.add_tool(tool_id, desc)

    def get_tool_description(self, tool_id: str) -> str:
        return self.tool_map.get(tool_id, {}).get("description", "")
