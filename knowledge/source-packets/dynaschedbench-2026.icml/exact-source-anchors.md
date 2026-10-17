# Exact source anchors

## Selected mechanism

To resolve this, we introduce DynaSchedBench , a diagnostic framework for DFJSP that rigorously controls the instance-generation process.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | framework |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/dsbx/Agents/LLMScheduler/tools.py:12` | `ToolRuntimeContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/tools.py:101` | `register_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/tools.py:105` | `execute_tool_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/prompts.py:38` | `_render_markdown_table` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/prompts.py:64` | `FewShotBank` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/prompts.py:225` | `_get_few_shot_examples` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/config.py:6` | `OType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/config.py:10` | `SType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/config.py:14` | `InfoLevel` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/RACEC/rule_evaluator.py:26` | `RuleEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Eval/Metrics.py:62` | `compute_static_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Eval/Metrics.py:289` | `compute_dynamic_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Eval/Metrics.py:371` | `evaluate_trajectory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/PolicyAdapter.py:10` | `LlmPolicyAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/logger.py:13` | `TrajectoryLogger` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/sampler.py:10` | `Sampler` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/sampler.py:46` | `choose_by_env_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/dsbx/Agents/LLMScheduler/sampler.py:68` | `choose_by_heuristic` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `08975bf4a0473c5dff9177393bc6743db9ddc946`. Paper page numbers refer to the fixed local proceedings PDF.
