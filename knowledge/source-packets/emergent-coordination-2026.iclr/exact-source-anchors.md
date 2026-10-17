# Exact source anchors

## Selected mechanism

Run prompt-steered multi-agent interactions and measure higher-order coordination with time-delayed information decomposition, without updating model parameters.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | design |
| Results and ablations | PDF p.18; `paper/paper-iclr2026.txt` marker `===== PDF p.18 =====` | results |
| Limitations or failure conditions | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/prompt_capture.py:6` | `PromptCapture` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt_capture.py:42` | `init_prompt_capture` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt_capture.py:47` | `capture_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/results_compresser.py:6` | `compress_folder_zip` | Pinned implementation entry for the selected mechanism. |
| `official-code/results_compresser.py:29` | `compress_folder_tar_xz` | Pinned implementation entry for the selected mechanism. |
| `official-code/persona_wrapper.py:4` | `PersonaWrapper` | Pinned implementation entry for the selected mechanism. |
| `official-code/extract_game_data_to_csv.py:5` | `extract_round_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/extract_game_data_to_csv.py:23` | `save_to_csv` | Pinned implementation entry for the selected mechanism. |
| `official-code/extract_game_data_to_csv.py:38` | `extract_game_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/results_visualization.py:7` | `parse_game_log` | Pinned implementation entry for the selected mechanism. |
| `official-code/results_visualization.py:23` | `collect_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/results_visualization.py:63` | `create_plots` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_experiment_multi_model.py:13` | `run_single_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_experiment_multi_model.py:38` | `create_fallback_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_experiment_multi_model.py:55` | `create_config_batches` | Pinned implementation entry for the selected mechanism. |
| `official-code/persona_experiment.py:12` | `PersonaAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/persona_experiment.py:102` | `PersonaGameMaster` | Pinned implementation entry for the selected mechanism. |
| `official-code/persona_experiment.py:142` | `run_single_config` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d260c20a12c78faecbadfd66c01e40d752194b80`. Paper page numbers refer to the fixed local proceedings PDF.
