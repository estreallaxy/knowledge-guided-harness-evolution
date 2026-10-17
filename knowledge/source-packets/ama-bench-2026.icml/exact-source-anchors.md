# Exact source anchors

## Selected mechanism

To address this gap, we introduce AMA-Bench ( A gent M emory with A ny length), a benchmark for evaluating long-horizon memory in realistic agentic settings.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.17; `paper/paper-icml2026.txt` marker `===== PDF p.17 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Method |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 6.1. Experimental Setup |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 6.4. Ablation |
| Limitations or failure conditions | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/method/ama_agent_core/tool.py:9` | `traj_get` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/ama_agent_core/tool.py:63` | `traj_find` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/ama_agent_core/tool.py:119` | `get_openai_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/ama_agent_core/retrieve.py:34` | `_extract_step_numbers` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/ama_agent_core/retrieve.py:102` | `_extract_inline_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/ama_agent_core/retrieve.py:119` | `memory_retrieve` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate.py:10` | `evaluate_batch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate.py:59` | `evaluate_from_files` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate.py:210` | `print_evaluation_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/evaluation_metrics.py:21` | `normalize_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/evaluation_metrics.py:40` | `tokenize` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/evaluation_metrics.py:45` | `compute_exact_match` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_harness.py:49` | `_build_instruction` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_harness.py:85` | `_write_codex_home` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_harness.py:95` | `run_codex_episode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_interface.py:16` | `MemoryQAInterface` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/agent_method.py:14` | `AgentHarnessMethod` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/agent_method.py:58` | `CodexAgentMethod` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ddfd319e0be33424288c13806f1eafc63e625b59`. Paper page numbers refer to the fixed local proceedings PDF.
