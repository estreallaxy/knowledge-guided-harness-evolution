# Exact source anchors

## Selected mechanism

Run an adaptive red-team agent with reusable attack memory, executable tools, sandboxing, and outcome verification.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | system |
| Experimental setup | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | experiments |
| Results and ablations | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/filter_inputs.py:8` | `execute` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/filter_inputs.py:17` | `write` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/sanitize.py:20` | `remove_unindented_lines` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/sanitize.py:45` | `to_four_space_indents` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/render.py:16` | `analyze_resfile` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/render.py:53` | `align_ampersands` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/render.py:85` | `texprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/viz_passrate.py:31` | `passk_rel_drop` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/viz_passrate.py:87` | `get_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/utils.py:15` | `get_problems` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/utils.py:19` | `get_task_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/utils.py:24` | `to_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v016.py:4` | `check_id` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v016.py:8` | `check_valid` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v016.py:20` | `fix` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v013.py:1` | `check_id` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v013.py:5` | `fix` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v015.py:4` | `check_id` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7448982e2c47422c3b5eb5a184b7665696750e14`. Paper page numbers refer to the fixed local proceedings PDF.
