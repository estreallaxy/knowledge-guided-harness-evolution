# Exact source anchors

## Selected mechanism

Score trace-level groundedness, recovery, and evidence calibration rather than relying only on final-answer accuracy.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.17; `paper/paper-iclr2026.txt` marker `===== PDF p.17 =====` | framework |
| Experimental setup | PDF p.15; `paper/paper-iclr2026.txt` marker `===== PDF p.15 =====` | 4 Experiments |
| Results and ablations | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Analysis |
| Limitations or failure conditions | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/setup.py:10` | `create_directories` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:24` | `install_dependencies` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:34` | `create_env_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace_eval/rerun_traces.py:23` | `StopOnSequence` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace_eval/rerun_traces.py:38` | `process_batch_local` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace_eval/rerun_traces.py:176` | `process_line` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace_eval/generate_traces.py:138` | `_convert_numpy_to_native` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace_eval/generate_traces.py:149` | `batch_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace_eval/generate_traces.py:177` | `execute_multi_turn` | Pinned implementation entry for the selected mechanism. |
| `official-code/annotation/prompts.py:1` | `generate_ontology_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/model_loading.py:9` | `_is_hf_model_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/model_loading.py:13` | `_maybe_actor_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/model_loading.py:20` | `_normalize_local_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/qa_em.py:19` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/qa_em.py:36` | `em_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/qa_em.py:49` | `subem_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/annotation/parser.py:7` | `parse_information` | Pinned implementation entry for the selected mechanism. |
| `official-code/annotation/parser.py:19` | `parse_sequences_str` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `afddcb3b0109eb7300971490a8fb857c442425c4`. Paper page numbers refer to the fixed local proceedings PDF.
