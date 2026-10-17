# Exact source anchors

## Selected mechanism

To address this, we introduce MASPO, a novel framework designed to automatically and iteratively refine prompts across the entire system.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | system |
| Experimental setup | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 4. Experiments |
| Results and ablations | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | analysis |
| Limitations or failure conditions | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 3.4. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent.py:15` | `InferenceCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent.py:79` | `Agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent.py:160` | `MAS` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:29` | `get_role_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:167` | `get_agent_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/config.py:4` | `GraphType` | Pinned implementation entry for the selected mechanism. |
| `official-code/config.py:15` | `AgentType` | Pinned implementation entry for the selected mechanism. |
| `official-code/config.py:39` | `TaskType` | Pinned implementation entry for the selected mechanism. |
| `official-code/judges.py:7` | `LLMJudgeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/judges.py:34` | `CodeJudgeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_loaders.py:8` | `load_test_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_loaders.py:39` | `load_train_for_opt` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_loaders.py:45` | `get_task_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:14` | `async_retry` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:31` | `async_call_llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:54` | `extract_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_maspo.py:21` | `aprocess_single` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_maspo.py:78` | `aprocess_task` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `e79aa8ea00b14c1a28f5c13500676459456a3670`. Paper page numbers refer to the fixed local proceedings PDF.
