# Exact source anchors

## Selected mechanism

To this end, we introduce Rule2DRC, a large-scale benchmark for DRC script coding agents with 1,000 rule-to-script tasks and 13,921 evaluation chip layouts for execution-based scoring.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | design |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5.5. Ablation |
| Limitations or failure conditions | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/bon_scores.py:18` | `_read_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/bon_scores.py:25` | `_read_json_any` | Pinned implementation entry for the selected mechanism. |
| `official-code/bon_scores.py:34` | `_cand_dirs` | Pinned implementation entry for the selected mechanism. |
| `official-code/score_llm_judge.py:24` | `_read_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/score_llm_judge.py:34` | `_write_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/score_llm_judge.py:39` | `_append_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/make_prompt.py:11` | `find_problem_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/make_prompt.py:26` | `render_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/make_prompt.py:38` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:30` | `eval_problem` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:116` | `_eval_worker` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:128` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/gen_tests.py:15` | `_load_render_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/gen_tests.py:21` | `log` | Pinned implementation entry for the selected mechanism. |
| `official-code/gen_tests.py:27` | `collect_problem_dirs` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/gds_to_text.py:9` | `_layer_indices` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/gds_to_text.py:17` | `_layer_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/gds_to_text.py:22` | `_pts` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8ad1cd5553b9876e9c0ee2a527450be4bf614a74`. Paper page numbers refer to the fixed local proceedings PDF.
