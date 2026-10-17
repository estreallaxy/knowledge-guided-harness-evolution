# Exact source anchors

## Selected mechanism

Build a graph of document chunks and perform query-guided associative traversal for contextual retrieval.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | framework |
| Results and ablations | PDF p.18; `paper/paper-iclr2026.txt` marker `===== PDF p.18 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/helpers/metrics.py:4` | `get_recall` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/helpers/metrics.py:18` | `exact_match_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/helpers/metrics.py:26` | `f1_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/ner_prompt.py:4` | `get_ner_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/encoders.py:3` | `NVEmbedEncoder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/encoders.py:26` | `QwenEncoder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/subquerygeneration.py:12` | `query_openai_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/subquerygeneration.py:34` | `process_queries` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/subquerygeneration.py:61` | `get_subqueries` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/rag_qa_prompts.py:2` | `BrowseNetQAPrompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/rag_qa_prompts.py:47` | `NaiveRAGQAPrompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/retrievers.py:11` | `get_index` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/retrievers.py:17` | `split_qs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/retrievers.py:27` | `split_q_tags` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/indexer/kg_evaluation.py:15` | `get_edge_accuracy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/NaiveRAG.py:19` | `NaiveRAG` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/BrowseNet.py:22` | `BrowseNet` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/helpers/utils.py:4` | `preprocess_entity` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ba82eeceb089104de2999d00b744cd02583fe8a4`. Paper page numbers refer to the fixed local proceedings PDF.
