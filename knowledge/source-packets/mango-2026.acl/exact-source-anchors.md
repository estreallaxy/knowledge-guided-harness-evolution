# Exact source anchors

## Selected mechanism

We propose Mango, a multi-agent web navigation method that leverages the website structure to dynamically determine optimal starting points.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Method |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 4.3 Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/llm_web_scraper/utils/embedding_scorer.py:16` | `_get_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_web_scraper/utils/embedding_scorer.py:23` | `_fetch_url` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_web_scraper/utils/embedding_scorer.py:35` | `_extract_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webvoyager/evaluate.py:8` | `load_task_configs` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webvoyager/evaluate.py:20` | `build_evaluation_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webvoyager/evaluate.py:35` | `parse_evaluation_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webwalker/evaluate.py:27` | `eval_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/baselines/webwalker/agent.py:19` | `WebWalker` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webvoyager/rebuttal/run_no_memory_ablation.py:15` | `normalize_model_name_for_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webvoyager/rebuttal/run_no_memory_ablation.py:21` | `load_preprocessed_urls` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webvoyager/rebuttal/run_no_memory_ablation.py:35` | `filter_file_urls` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_no_memory_ablation.py:16` | `normalize_model_name_for_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_no_memory_ablation.py:22` | `load_preprocessed_urls` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_no_memory_ablation.py:36` | `filter_file_urls` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_web_scraper/prompts/final_answer.py:5` | `get_final_answer_instruction` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_web_scraper/prompts/final_answer.py:15` | `get_final_answer_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_web_scraper/prompts/simple_navigation.py:1` | `get_navigation_instruction` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_web_scraper/prompts/simple_navigation.py:28` | `get_navigation_prompt` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c6490d5530d9f0d6a189fe107d1bb17183dc4caf`. Paper page numbers refer to the fixed local proceedings PDF.
