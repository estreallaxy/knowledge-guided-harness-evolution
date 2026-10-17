# Exact source anchors

## Selected mechanism

Apply post-training progressive mixed-precision KV-cache quantization across layers and tokens for long reasoning traces.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | experiments |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/pm_kvq/evaluation/eval_livecodebench/prompts.py:6` | `CodeGenerationPromptConstants` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/prompts.py:33` | `TestOutputPromptConstants` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/prompts.py:52` | `SelfRepairPromptConstants` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/evaluator.py:15` | `score_code_generation` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/evaluator.py:53` | `score_code_execution` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/evaluator.py:60` | `score_test_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/testing_util.py:22` | `truncatefn` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/testing_util.py:30` | `CODE_TYPE` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/testing_util.py:36` | `TimeoutException` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/quantization/methods/pm_kvq/smoothattention/searching_scales.py:13` | `catch_feature_hook` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/quantization/methods/pm_kvq/smoothattention/searching_scales.py:22` | `catch_attention_ouptut_hook` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/quantization/methods/pm_kvq/smoothattention/searching_scales.py:32` | `search_rep_scales` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/quantization/methods/pm_kvq/progressive/progressive_quantized_cache.py:10` | `ProgressiveQuantizedCacheConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/quantization/methods/pm_kvq/progressive/progressive_quantized_cache.py:29` | `ProgressiveQuantizedCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/eval_wrapper.py:6` | `evaluate_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/judge.py:7` | `judge_aime` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/judge.py:55` | `judge_cmimc` | Pinned implementation entry for the selected mechanism. |
| `official-code/pm_kvq/evaluation/judge.py:103` | `judge_livecodebench` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c8a2bff80628a3c476c057aa42e13d5e5c55196f`. Paper page numbers refer to the fixed local proceedings PDF.
