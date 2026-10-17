# Exact source anchors

## Selected mechanism

To address this, we introduce ReviewBench, a benchmark evaluating review text according to paper-specific rubrics derived from official guidelines, the paper’s content, and human-written reviews.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | method |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/evaluator/2_evaluate_agenticreview.py:101` | `convert_ai_researcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_agenticreview.py:142` | `convert_agenticreview` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_agenticreview.py:195` | `ReviewProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/reviewer_agent/paper_search/paper_retriever.py:16` | `PaperRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate.py:99` | `ReviewProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate.py:129` | `load_prompt_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate.py:136` | `build_evaluation_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_cyclereviewer.py:100` | `convert_cyclereviewer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_cyclereviewer.py:191` | `ReviewProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_cyclereviewer.py:221` | `load_prompt_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_aiscientist.py:101` | `convert_ai_researcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_aiscientist.py:142` | `convert_agenticreview` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/2_evaluate_aiscientist.py:195` | `ReviewProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/reviewer_agent/related_work_searcher.py:30` | `RelatedWorkSearcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/reviewer_agent/paper_search/paper_search_api.py:9` | `PaperSearchAPI` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/reviewer_agent/paper_search/semantic_scholar_api.py:11` | `SemanticScholarAPI` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/reviewer_agent/paper_search/asta_api.py:21` | `AstaAPI` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluator/llm_service.py:29` | `LLMService` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7501cead4921d3f6e38615c09925345564858b97`. Paper page numbers refer to the fixed local proceedings PDF.
