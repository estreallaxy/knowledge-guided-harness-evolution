# Exact source anchors

## Selected mechanism

Represent, execute, and score constraint-aware multi-domain plans and tool-use workflows.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.20; `paper/paper-iclr2026.txt` marker `===== PDF p.20 =====` | Mechanism-specific discussion |
| Results and ablations | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | results |
| Limitations or failure conditions | PDF p.26; `paper/paper-iclr2026.txt` marker `===== PDF p.26 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/utils/evaluation/evaluate_workflow_as_DAG.py:13` | `_unit_node_subst_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluation/evaluate_workflow_as_DAG.py:22` | `_weighted_node_subst_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluation/evaluate_workflow_as_DAG.py:57` | `_unit_edge_subst_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/orchestration_agent.py:24` | `OrchestrationAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluation/evaluate_arguments.py:28` | `process_single_llm_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluation/evaluate_arguments.py:99` | `call_evaluation_llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluation/evaluate_arguments.py:269` | `calculate_function_name_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/orchestration_engine.py:17` | `debug_log` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/orchestration_engine.py:21` | `OrchestrationEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/base_agent.py:14` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/toolcall_fetcher.py:5` | `ToolResultFetcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/llm_agent.py:29` | `LLMAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config_loader.py:17` | `load_dotenv` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config_loader.py:38` | `substitute_env_vars` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config_loader.py:47` | `load_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation.py:20` | `load_eval_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation.py:38` | `apply_judge_env_overrides` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation.py:116` | `load_evaluation_data` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `f3596dadffad5eebf5abb281e51e5a239cfbd131`. Paper page numbers refer to the fixed local proceedings PDF.
