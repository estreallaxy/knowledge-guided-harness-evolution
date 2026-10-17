# Exact source anchors

## Selected mechanism

We introduce CloneMem, a benchmark for evaluating long-term memory in AI Clone scenarios grounded in non-conversational digital traces, including diaries, social media posts, and emails, spanning one to three years.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 5 Experimental Setup |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 6.1 Main Results |
| Limitations or failure conditions | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | 7 Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/clonemem-eval/eval/compute_auto_metrics_for_clonemem.py:14` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/compute_auto_metrics_for_clonemem.py:27` | `load_ground_truth` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/compute_auto_metrics_for_clonemem.py:41` | `compute_metrics_for_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/compute_llm_metrics_for_clonemem.py:17` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/compute_llm_metrics_for_clonemem.py:114` | `load_ground_truth` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/compute_llm_metrics_for_clonemem.py:125` | `extract_json_from_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/analysis/visualize_all_metrics.py:12` | `plot_llm_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/analysis/visualize_all_metrics.py:105` | `plot_recall_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/analysis/visualize_all_metrics.py:204` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/analysis/aggregate_metrics_by_category.py:17` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/analysis/aggregate_metrics_by_category.py:30` | `load_all_qa_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval/analysis/aggregate_metrics_by_category.py:54` | `compute_metrics_for_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/embedding_retriever.py:16` | `FlexibleEmbeddingRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem/common/config.py:9` | `load_yaml` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem/common/config.py:17` | `load_dotenv_required` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem/common/config.py:24` | `require_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval_oracle.py:16` | `process_user` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/clonemem-eval/eval_oracle.py:107` | `process_user_wrapper` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `753d8a97fd78f4ee25af398a0f0c8d981a6be304`. Paper page numbers refer to the fixed local proceedings PDF.
