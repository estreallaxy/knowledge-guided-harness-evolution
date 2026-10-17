import argparse
import glob
import json
import math
import os
import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

import spacy
from tqdm import tqdm


ALLOWED_NER_TYPES = {
    "PERSON", "NORP", "FAC", "ORG", "GPE", "LOC",
    "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE",
    "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY",
    "ORDINAL", "CARDINAL",
}

# These are often noisy for multi-hop bridge discovery. They are not dropped by default.
DEFAULT_DROP_TYPES = set()

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
_NLP = None


def get_nlp():
    """Lazy-load spaCy only when doc-level cache is unavailable."""
    global _NLP
    if _NLP is None:
        if spacy.prefer_gpu():
            print("[INFO] Using GPU for spaCy")
        else:
            print("[INFO] GPU not available, using CPU")
        _NLP = spacy.load("en_core_web_trf")
    return _NLP


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def load_jsonl(path: str, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if max_items is not None and len(rows) >= max_items:
                break
    return rows


def get_query_text(q: Dict[str, Any]) -> str:
    return q.get("text") or q.get("question") or q.get("query") or ""


def get_doc_id(d: Dict[str, Any], doc_idx: int) -> str:
    return str(d.get("_id") or d.get("id") or doc_idx)


def get_doc_text(d: Dict[str, Any]) -> str:
    title = d.get("title", "") or ""
    text = d.get("text", "") or ""
    if title:
        return f"{title}\n{text}"
    return text


def load_doc_entities_cache(path: Optional[str]) -> Dict[str, List[Dict[str, str]]]:
    cache: Dict[str, List[Dict[str, str]]] = {}
    if not path:
        return cache
    if not os.path.exists(path):
        print(f"[WARN] Doc entity cache not found: {path}; will fallback to spaCy NER.")
        return cache

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            doc_id = obj.get("doc_id")
            if doc_id is None:
                continue
            cache[str(doc_id)] = obj.get("entities") or []

    print(f"[INFO] Loaded doc entity cache: {path}, docs={len(cache)}")
    return cache


class BM25Retriever:
    def __init__(
        self,
        docs: List[Dict[str, Any]],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.docs = docs
        self.k1 = k1
        self.b = b

        self.doc_lens: List[int] = []
        self.postings: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        self.df: Dict[str, int] = {}

        self._build_index()

    def _build_index(self):
        print(f"[INFO] Building BM25 index for {len(self.docs)} docs ...")

        total_len = 0
        for doc_idx, doc in enumerate(tqdm(self.docs, desc="Indexing corpus", unit="doc")):
            text = get_doc_text(doc)
            toks = tokenize(text)
            tf = Counter(toks)
            doc_len = len(toks)

            self.doc_lens.append(doc_len)
            total_len += doc_len

            for term, cnt in tf.items():
                self.postings[term].append((doc_idx, cnt))

        self.avgdl = total_len / max(len(self.docs), 1)
        self.df = {term: len(rows) for term, rows in self.postings.items()}

        print(f"[INFO] BM25 index done. vocab={len(self.postings)}, avgdl={self.avgdl:.2f}")

    def idf(self, term: str) -> float:
        n = len(self.docs)
        df = self.df.get(term, 0)
        if df == 0:
            return 0.0
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        q_terms = tokenize(query)
        if not q_terms:
            return []

        scores: Dict[int, float] = defaultdict(float)

        for term in set(q_terms):
            idf = self.idf(term)
            if idf <= 0:
                continue

            for doc_idx, tf in self.postings.get(term, []):
                dl = self.doc_lens[doc_idx]
                denom = tf + self.k1 * (1.0 - self.b + self.b * dl / max(self.avgdl, 1e-9))
                scores[doc_idx] += idf * (tf * (self.k1 + 1.0)) / denom

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


def select_entities(
    by_type: Dict[str, List[Tuple[str, str, float]]],
    top_entity_ratio: Optional[float] = None,
    min_entities_per_type: int = 1,
    max_entities_per_type: Optional[int] = 10,
    max_entities_per_query: Optional[int] = 50,
) -> List[Tuple[str, str, float]]:
    """
    Select entities from ranked per-type buckets.

    If top_entity_ratio is provided, keep top p% within each entity type, with
    min_entities_per_type lower bound and max_entities_per_type upper bound.
    Otherwise, keep max_entities_per_type per type, matching the first retrieval script.
    """
    selected: List[Tuple[str, str, float]] = []

    for typ, rows in by_type.items():
        rows = sorted(rows, key=lambda x: (-x[2], x[0]))
        if not rows:
            continue

        if top_entity_ratio is None:
            keep_n = len(rows) if max_entities_per_type is None else max_entities_per_type
        else:
            keep_n = max(min_entities_per_type, math.ceil(len(rows) * top_entity_ratio))
            if max_entities_per_type is not None:
                keep_n = min(keep_n, max_entities_per_type)

        selected.extend(rows[:keep_n])

    selected = sorted(selected, key=lambda x: (-x[2], x[1], x[0]))
    if max_entities_per_query is not None:
        selected = selected[:max_entities_per_query]
    return selected


def extract_rank_weighted_entities(
    query: Dict[str, Any],
    retrieved: List[Tuple[int, float]],
    docs: List[Dict[str, Any]],
    doc_entities_cache: Optional[Dict[str, List[Dict[str, str]]]] = None,
    top_entity_ratio: Optional[float] = None,
    min_entities_per_type: int = 1,
    max_entities_per_type: Optional[int] = 10,
    max_entities_per_query: Optional[int] = 50,
    batch_size: int = 16,
    drop_types: Optional[set] = None,
) -> Dict[str, Any]:
    qid = query.get("_id") or query.get("id")
    qtxt = get_query_text(query)
    drop_types = drop_types or DEFAULT_DROP_TYPES

    scored: Dict[Tuple[str, str], float] = defaultdict(float)
    source_docs: Dict[Tuple[str, str], List[str]] = defaultdict(list)

    retrieved_doc_ids: List[str] = []
    texts: List[str] = []
    rank_info: List[Tuple[int, str, float, int]] = []

    for rank, (doc_idx, bm25_score) in enumerate(retrieved, start=1):
        doc = docs[doc_idx]
        doc_id = get_doc_id(doc, doc_idx)
        retrieved_doc_ids.append(doc_id)

        text = get_doc_text(doc).replace("(", " ( ").replace(")", " ) ")
        texts.append(text)
        rank_info.append((rank, doc_id, bm25_score, doc_idx))

    def add_entity(ent_text: str, typ: str, weight: float, doc_id: str):
        if typ not in ALLOWED_NER_TYPES or typ in drop_types:
            return
        ent_text = normalize_space(ent_text)
        if not ent_text or len(ent_text) <= 1:
            return

        key = (ent_text, typ)
        scored[key] += weight
        if len(source_docs[key]) < 5:
            source_docs[key].append(doc_id)

    # Prefer cached corpus NER. If cache is unavailable or incomplete for a doc, fallback to spaCy.
    cache = doc_entities_cache or {}
    missing_indices = []
    missing_rank_info = []
    missing_texts = []

    for (rank, doc_id, bm25_score, doc_idx), text in zip(rank_info, texts):
        rank_weight = 1.0 / rank
        score_weight = math.log1p(max(bm25_score, 0.0))
        weight = rank_weight * (1.0 + score_weight)

        cached_ents = cache.get(str(doc_id))
        if cached_ents is not None:
            for ent in cached_ents:
                add_entity(ent.get("entity", ""), ent.get("type", ""), weight, doc_id)
        else:
            missing_indices.append(doc_idx)
            missing_rank_info.append((rank, doc_id, bm25_score))
            missing_texts.append(text)

    if missing_texts:
        print(f"[WARN] {len(missing_texts)} retrieved docs missing from cache; fallback to spaCy NER.")
        nlp = get_nlp()
        for spacy_doc, (rank, doc_id, bm25_score) in zip(
            nlp.pipe(missing_texts, batch_size=batch_size, n_process=1),
            missing_rank_info,
        ):
            rank_weight = 1.0 / rank
            score_weight = math.log1p(max(bm25_score, 0.0))
            weight = rank_weight * (1.0 + score_weight)
            for ent in spacy_doc.ents:
                add_entity(ent.text, ent.label_, weight, doc_id)

    by_type: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
    for (ent_text, typ), score in scored.items():
        by_type[typ].append((ent_text, typ, score))

    selected = select_entities(
        by_type=by_type,
        top_entity_ratio=top_entity_ratio,
        min_entities_per_type=min_entities_per_type,
        max_entities_per_type=max_entities_per_type,
        max_entities_per_query=max_entities_per_query,
    )

    entities = []
    for ent_text, typ, score in selected:
        key = (ent_text, typ)
        entities.append(
            {
                "hop": 0,
                "entity": ent_text,
                "type": typ,
                "score": round(float(score), 6),
                "source": "retrieval_grounded",
                "support_doc_ids": source_docs.get(key, []),
            }
        )

    return {
        "_id": qid,
        "text": qtxt,
        "entities": entities,
        "retrieved_doc_ids": retrieved_doc_ids,
        "error": None,
    }


def parse_drop_types(value: str) -> set:
    if not value:
        return set()
    return {x.strip() for x in value.split(",") if x.strip()}


def run_query_file(
    queries_path: str,
    corpus_path: str,
    output_path: str,
    doc_entities_path: Optional[str] = None,
    max_queries: Optional[int] = None,
    top_k: int = 10,
    top_entity_ratio: Optional[float] = None,
    min_entities_per_type: int = 1,
    max_entities_per_type: Optional[int] = 10,
    max_entities_per_query: Optional[int] = 50,
    batch_size: int = 16,
    drop_types: Optional[set] = None,
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"[INFO] Loading queries: {queries_path}")
    queries = load_jsonl(queries_path, max_items=max_queries)
    print(f"[INFO] Loaded queries: {len(queries)}")

    print(f"[INFO] Loading corpus: {corpus_path}")
    docs = load_jsonl(corpus_path)
    print(f"[INFO] Loaded corpus docs: {len(docs)}")

    doc_entities_cache = load_doc_entities_cache(doc_entities_path)
    retriever = BM25Retriever(docs)

    with open(output_path, "w", encoding="utf-8") as fout:
        for q in tqdm(queries, desc="Retrieval-grounded query entities", unit="q"):
            qtxt = get_query_text(q)

            try:
                retrieved = retriever.search(qtxt, top_k=top_k)
                res = extract_rank_weighted_entities(
                    query=q,
                    retrieved=retrieved,
                    docs=docs,
                    doc_entities_cache=doc_entities_cache,
                    top_entity_ratio=top_entity_ratio,
                    min_entities_per_type=min_entities_per_type,
                    max_entities_per_type=max_entities_per_type,
                    max_entities_per_query=max_entities_per_query,
                    batch_size=batch_size,
                    drop_types=drop_types,
                )
            except Exception as e:
                res = {
                    "_id": q.get("_id") or q.get("id"),
                    "text": qtxt,
                    "entities": None,
                    "retrieved_doc_ids": [],
                    "error": str(e),
                }

            fout.write(json.dumps(res, ensure_ascii=False) + "\n")

    print(f"[OK] Saved retrieval-grounded query entities to: {output_path}")


def run_queries(
    dataset_names: Iterable[str],
    data_root: str = "datasets",
    output_dir: str = "results/queries_entities_retrieval",
    doc_entities_root: str = "results/corpus_doc_entities",
    max_queries: Optional[int] = None,
    top_k: int = 10,
    top_entity_ratio: Optional[float] = None,
    min_entities_per_type: int = 1,
    max_entities_per_type: Optional[int] = 10,
    max_entities_per_query: Optional[int] = 50,
    batch_size: int = 16,
    drop_types: Optional[set] = None,
):
    os.makedirs(output_dir, exist_ok=True)

    for ds in dataset_names:
        queries_path = os.path.join(data_root, ds, "queries.jsonl")
        corpus_path = os.path.join(data_root, ds, "corpus.jsonl")
        output_path = os.path.join(output_dir, f"{ds}.jsonl")
        doc_entities_path = os.path.join(doc_entities_root, f"{ds}.jsonl") if doc_entities_root else None

        print(f"\n[INFO] Dataset: {ds}")
        print(f"  queries: {queries_path}")
        print(f"  corpus : {corpus_path}")
        print(f"  cache  : {doc_entities_path}")
        print(f"  output : {output_path}")

        run_query_file(
            queries_path=queries_path,
            corpus_path=corpus_path,
            output_path=output_path,
            doc_entities_path=doc_entities_path,
            max_queries=max_queries,
            top_k=top_k,
            top_entity_ratio=top_entity_ratio,
            min_entities_per_type=min_entities_per_type,
            max_entities_per_type=max_entities_per_type,
            max_entities_per_query=max_entities_per_query,
            batch_size=batch_size,
            drop_types=drop_types,
        )


def list_datasets(data_root: str) -> List[str]:
    pat = os.path.join(data_root, "*/queries.jsonl")
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(pat))


def none_or_int(value: str) -> Optional[int]:
    if value is None or str(value).lower() == "none":
        return None
    return int(value)


def none_or_float(value: str) -> Optional[float]:
    if value is None or str(value).lower() == "none":
        return None
    return float(value)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieval-grounded query-centric entity extraction."
    )
    parser.add_argument("--data_root", type=str, default="datasets")
    parser.add_argument("--output_dir", type=str, default="results/queries_entities_retrieval")
    parser.add_argument("--doc_entities_root", type=str, default="results/corpus_doc_entities")
    parser.add_argument("--datasets", nargs="+", default=["all"])

    parser.add_argument("--max_queries", type=int, default=None)
    parser.add_argument("--top_k", type=int, default=10)
    parser.add_argument(
        "--top_entity_ratio",
        type=none_or_float,
        default=None,
        help="Keep top p%% entities within each type for each query. Example: 0.2. Use None to disable.",
    )
    parser.add_argument("--min_entities_per_type", type=int, default=1)
    parser.add_argument(
        "--max_entities_per_type",
        type=none_or_int,
        default=10,
        help="Upper bound per type. Use None to disable.",
    )
    parser.add_argument(
        "--max_entities_per_query",
        type=none_or_int,
        default=50,
        help="Upper bound per query. Use None to disable.",
    )
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument(
        "--drop_types",
        type=str,
        default="",
        help='Comma-separated entity types to drop, e.g. "DATE,CARDINAL,ORDINAL".',
    )

    return parser.parse_args()


def main():
    args = parse_args()
    available = list_datasets(args.data_root)

    if not available:
        print(f"[WARN] No datasets found under {args.data_root}")
        return

    if "all" in args.datasets:
        selected = available
    else:
        selected = args.datasets

    run_queries(
        dataset_names=selected,
        data_root=args.data_root,
        output_dir=args.output_dir,
        doc_entities_root=args.doc_entities_root,
        max_queries=args.max_queries,
        top_k=args.top_k,
        top_entity_ratio=args.top_entity_ratio,
        min_entities_per_type=args.min_entities_per_type,
        max_entities_per_type=args.max_entities_per_type,
        max_entities_per_query=args.max_entities_per_query,
        batch_size=args.batch_size,
        drop_types=parse_drop_types(args.drop_types),
    )


if __name__ == "__main__":
    main()
