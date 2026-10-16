# Exact source anchors

## Selected mechanism

Use an expert-inspired staged agent workflow, domain tools, and verification steps to turn observations into a checked solution.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | experiments |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_multi_agent_ir.py:30` | `topk_cosine_similarity` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_multi_agent_ir.py:83` | `parse_outputs` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils_table.py:7` | `validity_checker` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils_table.py:14` | `canonicalize_smiles` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils_table.py:24` | `get_scaffold` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_utils/random_split.py:10` | `seed_everything` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_utils/random_split.py:25` | `random_split` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_utils/preprocess_data.py:15` | `SMILESTokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_utils/preprocess_data.py:23` | `IRData` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_utils/preprocess_data.py:31` | `IRDataset` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3fe2635fa710bc82a84951293c69234da702feb9`. Paper page numbers refer to the fixed local proceedings PDF.
