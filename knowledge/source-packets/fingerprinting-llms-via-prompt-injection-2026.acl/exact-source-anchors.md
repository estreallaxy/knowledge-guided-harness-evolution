# Exact source anchors

## Selected mechanism

Retain fingerprint-prompt optimization and gray-box or black-box statistical verification; the mechanism modifies prompts and decision rules rather than model parameters.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Method |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.1 Experimental Setup |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 5.2 Main Results |
| Limitations or failure conditions | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/generate_adv_prompt.py:15` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate_adv_prompt.py:168` | `infer_model_tag` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate_adv_prompt.py:175` | `resolve_default_pairs_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/create_adv_prompt.py:36` | `GCGConfig_target` | Pinned implementation entry for the selected mechanism. |
| `official-code/create_adv_prompt.py:57` | `GCGResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/create_adv_prompt.py:65` | `AttackBuffer` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_test_prob.py:35` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_test_prob.py:132` | `infer_model_tag` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_test_prob.py:139` | `normalize_path_string` | Pinned implementation entry for the selected mechanism. |
| `official-code/detect_func.py:38` | `sequence_to_bits` | Pinned implementation entry for the selected mechanism. |
| `official-code/detect_func.py:46` | `compute_bitwise_accuracy` | Pinned implementation entry for the selected mechanism. |
| `official-code/detect_func.py:62` | `get_graybox_filtered_bits` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate_pairs.py:136` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate_pairs.py:184` | `infer_model_tag` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate_pairs.py:191` | `load_tokenizer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3e577f98b2bb64780ec2995b074c5aeec9b017e1`. Paper page numbers refer to the fixed local proceedings PDF.
