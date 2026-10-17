# Exact source anchors

## Selected mechanism

To this end, we propose IF-RewardBench, a comprehensive meta-evaluation benchmark for instruction-following that covers diverse instruction and constraint types.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-acl2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | System |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/metrics/analysis_overall_assessment.py:18` | `compute_elo_with_indices` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics/analysis_overall_assessment.py:44` | `get_model_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics/analysis_overall_assessment.py:52` | `get_constraint_count_bucket` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics/analysis_constraint_assessment.py:13` | `parse_critique` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics/analysis_constraint_assessment.py:39` | `verdict` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics/analysis_constraint_assessment.py:48` | `get_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/constraint_assessment_inference_vllm.py:9` | `parse_solution` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/constraint_assessment_inference_vllm.py:13` | `reconstruct` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/constraint_assessment_inference_vllm.py:24` | `build_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/overall_assessment_inference_vllm.py:10` | `build_prompt` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c192fe968c15520352c7e7d9a853a3900f612d06`. Paper page numbers refer to the fixed local proceedings PDF.
