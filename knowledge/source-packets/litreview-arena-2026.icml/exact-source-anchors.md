# Exact source anchors

## Selected mechanism

We introduce LitReview Arena , a battle-style evaluation platform with a structured protocol tailored to literature review quality: domain experts with AI paper-writing experience compare anonymized drafts, are matched to topics within their expertise, and provide dimension-wise outcomes over five literature-review-specific criteria.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluator/context_cache.py:21` | `_sha16` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/context_cache.py:25` | `topic_fingerprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/context_cache.py:34` | `expert_outcomes_fingerprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/context_builder.py:69` | `_mmr_select` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/context_builder.py:105` | `_avg_pairwise` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/context_builder.py:121` | `ContextBuilder` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/simple_agent.py:12` | `SimpleAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/bt_model.py:16` | `BradleyTerryModel` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/naive_judge.py:18` | `NaiveContextBuilder` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/structure_utils.py:17` | `extract_skeleton_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/structure_utils.py:46` | `build_paragraph_network` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/structure_utils.py:80` | `compute_graph_similarity` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/utils.py:25` | `LLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/data_loader.py:18` | `battle_topic_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/data_loader.py:23` | `load_battle_ids_from_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/data_loader.py:47` | `load_battle_ids_from_aggregated_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/calibration_diversity_report.py:39` | `_mean` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluator/calibration_diversity_report.py:43` | `run_report` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `61516e8d1ae9e430ae0b5fa91aacb4fd7982fd4f`. Paper page numbers refer to the fixed local proceedings PDF.
