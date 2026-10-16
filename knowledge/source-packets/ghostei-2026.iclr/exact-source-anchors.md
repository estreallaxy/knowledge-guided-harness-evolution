# Exact source anchors

## Selected mechanism

Inject dynamic on-device environmental interference and measure whether mobile agents recognize and recover from it.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | framework |
| Results and ablations | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_appagent_hooks.py:36` | `load_run_configuration` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_appagent_hooks.py:53` | `load_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_appagent_hooks.py:59` | `_normalize_app_whitelist` | Pinned implementation entry for the selected mechanism. |
| `official-code/MobileAgent/prompt.py:1` | `get_action_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/MobileAgent/prompt.py:136` | `get_reflect_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/MobileAgent/prompt.py:191` | `get_memory_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/AppAgent/scripts/task_executor.py:117` | `area_to_xy` | Pinned implementation entry for the selected mechanism. |
| `official-code/AppAgent/scripts/config.py:5` | `load_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/gui_agent/test_loop_atlas.py:16` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/gui_agent/test_loop_atlas.py:29` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/gui_agent/test_loop_tars15.py:16` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/gui_agent/test_loop_tars15.py:29` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/gui_agent/test_loop_uitars.py:16` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/gui_agent/test_loop_uitars.py:29` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:52` | `build_overlay_trigger` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:80` | `build_popup_trigger` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:99` | `load_run_configuration` | Pinned implementation entry for the selected mechanism. |
| `official-code/MobileAgent/text_localization.py:6` | `order_point` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `459b3d84b79f05d48a4dbe330ea719b4e4715ab6`. Paper page numbers refer to the fixed local proceedings PDF.
