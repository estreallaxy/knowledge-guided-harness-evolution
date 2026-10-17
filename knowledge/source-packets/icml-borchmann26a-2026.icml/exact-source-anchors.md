# Exact source anchors

## Selected mechanism

To address this, we introduce MADQA, a benchmark of 2,250 human-authored questions grounded in 800 heterogeneous PDF documents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.16; `paper/paper-icml2026.txt` marker `===== PDF p.16 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.41; `paper/paper-icml2026.txt` marker `===== PDF p.41 =====` | System |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eval/metrics.py:47` | `bias_adjusted_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/metrics.py:74` | `standard_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/metrics.py:108` | `confidence_interval` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/gemini-file-search/gemini_file_search_agent.py:28` | `GeminiFileSearchAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/gemini-file-search/gemini_file_search_agent.py:387` | `run_evaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/gemini-file-search/gemini_file_search_agent.py:445` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/openai-file-search/openai_file_search_agent.py:27` | `OpenAIFileSearchAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/openai-file-search/openai_file_search_agent.py:548` | `run_evaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/openai-file-search/openai_file_search_agent.py:606` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluate.py:31` | `derive_hop_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluate.py:68` | `load_gold_standard` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluate.py:103` | `load_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/heaven/retrieval.py:23` | `RetrievalResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/heaven/retrieval.py:32` | `HEAVENRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/heaven/retrieval.py:379` | `SimpleRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/bm25-mllm-agent/utils.py:30` | `_get_doc_urls` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/bm25-mllm-agent/utils.py:44` | `Citation` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/bm25-mllm-agent/utils.py:50` | `Answer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `978fa76de16acf983363557823f4f2d1ed74ba47`. Paper page numbers refer to the fixed local proceedings PDF.
