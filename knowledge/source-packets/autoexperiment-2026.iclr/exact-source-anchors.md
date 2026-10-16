# Exact source anchors

## Selected mechanism

Evaluate research agents with progressive code masking so reproduction, adaptation, and independent replication remain distinguishable.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.14; `paper/paper-iclr2026.txt` marker `===== PDF p.14 =====` | experiments |
| Results and ablations | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | results |
| Limitations or failure conditions | PDF p.16; `paper/paper-iclr2026.txt` marker `===== PDF p.16 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/autoexperiment/agents/environment.py:16` | `add_env_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/environment.py:19` | `ACI` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/environment.py:27` | `EnvironmentStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/retrieval.py:18` | `Chunk` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/retrieval.py:23` | `CodeChunk` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/retrieval.py:34` | `TextChunk` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/memory.py:3` | `add_memory_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/memory.py:9` | `Memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/memory.py:31` | `FullMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/logger.py:6` | `create_log` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/logger.py:13` | `write_log` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/run.py:10` | `get_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/run.py:13` | `get_memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/run.py:23` | `get_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/run_refsol.py:7` | `run_refsol` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/run_refsol.py:13` | `command_line` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/verifier.py:14` | `get_combined_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/autoexperiment/agents/verifier.py:19` | `get_generated_codes` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `44c92e3ddc93f39dbe09352148fa9f9a59c1a60d`. Paper page numbers refer to the fixed local proceedings PDF.
