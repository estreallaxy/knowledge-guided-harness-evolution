# Exact source anchors

## Selected mechanism

We introduce STING ( Sequential Testing of Illicit N-step Goal execution ), an automated red-teaming framework that constructs a step-by-step illicit plan grounded in a benign persona and iteratively probes a target agent with adaptive follow-ups, using judge agents to track phase completion.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.13; `paper/paper-icml2026.txt` marker `===== PDF p.13 =====` | System |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 5. Experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agentharm/benchmark/benign_tools/verify_database_security.py:12` | `verify_database_security` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/gpt_evaluator.py:8` | `_find_json_objects` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/gpt_evaluator.py:37` | `_extract_json_fragment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/gpt_evaluator.py:110` | `_judge_user_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/benign_tools/search_asset_libraries.py:20` | `search_asset_libraries` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/benign_tools/search_web_hosting.py:11` | `search_web_hosting` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/benign_tools/search_hotels.py:33` | `search_hotels` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/search_asset_libraries.py:21` | `search_asset_libraries` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/search_web_hosting.py:12` | `search_web_hosting` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/benign_tools/query_onion_search.py:24` | `query_onion_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/benign_tools/query_bing_search.py:39` | `query_bing_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/search_hotels.py:34` | `search_hotels` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/query_bing_search.py:32` | `query_bing_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/benign_tools/query_google_search.py:74` | `query_google_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/query_onion_search.py:35` | `_maybe_load_encoder` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/query_onion_search.py:81` | `_semantic_lookup` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/query_onion_search.py:105` | `_slugify` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentharm/benchmark/harmful_tools/query_google_search.py:65` | `query_google_search` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c8053cf60737b3c43b24ec927ad77b995986a4c9`. Paper page numbers refer to the fixed local proceedings PDF.
