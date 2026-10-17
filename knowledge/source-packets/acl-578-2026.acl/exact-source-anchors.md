# Exact source anchors

## Selected mechanism

To address this, we propose SMCS, a Scalable Multi-LLM Collaboration System designed to effectively coordinate multiple open-source LLMs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | design |
| Results and ablations | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | results |
| Limitations or failure conditions | PDF p.20; `paper/paper-acl2026.txt` marker `===== PDF p.20 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_code_execution_metrics.py:7` | `evaluate_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_code_execution_metrics.py:21` | `pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_code_execution_metrics.py:25` | `code_execution_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_scores.py:15` | `get_parser` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_scores.py:72` | `compute_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_code_generation_metrics.py:23` | `_temp_run` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_code_generation_metrics.py:29` | `check_correctness` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/evaluation/compute_code_generation_metrics.py:56` | `evaluate_generations_by_problem` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/IFEval/build_reference_cache.py:28` | `build_reference_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MBPP/evaluator.py:42` | `Evaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_local.py:21` | `load_mmlu_pro` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_local.py:29` | `load_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_local.py:40` | `preprocess` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_api.py:30` | `call_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_api.py:42` | `async_call_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_api.py:47` | `call_api_with_reference` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/runner/custom_evaluator.py:15` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/global_utils/runtime_config.py:18` | `repo_root` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `4efe959935de87926d1a1b3e6106e59d110ee4db`. Paper page numbers refer to the fixed local proceedings PDF.
