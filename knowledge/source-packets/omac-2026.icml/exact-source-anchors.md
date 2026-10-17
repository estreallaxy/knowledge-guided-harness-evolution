# Exact source anchors

## Selected mechanism

In this work, we introduce OMAC, a general framework designed for holistic optimization of LLM-based MAS.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.23; `paper/paper-icml2026.txt` marker `===== PDF p.23 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Method |
| Experimental setup | PDF p.14; `paper/paper-icml2026.txt` marker `===== PDF p.14 =====` | Experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 4.3. Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/code/MMLU/calc_score.py:8` | `process_lists` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/MMLU/calc_score.py:107` | `calculate_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/LLM_Agent.py:8` | `LLMAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/LLM_Agent.py:154` | `LLMEdge` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/prompt_lib.py:172` | `construct_ranking_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/prompt_lib.py:198` | `construct_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/prompt_lib.py:261` | `construct_judge_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/prompt_iteration/chat_service.py:13` | `retryable_openai_errors` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/prompt_iteration/chat_service.py:23` | `ChatService` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_readme_smoke.py:17` | `benchmark_import_context` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_readme_smoke.py:45` | `load_module` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_readme_smoke.py:52` | `ReadmeSmokeTests` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/HumanEval/prompt_iteration/prompt.py:12` | `Prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/MMLU/LLM_Agent.py:17` | `LLMAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/MMLU/LLM_Agent.py:116` | `LLMEdge` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/MMLU/LLM_Agent.py:128` | `parse_ranks` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/MMLU/prompt_lib.py:36` | `construct_ranking_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/MMLU/prompt_lib.py:60` | `construct_message` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `6bccfec5825adbb0f44d6e6bb5e3fe64cb98ee13`. Paper page numbers refer to the fixed local proceedings PDF.
