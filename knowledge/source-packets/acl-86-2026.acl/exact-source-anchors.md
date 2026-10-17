# Exact source anchors

## Selected mechanism

To address these challenges, we propose SpreadsheetAgent, a two-stage multi-agent framework for spreadsheet understanding that adopts a step-by-step reading and reasoning paradigm.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | approach |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | results |
| Limitations or failure conditions | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 3.3 Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/core/solver/metrics/base_metric.py:3` | `BaseMetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/qa_metrics.py:12` | `process_decimal` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/qa_metrics.py:23` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/qa_metrics.py:41` | `word_level_f1_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/metric/exact_match/exact_match.py:87` | `ExactMatch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/metric/rouge/rouge.py:83` | `Tokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/metric/rouge/rouge.py:94` | `Rouge` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/solver/metrics/metric/sacrebleu/sacrebleu.py:106` | `Sacrebleu` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/code_exec_docker/api.py:26` | `cleanup_kernels` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/code_exec_docker/api.py:53` | `async_cleanup_kernels` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/code_exec_docker/api.py:56` | `ExecuteHandler` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/code_exec_docker/jupyter.py:18` | `strip_ansi` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/code_exec_docker/jupyter.py:52` | `JupyterKernel` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/code_exec_docker/jupyter.py:237` | `JupyterGatewayDocker` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/eval/spreadsheet.py:13` | `datetime_to_float` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/eval/spreadsheet.py:19` | `transform_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/eval/spreadsheet.py:34` | `compare_cell_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/extractor/desc_verify.py:40` | `YamlDescVerifyStructureExtractor` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b4ded1ebdb73ab66acfa8439ad2af54470e317e3`. Paper page numbers refer to the fixed local proceedings PDF.
