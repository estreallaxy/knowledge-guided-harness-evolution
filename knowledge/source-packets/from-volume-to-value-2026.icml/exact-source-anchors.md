# Exact source anchors

## Selected mechanism

We propose EPIC (Efficient Preference-aligned Index Construction), which focuses on user preferences as a compact and stable form of personal context and integrates them throughout the RAG pipeline.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Method |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5.5. Ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 6. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/EPIC_evaluation.py:6` | `EPICEvaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/EPIC_main.py:13` | `EPICMain` | Pinned implementation entry for the selected mechanism. |
| `official-code/EPIC_main.py:139` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/EPIC_generation.py:10` | `EPICGeneration` | Pinned implementation entry for the selected mechanism. |
| `official-code/EPIC_indexing.py:9` | `EPICIndexing` | Pinned implementation entry for the selected mechanism. |
| `official-code/EPIC_utils.py:14` | `set_global_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/EPIC_utils.py:23` | `EPICUtils` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/build_chunks.py:6` | `load_documents` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/build_chunks.py:19` | `clean_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/build_chunks.py:24` | `chunk_documents_sentencewise` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/sample_documents.py:8` | `sample_wiki_documents` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/sample_documents.py:42` | `sample_eli5_documents` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/sample_documents.py:81` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/build_embeddings.py:10` | `mean_pooling` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/build_embeddings.py:16` | `load_chunks` | Pinned implementation entry for the selected mechanism. |
| `official-code/preprocess/build_embeddings.py:25` | `load_models` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ee63fff6fe5c00b1cb65d6f6a1ab4fa2e1f4338c`. Paper page numbers refer to the fixed local proceedings PDF.
