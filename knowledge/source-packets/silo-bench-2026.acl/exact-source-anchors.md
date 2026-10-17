# Exact source anchors

## Selected mechanism

We introduce SILO-BENCH, a role-free benchmark for evaluating free-form collaboration under information silos.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.23; `paper/paper-acl2026.txt` marker `===== PDF p.23 =====` | system |
| Experimental setup | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/sfs/evaluate.py:8` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/msg/evaluate.py:8` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/broadcast/evaluate.py:8` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/metrics.py:16` | `_normalize_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/metrics.py:45` | `compute_success_rate` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/metrics.py:81` | `_longest_increasing_subsequence_length` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/msg/tools.py:13` | `tool_send_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/msg/tools.py:45` | `tool_receive_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/msg/tools.py:75` | `tool_wait` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/broadcast/tools.py:13` | `tool_broadcast_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/broadcast/tools.py:38` | `tool_receive_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/broadcast/tools.py:99` | `tool_list_agents` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/sfs/tools.py:12` | `_load_shared_kv` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/sfs/tools.py:20` | `_save_shared_kv` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/sfs/tools.py:27` | `tool_list_files` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/prompts.py:259` | `generate_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config.py:21` | `_find_config_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config.py:34` | `load_config` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `e74127782ed1c42fff474249961f022c063d76f2`. Paper page numbers refer to the fixed local proceedings PDF.
