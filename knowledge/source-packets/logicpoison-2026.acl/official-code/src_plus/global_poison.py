import argparse
import glob
import json
import os
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional

import spacy
from tqdm import tqdm

if spacy.prefer_gpu():
    print("[INFO] Using GPU for spaCy")
else:
    print("[INFO] GPU not available, using CPU")

nlp = spacy.load("en_core_web_trf")  # MUST load after prefer_gpu()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def get_doc_text(rec: dict, include_title: bool = False) -> str:
    """Keep include_title=False by default to preserve the original global-NER behavior."""
    title = rec.get("title", "") or ""
    text = rec.get("text", "") or ""
    if include_title and title:
        return f"{title}\n{text}"
    return text


def corpus_stats(
    input_path: str,
    batch_size: int = 32,
    doc_entities_output_path: Optional[str] = None,
    include_title: bool = False,
) -> Dict[str, Counter]:
    """
    Process corpus.jsonl using spaCy + GPU + nlp.pipe in batches.

    Returns:
        { label: Counter({ entity_text: count }) }

    Optionally saves a doc-level NER cache for retrieval-grounded query-centric poisoning:
        jsonl lines:
        {
          "doc_id": str,
          "title": str,
          "entities": [{"entity": str, "type": str}, ...]
        }

    Notes:
        - Corpus-level frequency counts preserve the original behavior: every entity mention is counted.
        - Doc-level cache deduplicates entities within each document, because query-centric scoring only
          needs to know whether an entity appears in a retrieved document.
    """
    cnts: Dict[str, Counter] = defaultdict(Counter)

    records = []
    with open(input_path, "r", encoding="utf-8") as fin:
        for idx, ln in enumerate(fin):
            ln = ln.strip()
            if not ln:
                continue
            rec = json.loads(ln)
            # Make sure cache ids can always match query_centric_retrieval fallback ids.
            if rec.get("_id") is None and rec.get("id") is None:
                rec["_logicpoison_doc_idx"] = str(idx)
            records.append(rec)

    print(f"[INFO] corpus size: {len(records)} docs")

    def txt_stream():
        for rec in records:
            txt = get_doc_text(rec, include_title=include_title)
            txt = txt.replace("(", " ( ").replace(")", " ) ")
            yield txt

    fout = None
    if doc_entities_output_path is not None:
        os.makedirs(os.path.dirname(doc_entities_output_path), exist_ok=True)
        fout = open(doc_entities_output_path, "w", encoding="utf-8")
        print(f"[INFO] Will save doc-level entity cache to: {doc_entities_output_path}")

    try:
        for rec, doc in tqdm(
            zip(records, nlp.pipe(txt_stream(), batch_size=batch_size, n_process=1)),
            total=len(records),
            desc=f"NER (GPU) on {os.path.basename(input_path)}",
            unit="doc",
        ):
            ents = []
            seen_in_doc = set()

            for ent in doc.ents:
                ent_text = normalize_space(ent.text)
                ent_type = ent.label_
                if not ent_text:
                    continue

                # Preserve mention-level frequency for global poisoning.
                cnts[ent_type][ent_text] += 1

                # Save a deduplicated doc-level cache for retrieval-grounded query-centric poisoning.
                key = (ent_text, ent_type)
                if key not in seen_in_doc:
                    seen_in_doc.add(key)
                    ents.append({"entity": ent_text, "type": ent_type})

            if fout is not None:
                doc_id = rec.get("_id") or rec.get("id") or rec.get("_logicpoison_doc_idx")
                out = {
                    "doc_id": str(doc_id) if doc_id is not None else None,
                    "title": rec.get("title", ""),
                    "entities": ents,
                }
                fout.write(json.dumps(out, ensure_ascii=False) + "\n")
    finally:
        if fout is not None:
            fout.close()

    return cnts


def save_stats(stats: Dict[str, Counter], output_path: str):
    data = {
        label: sorted(counter.items(), key=lambda x: -x[1])
        for label, counter in stats.items()
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved corpus entity stats to: {output_path}")


def run_corpus(
    dataset_names: Iterable[str],
    data_root: str = "datasets",
    output_root: str = "results/corpus_entities",
    doc_entities_root: str = "results/corpus_doc_entities",
    batch_size: int = 32,
    save_doc_entities: bool = True,
    include_title: bool = False,
):
    os.makedirs(output_root, exist_ok=True)
    if save_doc_entities:
        os.makedirs(doc_entities_root, exist_ok=True)

    for ds in dataset_names:
        in_path = os.path.join(data_root, ds, "corpus.jsonl")
        out_path = os.path.join(output_root, f"{ds}.json")
        doc_entities_path = os.path.join(doc_entities_root, f"{ds}.jsonl") if save_doc_entities else None

        print(f"\n[INFO] Processing corpus for dataset: {ds}")
        print(f"       Input : {in_path}")
        print(f"       Output: {out_path}")
        if doc_entities_path:
            print(f"       Cache : {doc_entities_path}")

        cnts = corpus_stats(
            in_path,
            batch_size=batch_size,
            doc_entities_output_path=doc_entities_path,
            include_title=include_title,
        )
        save_stats(cnts, out_path)


def run_all(
    data_root: str = "datasets",
    output_root: str = "results/corpus_entities",
    doc_entities_root: str = "results/corpus_doc_entities",
    batch_size: int = 32,
    save_doc_entities: bool = True,
    include_title: bool = False,
):
    pat = os.path.join(data_root, "*/corpus.jsonl")
    files = sorted(glob.glob(pat))
    ds_list = [os.path.basename(os.path.dirname(p)) for p in files]

    if not ds_list:
        print("[WARN] No corpus.jsonl files found.")
        return

    run_corpus(
        ds_list,
        data_root=data_root,
        output_root=output_root,
        doc_entities_root=doc_entities_root,
        batch_size=batch_size,
        save_doc_entities=save_doc_entities,
        include_title=include_title,
    )


def list_datasets(data_root: str) -> List[str]:
    pat = os.path.join(data_root, "*/corpus.jsonl")
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(pat))


def parse_args():
    parser = argparse.ArgumentParser(description="Extract corpus entity statistics by dataset.")
    parser.add_argument("--data_root", type=str, default="datasets")
    parser.add_argument("--output_root", type=str, default="results/corpus_entities")
    parser.add_argument("--doc_entities_root", type=str, default="results/corpus_doc_entities")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["all"],
        help='Dataset names, e.g. "hotpotqa musique", or "all".',
    )
    parser.add_argument(
        "--no_doc_entities",
        action="store_true",
        help="Do not save doc-level entity cache. Default: save it.",
    )
    parser.add_argument(
        "--include_title",
        action="store_true",
        help="Also run NER on document titles. Default keeps the original behavior: text only.",
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

    run_corpus(
        selected,
        data_root=args.data_root,
        output_root=args.output_root,
        doc_entities_root=args.doc_entities_root,
        batch_size=args.batch_size,
        save_doc_entities=not args.no_doc_entities,
        include_title=args.include_title,
    )


if __name__ == "__main__":
    main()
