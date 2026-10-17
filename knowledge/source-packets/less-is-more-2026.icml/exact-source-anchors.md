# Exact source anchors

## Selected mechanism

To address these limitations, we propose CORE-RAG, a novel framework for context compression in RAG systems.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | framework |
| Experimental setup | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | experiments |
| Results and ablations | PDF p.13; `paper/paper-icml2026.txt` marker `===== PDF p.13 =====` | results |
| Limitations or failure conditions | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/verl_core/tests/reward_score/test_sandbox_fusion.py:78` | `test_integration_success_correct` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/tests/reward_score/test_sandbox_fusion.py:89` | `test_integration_success_wrong_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/tests/reward_score/test_sandbox_fusion.py:99` | `test_integration_compile_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/math_verify.py:23` | `compute_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/prime_code/testing_util.py:39` | `truncatefn` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/prime_code/testing_util.py:47` | `CODE_TYPE` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/prime_code/testing_util.py:54` | `Capturing` | Pinned implementation entry for the selected mechanism. |
| `official-code/LLaMA-Factory/src/llamafactory/eval/evaluator.py:61` | `Evaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/LLaMA-Factory/src/llamafactory/eval/evaluator.py:157` | `run_eval` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/recipe/r1/reward_score.py:16` | `reward_func` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/math_batch.py:18` | `compute_score_batched` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/geo3k.py:20` | `format_reward` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/geo3k.py:26` | `acc_reward` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/geo3k.py:31` | `compute_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/gsm8k.py:18` | `extract_solution` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/gsm8k.py:44` | `compute_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/api_chat_completion.py:8` | `OpenAPI` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl_core/verl/utils/reward_score/__init__.py:19` | `default_compute_score` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `bb3690f2b4c377985fd07fb52fa28e1293a5794b`. Paper page numbers refer to the fixed local proceedings PDF.
