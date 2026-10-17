# Exact source anchors

## Selected mechanism

Detect collective memory distortion and apply prompt-level cognitive anchoring and source-scrutiny controls.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.19; `paper/paper-iclr2026.txt` marker `===== PDF p.19 =====` | System |
| Results and ablations | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | analysis |
| Limitations or failure conditions | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eval_defense.py:91` | `get_all_tasks_from_data_folder` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_defense.py:110` | `check_if_output_exists` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_defense.py:143` | `process_single_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_correct.py:47` | `get_all_tasks_from_data_folder` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_correct.py:66` | `check_if_output_exists` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_correct.py:98` | `process_single_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:99` | `get_cycle_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:116` | `get_all_tasks_from_data_folder` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:134` | `check_if_output_exists` | Pinned implementation entry for the selected mechanism. |
| `official-code/format_data_bbh_correct.py:47` | `generate_agent_names` | Pinned implementation entry for the selected mechanism. |
| `official-code/format_data_bbh_correct.py:58` | `get_correct_guidance_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/format_data_bbh_correct.py:76` | `get_enriching_guidance_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:46` | `get_cached_model_and_tokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:104` | `add_retries` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:127` | `generate_gpt` | Pinned implementation entry for the selected mechanism. |
| `official-code/format_data_bbh_combined.py:82` | `assign_mandela_roles` | Pinned implementation entry for the selected mechanism. |
| `official-code/format_data_bbh_combined.py:288` | `get_role_specific_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/format_data_bbh_combined.py:472` | `generate_agent_names` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2688076944fb026cebc894c25f600627e325b8a8`. Paper page numbers refer to the fixed local proceedings PDF.
