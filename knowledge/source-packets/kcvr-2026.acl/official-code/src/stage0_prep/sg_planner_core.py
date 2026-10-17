from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KnowledgeConcept:
    id: str
    name: str
    level: int
    definition: str
    subject: str
    first_appear_module: str


@dataclass(frozen=True)
class TeachingPoint:
    id: str
    name: str
    level: int
    description: str
    subject: str


@dataclass(frozen=True)
class PlannerConfig:
    # SG-Planner configuration

    seed_top_k: int = 20
    final_top_b: int = 10
    alpha_match: float = 0.6
    sim_threshold: float = 0.3
    neighbor_decay: float = 0.5
    weight_based_on: float = 1.0
    weight_next: float = 0.5
    max_swap_iters: int = 200
    keep_unknown_module: bool = True
    top_module_k: int = 2
    module_soft_keep_score: float = 1.2
    max_tp_per_kc: int = 2
    include_tp_next_edges: bool = True
    # If a KC is only briefly mentioned early and not supported by objectives/knowledge_points,
    # down-weight it to avoid "background review" dominating the plan.
    background_early_pos: float = 0.25
    background_pos_weight_min: float = 0.35
    # Penalize very specific sub-branches unless supported by objectives/knowledge_points.
    specific_penalty: float = 0.6


def _strip(x: Optional[str]) -> str:
    return (x or "").strip()


def _to_int(x: str, default: int = 0) -> int:
    try:
        return int(float(x))
    except Exception:
        return default


def _normalize_text(text: str) -> str:
    """Normalize text for matching.

    Args:
        text: Raw input text.

    Returns:
        Normalized text.
    """
    t = text.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _normalize_concept_phrase(phrase: str) -> str:
    """Normalize a concept phrase from objectives/knowledge_points.

    This removes common Chinese suffixes like "的定义/的特征/的方法/与...的关系" to better match KC names.

    Args:
        phrase: Raw phrase.

    Returns:
        Normalized phrase.
    """
    p = _strip(phrase)
    if not p:
        return ""
    p = re.sub(r"[【】\[\]（）()、，,。\.；;：:\-—_]+", " ", p)
    p = re.sub(r"\s+", " ", p).strip()
    # Remove common suffix patterns
    p = re.sub(r"(的)?(定义|概念|特征|性质|方法|公式|判定方法|应用|意义|作用|关系)$", "", p).strip()
    p = re.sub(r"(与|和).+(的)?(关系|联系)$", "", p).strip()
    return _normalize_text(p)


def _infer_tp_module(tp_id: str) -> Optional[str]:
    """Infer module token from TP id like 'tp_math_alg1_ch1_sec1'.

    Args:
        tp_id: TP node id.

    Returns:
        Module token or None.
    """
    if not tp_id.startswith("tp_"):
        return None
    parts = tp_id.split("_")
    # Expected: tp_{subj_code}_{module}_...
    if len(parts) >= 3:
        mod = parts[2].strip()
        return mod or None
    return None


class TextSimilarity:
    """Text similarity helper with optional embedding backend.

    - If `sentence_transformers` is available, it will be used for stable cosine similarity.
    - Otherwise fallback to TF-IDF cosine (requires sklearn).
    """

    def __init__(self, model_name_or_path: Optional[str] = None, device: str = "cpu") -> None:
        """Init similarity.

        Args:
            model_name_or_path: SentenceTransformer model path/name (e.g., bge-m3).
            device: "cpu" or "cuda".
        """
        self._backend = "tfidf"
        self._model = None
        self._device = device
        self._warned_tfidf_fallback = False
        self._tfidf_vect = None
        self._tfidf_mat = None
        self._doc_ids: List[str] = []
        self._docs_text: List[str] = []
        self._docs_tokens: List[Set[str]] = []
        self._doc_embs = None
        self._hf_tokenizer = None
        self._hf_model = None
        if model_name_or_path:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                self._model = SentenceTransformer(model_name_or_path, device=device)
                self._backend = "sbert"
            except Exception as e:
                # Try to fallback to HuggingFace + safetensors (works with torch<2.6, avoids transformers torch.load check).
                msg = str(e)
                logger.warning("SentenceTransformer unavailable: %s", e)
                try:
                    from transformers import AutoModel, AutoTokenizer  # type: ignore

                    model_dir = Path(model_name_or_path)
                    safetensors_path = model_dir / "model.safetensors"
                    if not safetensors_path.exists():
                        logger.warning(
                            "No model.safetensors found under %s; please convert pytorch_model.bin to safetensors or upgrade torch>=2.6.",
                            model_dir,
                        )
                        self._backend = "tfidf"
                    else:
                        self._hf_tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
                        self._hf_model = AutoModel.from_pretrained(
                            model_name_or_path,
                            torch_dtype=None,
                            device_map=None,
                            use_safetensors=True,
                        )
                        if device.startswith("cuda"):
                            import torch

                            self._hf_model = self._hf_model.to(torch.device(device))
                        self._hf_model.eval()
                        self._backend = "hf"
                except Exception as e2:
                    logger.warning("HF safetensors backend unavailable, fallback to TF-IDF: %s", e2)
                    self._model = None
                    self._backend = "tfidf"

    def prepare_corpus(self, doc_ids: Sequence[str], docs: Sequence[str]) -> None:
        """Prepare corpus representations for fast query-time similarity.

        Args:
            doc_ids: Document IDs aligned with docs.
            docs: Document texts.

        Returns:
            None
        """
        self._doc_ids = list(doc_ids)
        self._docs_text = list(docs)
        # Precompute tokens for robust fallback (works even when sklearn breaks)
        self._docs_tokens = [set(_normalize_text(d).split()) for d in docs]
        if not docs:
            return
        if self._backend == "sbert" and self._model is not None:
            self._doc_embs = self._model.encode(list(docs), normalize_embeddings=True)
            return
        if self._backend == "hf" and self._hf_model is not None and self._hf_tokenizer is not None:
            self._doc_embs = self._hf_encode(list(docs))
            return
        # TF-IDF fallback (fit once)
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

            self._tfidf_vect = TfidfVectorizer(max_features=50000)
            self._tfidf_mat = self._tfidf_vect.fit_transform(list(docs))
        except Exception as e:
            if not self._warned_tfidf_fallback:
                logger.warning("TF-IDF unavailable, will fallback to token overlap: %s", e)
                self._warned_tfidf_fallback = True
            self._tfidf_vect = None
            self._tfidf_mat = None

    def cosine_sim_query(self, query: str) -> Dict[str, float]:
        """Compute cosine similarity between query and prepared corpus.

        Args:
            query: Query text.

        Returns:
            Mapping doc_id -> similarity.
        """
        if not self._doc_ids:
            return {}
        if self._backend == "sbert" and self._model is not None and self._doc_embs is not None:
            q = self._model.encode([query], normalize_embeddings=True)
            sims = (self._doc_embs @ q.T).reshape(-1)
            return {self._doc_ids[i]: float(sims[i]) for i in range(len(self._doc_ids))}
        if self._backend == "hf" and self._hf_model is not None and self._hf_tokenizer is not None and self._doc_embs is not None:
            q = self._hf_encode([query])
            sims = (self._doc_embs @ q.T).reshape(-1)
            return {self._doc_ids[i]: float(sims[i]) for i in range(len(self._doc_ids))}
        if self._tfidf_vect is not None and self._tfidf_mat is not None:
            try:
                from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

                qv = self._tfidf_vect.transform([query])
                sims = cosine_similarity(self._tfidf_mat, qv).reshape(-1)
                return {self._doc_ids[i]: float(sims[i]) for i in range(len(self._doc_ids))}
            except Exception as e:
                if not self._warned_tfidf_fallback:
                    logger.warning("TF-IDF query failed, fallback to token overlap: %s", e)
                    self._warned_tfidf_fallback = True
        # token overlap fallback
        q_tokens = set(_normalize_text(query).split())
        out: Dict[str, float] = {}
        for i, doc_id in enumerate(self._doc_ids):
            d_tokens = self._docs_tokens[i] if i < len(self._docs_tokens) else set()
            inter = len(q_tokens & d_tokens)
            denom = max(1, len(q_tokens | d_tokens))
            out[doc_id] = float(inter) / float(denom)
        return out

    def backend_name(self) -> str:
        """Return current similarity backend name.

        Returns:
            One of: "sbert" | "tfidf" | "overlap".
        """
        if self._backend == "sbert" and self._model is not None and self._doc_embs is not None:
            return "sbert"
        if self._backend == "hf" and self._hf_model is not None and self._doc_embs is not None:
            return "hf"
        if self._tfidf_vect is not None and self._tfidf_mat is not None:
            return "tfidf"
        return "overlap"

    def _hf_encode(self, texts: List[str], batch_size: int = 16) -> "Any":
        """Encode texts with HuggingFace model into L2-normalized embeddings.

        Args:
            texts: Input texts.
            batch_size: Batch size.

        Returns:
            A 2D numpy array of shape [N, D] (float32) for stable dot products.
        """
        import numpy as np
        import torch

        assert self._hf_model is not None
        assert self._hf_tokenizer is not None

        outs: List[np.ndarray] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            tok = self._hf_tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            if self._device.startswith("cuda"):
                tok = {k: v.to(torch.device(self._device)) for k, v in tok.items()}
            with torch.no_grad():
                out = self._hf_model(**tok)
                last = out.last_hidden_state  # [B, T, H]
                mask = tok["attention_mask"].unsqueeze(-1).to(last.dtype)  # [B, T, 1]
                summed = (last * mask).sum(dim=1)
                denom = mask.sum(dim=1).clamp(min=1.0)
                emb = summed / denom
                emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            outs.append(emb.detach().float().cpu().numpy())
        return np.concatenate(outs, axis=0)


class GraphStore:
    """In-memory KG store for SG-Planner."""

    def __init__(
        self,
        kc_nodes: Dict[str, KnowledgeConcept],
        tp_nodes: Dict[str, TeachingPoint],
        relations: List[Tuple[str, str, str]],
    ) -> None:
        """Init graph store.

        Args:
            kc_nodes: KC nodes by id.
            tp_nodes: TP nodes by id.
            relations: (start_id, end_id, type) triples.
        """
        self.kc_nodes = kc_nodes
        self.tp_nodes = tp_nodes
        self.relations = relations

        self.kc_adj: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # kc -> [(neighbor_kc, type)]
        self.has_concept_tp_to_kc: Dict[str, Set[str]] = defaultdict(set)
        self.has_concept_kc_to_tp: Dict[str, Set[str]] = defaultdict(set)
        self.tp_next: Set[Tuple[str, str]] = set()

        for s, e, t in relations:
            if t in {"BASED_ON", "RELATED_TO", "EXTENDS", "NEXT"} and s in kc_nodes and e in kc_nodes:
                self.kc_adj[s].append((e, t))
                self.kc_adj[e].append((s, t)) if t in {"RELATED_TO", "EXTENDS"} else None
            if t == "HAS_CONCEPT" and s in tp_nodes and e in kc_nodes:
                self.has_concept_tp_to_kc[s].add(e)
                self.has_concept_kc_to_tp[e].add(s)
            if t == "NEXT" and s in tp_nodes and e in tp_nodes:
                self.tp_next.add((s, e))

    @staticmethod
    def load_from_raw_csv(raw_csv_root: Path, subject: str) -> "GraphStore":
        """Load graph store from aggregated `knowledge_graph/raw_csv/`.

        Args:
            raw_csv_root: knowledge_graph/raw_csv directory.
            subject: Canonical subject name (e.g., "math").

        Returns:
            GraphStore
        """
        import csv

        kc_path = raw_csv_root / "nodes_kc.csv"
        tp_path = raw_csv_root / "nodes_tp.csv"
        rel_path = raw_csv_root / "relations.csv"

        kc_nodes: Dict[str, KnowledgeConcept] = {}
        tp_nodes: Dict[str, TeachingPoint] = {}
        relations: List[Tuple[str, str, str]] = []

        with kc_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if _strip(row.get("subject")) != subject:
                    continue
                rid = _strip(row.get("id"))
                if not rid:
                    continue
                kc_nodes[rid] = KnowledgeConcept(
                    id=rid,
                    name=_strip(row.get("name")),
                    level=_to_int(_strip(row.get("level")), 0),
                    definition=_strip(row.get("definition")),
                    subject=subject,
                    first_appear_module=_strip(row.get("first_appear_module")) or "unknown",
                )

        with tp_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if _strip(row.get("subject")) != subject:
                    continue
                rid = _strip(row.get("id"))
                if not rid:
                    continue
                tp_nodes[rid] = TeachingPoint(
                    id=rid,
                    name=_strip(row.get("name")),
                    level=_to_int(_strip(row.get("level")), 0),
                    description=_strip(row.get("description")),
                    subject=subject,
                )

        with rel_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                s = _strip(row.get(":START_ID"))
                e = _strip(row.get(":END_ID"))
                t = _strip(row.get(":TYPE"))
                if not s or not e or not t:
                    continue
                # Keep only relations whose endpoints exist in the loaded node sets.
                # NOTE: do NOT filter by `subject in id` because many subjects use id prefixes
                # like kc_chem / kc_bio / kc_chi which do not contain "chemistry/biology/chinese".
                if t in {"BASED_ON", "RELATED_TO", "EXTENDS", "NEXT"}:
                    # KC-KC edges (and sometimes KC-KC NEXT)
                    if s in kc_nodes and e in kc_nodes:
                        relations.append((s, e, t))
                    continue
                if t == "HAS_CONCEPT":
                    if s in tp_nodes and e in kc_nodes:
                        relations.append((s, e, t))
                    continue
                # TP-TP NEXT
                if t == "NEXT":
                    if s in tp_nodes and e in tp_nodes:
                        relations.append((s, e, t))
                    continue

        return GraphStore(kc_nodes=kc_nodes, tp_nodes=tp_nodes, relations=relations)


def _kc_name_match(text_norm: str, kc_name: str) -> bool:
    if not kc_name:
        return False
    return _normalize_text(kc_name) in text_norm


def _kc_last_occurrence_ratio(text: str, phrase: str) -> Optional[float]:
    """Return last occurrence position ratio of phrase in text.

    Args:
        text: Raw text.
        phrase: Phrase to search (raw).

    Returns:
        Ratio in [0,1] (end-position / len(text)) if found, else None.
    """
    t = text
    p = phrase
    if not t or not p:
        return None
    idx = t.rfind(p)
    if idx < 0:
        return None
    denom = max(1, len(t))
    return float(idx) / float(denom)


def _pick_segment_module(kc_ids: Sequence[str], kc_nodes: Dict[str, KnowledgeConcept]) -> Optional[str]:
    mods = [kc_nodes[k].first_appear_module for k in kc_ids if k in kc_nodes and kc_nodes[k].first_appear_module != "unknown"]
    if not mods:
        return None
    return Counter(mods).most_common(1)[0][0]


def _min_violation_ordering(
    items: List[str],
    precedence_edges: List[Tuple[str, str, float]],
    max_iters: int,
) -> List[str]:
    """Greedy adjacent swap to reduce violation cost.

    Args:
        items: Initial ordering.
        precedence_edges: List of (before, after, weight) meaning "before must appear before after".
        max_iters: Max swap iterations.

    Returns:
        Optimized ordering.
    """
    if len(items) <= 2 or not precedence_edges:
        return items

    def cost(order: List[str]) -> float:
        pos = {x: i for i, x in enumerate(order)}
        c = 0.0
        for before, after, w in precedence_edges:
            if before not in pos or after not in pos:
                continue
            if pos[after] < pos[before]:
                c += w
        return c

    order = list(items)
    cur = cost(order)
    it = 0
    while it < max_iters:
        improved = False
        for i in range(len(order) - 1):
            swapped = list(order)
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            c2 = cost(swapped)
            if c2 + 1e-9 < cur:
                order = swapped
                cur = c2
                improved = True
        if not improved:
            break
        it += 1
    return order


# Paper Reference: Section 3.1 (SG-Planner: Contextual Pruning)
# Algorithm: Subgraph extraction via contextual pruning + min-violation ordering
def plan_one_segment(
    graph: GraphStore,
    transcript: str,
    objectives: Sequence[str],
    knowledge_points: Sequence[Dict[str, Any]],
    config: PlannerConfig,
    similarity: TextSimilarity,
) -> Dict[str, Any]:
    """Generate SG-Plan for one segment.

    Args:
        graph: Subject-specific graph store.
        transcript: Segment transcript (ASR).
        objectives: Segment learning objectives.
        knowledge_points: Segment knowledge points (name+level).
        config: Planner config.
        similarity: Text similarity helper.

    Returns:
        Plan dict with kc_nodes, tp_nodes, edges, pi_kc, scores, and debug fields.
    """
    transcript_norm = _normalize_text(transcript)
    obj_text_norm = _normalize_text(" ".join([str(x) for x in objectives]))
    kp_phrases = [_strip(x.get("name")) for x in knowledge_points if isinstance(x, dict)]
    kp_norm_core = {_normalize_concept_phrase(p) for p in kp_phrases if p}
    obj_norm_core = {_normalize_concept_phrase(x) for x in objectives if isinstance(x, str)}

    sim_map = similarity.cosine_sim_query(transcript)

    raw_scores: Dict[str, float] = {}
    match_scores: Dict[str, float] = {}
    for k, kc in graph.kc_nodes.items():
        m = 0.0
        mentioned = _kc_name_match(transcript_norm, kc.name)
        last_pos = _kc_last_occurrence_ratio(transcript, kc.name) if mentioned else None
        pos_weight = 1.0
        if last_pos is not None:
            # Later mentions indicate this KC is more central to the segment.
            pos_weight = max(config.background_pos_weight_min, min(1.0, 0.5 + 0.5 * last_pos))
        if mentioned:
            m += 1.0 * pos_weight
        if kc.name and _normalize_text(kc.name) in obj_text_norm:
            m += 0.5
        # Fuzzy/core phrase match from objectives/knowledge_points
        kc_norm = _normalize_text(kc.name)
        if kc_norm:
            for core in kp_norm_core:
                if core and (kc_norm in core or core in kc_norm):
                    m += 1.0
                    break
            for core in obj_norm_core:
                if core and (kc_norm in core or core in kc_norm):
                    m += 0.5
                    break

        # Penalize over-specific branches if they are only a brief early review.
        supported = False
        for core in kp_norm_core:
            if core and (kc_norm in core or core in kc_norm):
                supported = True
                break
        if not supported:
            for core in obj_norm_core:
                if core and (kc_norm in core or core in kc_norm):
                    supported = True
                    break
        if (not supported) and kc.name:
            # Heuristic: branches like "一次函数/二次函数/三角函数..." are often review noise.
            if re.search(r"^(一次|二次|三次|线性|二次)$", kc.name) or re.search(r"(一次函数|二次函数|三角函数|对数函数|指数函数)$", kc.name):
                m *= config.specific_penalty
        match_scores[k] = m
        raw_scores[k] = config.alpha_match * m + (1.0 - config.alpha_match) * float(sim_map.get(k, 0.0))

    # Seed selection
    seeds = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)[: config.seed_top_k]
    seed_ids = [k for k, _ in seeds]
    seed_score_map = {k: s for k, s in seeds}

    # Expand 1-hop neighbors
    cand_score: Dict[str, float] = dict(seed_score_map)
    for sid, sscore in seeds:
        for nb, rtype in graph.kc_adj.get(sid, []):
            if nb not in graph.kc_nodes:
                continue
            cand_score[nb] = max(cand_score.get(nb, 0.0), config.neighbor_decay * sscore)

    cand_ids = list(cand_score.keys())
    # Soft module selection: take top-K modules from seeds, do not hard-kill strong candidates
    module_votes = Counter(
        [graph.kc_nodes[k].first_appear_module for k in seed_ids if k in graph.kc_nodes and graph.kc_nodes[k].first_appear_module != "unknown"]
    )
    top_modules = [m for m, _ in module_votes.most_common(config.top_module_k)]
    seg_module = top_modules[0] if top_modules else ""

    # Contextual pruning by module (soft gate)
    if top_modules:
        filtered: List[str] = []
        for k in cand_ids:
            fam = graph.kc_nodes[k].first_appear_module
            if fam in top_modules or (config.keep_unknown_module and fam == "unknown"):
                filtered.append(k)
                continue
            # Keep high-confidence cross-module KC to avoid false negatives
            if raw_scores.get(k, 0.0) >= config.module_soft_keep_score:
                filtered.append(k)
        cand_ids = filtered

    # Prune by sim threshold if not mentioned
    final_scores: Dict[str, float] = {}
    for k in cand_ids:
        sim = float(sim_map.get(k, 0.0))
        mentioned = _kc_name_match(transcript_norm, graph.kc_nodes[k].name)
        if (not mentioned) and sim < config.sim_threshold:
            continue
        # Merge base score with neighbor-decay for stability
        final_scores[k] = max(raw_scores.get(k, 0.0), cand_score.get(k, 0.0))

    chosen = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[: config.final_top_b]
    kc_sub = [k for k, _ in chosen]
    score_sub = {k: float(s) for k, s in chosen}

    # TP nodes induced by HAS_CONCEPT (keep only top few anchors per KC)
    tp_sub: Set[str] = set()
    edges: Dict[str, List[List[str]]] = defaultdict(list)
    for k in kc_sub:
        tps = list(graph.has_concept_kc_to_tp.get(k, set()))
        if not tps:
            continue
        # Rank TP anchors: module match first, then finer-grained TP (level=3 preferred)
        def _tp_rank(tp_id: str) -> Tuple[int, int]:
            tp_mod = _infer_tp_module(tp_id) or ""
            mod_ok = 1 if (seg_module and tp_mod == seg_module) else 0
            tp_level = graph.tp_nodes[tp_id].level if tp_id in graph.tp_nodes else 0
            return (mod_ok, tp_level)

        tps_sorted = sorted(tps, key=_tp_rank, reverse=True)[: config.max_tp_per_kc]
        for tp in tps_sorted:
            if tp in graph.tp_nodes:
                tp_sub.add(tp)
                edges["HAS_CONCEPT"].append([tp, k])

    # KC edges among selected nodes
    kc_set = set(kc_sub)
    for s, e, t in graph.relations:
        if t in {"BASED_ON", "RELATED_TO", "EXTENDS", "NEXT"} and s in kc_set and e in kc_set:
            edges[t].append([s, e])

    # Precedence edges for ordering
    precedence: List[Tuple[str, str, float]] = []
    # BASED_ON: "post -> pre" (post depends on pre), so pre should be before post
    for s, e, t in graph.relations:
        if t == "BASED_ON" and s in kc_set and e in kc_set:
            precedence.append((e, s, config.weight_based_on))
        if t == "NEXT" and s in kc_set and e in kc_set:
            precedence.append((s, e, config.weight_next))

    init_order = sorted(kc_sub, key=lambda x: score_sub.get(x, 0.0), reverse=True)
    pi_kc = _min_violation_ordering(init_order, precedence, max_iters=config.max_swap_iters)

    # Coverage vs annotated knowledge_points (weak match, best-effort)
    # IMPORTANT: do not use strict equality; use normalized phrase + containment (+ optional fuzzy) to avoid systemic underestimation.
    kp_hit = 0
    kp_total = len([x for x in kp_norm_core if x])
    kc_phrase_norm = [_normalize_concept_phrase(graph.kc_nodes[k].name) for k in kc_sub if k in graph.kc_nodes]
    kc_phrase_norm = [x for x in kc_phrase_norm if x]

    def _weak_hit(core: str) -> bool:
        if not core:
            return False
        for kc_core in kc_phrase_norm:
            if not kc_core:
                continue
            if core == kc_core:
                return True
            if core in kc_core or kc_core in core:
                return True
        # Optional fuzzy match if rapidfuzz is available
        try:
            from rapidfuzz import fuzz  # type: ignore

            for kc_core in kc_phrase_norm:
                if fuzz.ratio(core, kc_core) >= 85:
                    return True
        except Exception:
            pass
        return False

    for core in kp_norm_core:
        if core and _weak_hit(core):
            kp_hit += 1

    kp_recall: Optional[float]
    if kp_total > 0:
        kp_recall = float(kp_hit) / float(kp_total)
    else:
        kp_recall = None

    # TP NEXT edges (optional, for explainability)
    if config.include_tp_next_edges:
        for s, e in sorted(graph.tp_next):
            if s in tp_sub and e in tp_sub:
                edges["NEXT_TP"].append([s, e])

    return {
        "tp_nodes": sorted(tp_sub),
        "kc_nodes": kc_sub,
        "edges": dict(edges),
        "pi_kc": pi_kc,
        "scores": score_sub,
        "debug": {
            "segment_module": seg_module or "",
            "top_modules": top_modules,
            "kp_total": kp_total,
            "kp_hit": kp_hit,
            "kp_recall": kp_recall,
            "seed_top_k": config.seed_top_k,
            "final_top_b": config.final_top_b,
            "alpha_match": config.alpha_match,
            "sim_threshold": config.sim_threshold,
            "sim_backend": similarity.backend_name(),
        },
    }


