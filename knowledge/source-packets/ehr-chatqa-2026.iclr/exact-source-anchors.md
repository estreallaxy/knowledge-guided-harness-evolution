# Exact source anchors

## Selected mechanism

Evaluate multi-turn clarification, terminology resolution, query generation, and execution against a stateful EHR database.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Results and ablations | PDF p.25; `paper/paper-iclr2026.txt` marker `===== PDF p.25 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agents/tool_calling_agent.py:33` | `ToolCallingAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/mimic_iv_star/tools/table_search.py:6` | `TableSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/eicu_star/tools/table_search.py:6` | `TableSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/mimic_iv_star/tools/web_search.py:7` | `WebSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/eicu_star/tools/web_search.py:7` | `WebSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/eicu_star/tools/value_similarity_search.py:6` | `ValueSimilaritySearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/mimic_iv_star/tools/value_similarity_search.py:6` | `ValueSimilaritySearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/mimic_iv_star/tools/value_substring_search.py:8` | `ValueSubstringSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/eicu_star/tools/value_substring_search.py:8` | `ValueSubstringSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/mimic_iv_star/tools/column_search.py:6` | `ColumnSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/eicu_star/tools/column_search.py:6` | `ColumnSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/metric.py:10` | `load_result_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/metric.py:17` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/metric.py:95` | `calculate_metrics_by_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_factory.py:4` | `get_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/envs/tools.py:4` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/base.py:7` | `AgentTimeoutError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/base.py:11` | `Agent` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8b97b9a303ce601690224435c3aa54dab19c4d00`. Paper page numbers refer to the fixed local proceedings PDF.
