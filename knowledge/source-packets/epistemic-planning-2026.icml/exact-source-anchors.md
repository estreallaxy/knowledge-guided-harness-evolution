# Exact source anchors

## Selected mechanism

To address this, we propose the Epistemic Planning Calibration Agentic Workflow (EPC-AW), which assesses whether plans remain supported under varying information conditions rather than directly verifying feasibility.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 4.1. System |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5.1. Experimental Setup |
| Results and ablations | PDF p.11; `paper/paper-icml2026.txt` marker `===== PDF p.11 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/MAS/epc_aw/tools/web_search/google_search.py:9` | `human_like_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/web_search/google_search.py:15` | `get_stealth_driver` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/web_search/google_search.py:43` | `google_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/google_search/local_google_scraper.py:12` | `human_like_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/google_search/local_google_scraper.py:18` | `get_stealth_driver` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/google_search/local_google_scraper.py:69` | `local_google_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/wikipedia_search/web_rag.py:71` | `Web_Search_Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/google_search/tool.py:38` | `Google_Search_Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/wikipedia_search/tool.py:37` | `Select_Relevant_Queries` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/wikipedia_search/tool.py:41` | `select_relevant_queries` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/wikipedia_search/tool.py:130` | `Wikipedia_Search_Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/web_search/tool.py:23` | `fetch_sciencedirect` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/web_search/tool.py:106` | `Web_Search_Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/test/calculate_score_unified.py:13` | `AnswerVerification` | Pinned implementation entry for the selected mechanism. |
| `official-code/test/calculate_score_unified.py:17` | `BinaryAnswerVerification` | Pinned implementation entry for the selected mechanism. |
| `official-code/test/calculate_score_unified.py:20` | `ResultScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/base.py:5` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/MAS/epc_aw/tools/base_generator/tool.py:22` | `Base_Generator_Tool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `f9cc88080e929b29cfa909c2196d3121fd5129d1`. Paper page numbers refer to the fixed local proceedings PDF.
