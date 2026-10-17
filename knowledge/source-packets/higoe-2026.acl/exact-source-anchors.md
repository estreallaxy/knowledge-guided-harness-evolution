# Exact source anchors

## Selected mechanism

To overcome these challenges, we introduce Hierarchical Graph of Evidence (HiGoE) (Code link https://github.com/tkw123/HiGOE ).

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | method |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 4.2 Ablation |
| Limitations or failure conditions | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/retrieval.py:8` | `get_dense_retriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/retrieval.py:18` | `split_batch` | Pinned implementation entry for the selected mechanism. |
| `official-code/retrieval.py:34` | `get_dense_embedding` | Pinned implementation entry for the selected mechanism. |
| `official-code/graph_construction.py:25` | `rag_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/graph_construction.py:40` | `mem_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/graph_construction.py:63` | `get_node_embedding_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/sum_eval.py:9` | `bert_score_eval` | Pinned implementation entry for the selected mechanism. |
| `official-code/sum_eval.py:19` | `rouge_eval` | Pinned implementation entry for the selected mechanism. |
| `official-code/sum_eval.py:48` | `response_eval` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:18` | `ImprovedGAT` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:81` | `GoR` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:267` | `infer_node_embedding` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_process.py:5` | `clean_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_process.py:19` | `qm_process_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_process.py:38` | `booksum_process_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:14` | `show_time` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `6761610ffeabc51dc8d881d8dd6d8689504683e0`. Paper page numbers refer to the fixed local proceedings PDF.
