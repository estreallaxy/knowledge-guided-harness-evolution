# Exact source anchors

## Selected mechanism

To address these challenges, we propose Knowledge-Centric Video Reconstruction (KCVR), a Plan-then-Generate neuro-symbolic framework that decouples epistemic planning from content generation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | 3.1 Framework |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 4.3 Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/evaluation/t5_eval_metrics_matrix.py:58` | `_load_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/t5_eval_metrics_matrix.py:63` | `_build_ctl_resources` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/t5_eval_metrics_matrix.py:86` | `_objectives_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/validate_metrics_discriminative.py:48` | `load_standard_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/validate_metrics_discriminative.py:60` | `load_raw_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/validate_metrics_discriminative.py:73` | `compute_metrics_for_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/stage3_inference/evaluate.py:32` | `evaluate_predictions` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/stage3_inference/evaluate.py:144` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/metric_utils.py:65` | `TriggeredConcept` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/metric_utils.py:74` | `KgEdges` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/metric_utils.py:81` | `CtlResources` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/stage0_prep/04_standardize_knowledge_graph.py:23` | `KcRow` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/stage0_prep/04_standardize_knowledge_graph.py:36` | `TpRow` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/stage0_prep/04_standardize_knowledge_graph.py:48` | `RelRow` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/stage0_prep/sg_planner_core.py:16` | `KnowledgeConcept` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a0b2fc070bec525d6db4804ebd49c57c09343103`. Paper page numbers refer to the fixed local proceedings PDF.
