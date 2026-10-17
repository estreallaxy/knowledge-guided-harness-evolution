# Exact source anchors

## Selected mechanism

Retain the agent-oriented retrieval task taxonomy, task configurations, and evaluator covering code, tool, reasoning, and memory retrieval; no embedding model is trained.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.14; `paper/paper-icml2026.txt` marker `===== PDF p.14 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.21; `paper/paper-icml2026.txt` marker `===== PDF p.21 =====` | architecture |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | analysis |
| Limitations or failure conditions | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/mteb_patch/abstasks/memory_retrieval.py:38` | `MemoryRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/mteb_patch/tasks/mvrb_screenshot_retrieval.py:5` | `MVRBScreenshotRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/mteb_patch/tasks/mvrb_composed_screenshot_retrieval.py:5` | `MVRBComposedScreenshotRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_batch_aoeb.py:60` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_batch_aoeb.py:77` | `setup_logging` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_batch_aoeb.py:86` | `parse_task_configs` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_batch_mteb.py:133` | `build_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_batch_mteb.py:587` | `get_task_registry` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_batch_mteb.py:661` | `build_tasks` | Pinned implementation entry for the selected mechanism. |
| `official-code/mteb_patch/tasks/toolret.py:5` | `ToolRetRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/mteb_patch/tasks/longmemeval.py:6` | `LongMemEvalRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/data.py:9` | `IndexedMmapTarFile` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/model.py:7` | `InputType` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/model.py:12` | `EmbedderProtocol` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/model.py:26` | `MultimodalEmbedderProtocol` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/util.py:26` | `get_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/task.py:23` | `Modal` | Pinned implementation entry for the selected mechanism. |
| `official-code/aoeb_ng/task.py:32` | `RetrievalTask` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `259eb6eb89a2764a696fabd4b5ba9e6abb2f3670`. Paper page numbers refer to the fixed local proceedings PDF.
