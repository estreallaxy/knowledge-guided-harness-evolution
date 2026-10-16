# Exact source anchors

## Selected mechanism

Maintain an evolving context playbook through generator, reflector, and curator stages without weight updates.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | Method |
| Experimental setup | PDF p.11; `paper/paper-iclr2026.txt` marker `===== PDF p.11 =====` | experiments |
| Results and ablations | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | analysis |
| Limitations or failure conditions | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/utils.py:14` | `initialize_clients` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:52` | `get_section_slug` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:79` | `extract_boxed_content` | Pinned implementation entry for the selected mechanism. |
| `official-code/logger.py:15` | `log_llm_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/logger.py:32` | `log_bullet_usage` | Pinned implementation entry for the selected mechanism. |
| `official-code/logger.py:83` | `log_curator_operation_diff` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm.py:15` | `timed_llm_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/playbook_utils.py:13` | `parse_playbook_line` | Pinned implementation entry for the selected mechanism. |
| `official-code/playbook_utils.py:29` | `get_next_global_id` | Pinned implementation entry for the selected mechanism. |
| `official-code/playbook_utils.py:46` | `format_playbook_line` | Pinned implementation entry for the selected mechanism. |
| `official-code/ace/core/generator.py:12` | `Generator` | Pinned implementation entry for the selected mechanism. |
| `official-code/ace/core/reflector.py:12` | `Reflector` | Pinned implementation entry for the selected mechanism. |
| `official-code/ace/core/bulletpoint_analyzer.py:23` | `parse_playbook_line` | Pinned implementation entry for the selected mechanism. |
| `official-code/ace/core/bulletpoint_analyzer.py:64` | `BulletpointAnalyzer` | Pinned implementation entry for the selected mechanism. |
| `official-code/ace/core/curator.py:18` | `Curator` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/mind2web/data_processor.py:16` | `load_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/mind2web/data_processor.py:38` | `DataProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/mind2web2/data_processor.py:16` | `load_data` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `82709de050e1db6e6ef2f07bcb0393560b94992a`. Paper page numbers refer to the fixed local proceedings PDF.
