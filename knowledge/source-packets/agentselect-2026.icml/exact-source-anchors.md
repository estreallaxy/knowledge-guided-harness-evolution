# Exact source anchors

## Selected mechanism

We introduce AgentSelect, a benchmark that reframes agent selection as narrative query-to-agent recommendation over capability profiles.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Method |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experimental Setup |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | results |
| Limitations or failure conditions | PDF p.15; `paper/paper-icml2026.txt` marker `===== PDF p.15 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent_rec/graph_utils.py:23` | `GraphFeaturePack` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/graph_utils.py:32` | `build_graph_features` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:29` | `stable_seed_from_qid` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:36` | `build_aid_to_llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:47` | `evaluate_sampled_twotower` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/config.py:12` | `pos_topk_for_part` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/config.py:16` | `pos_topk_for_qid` | Pinned implementation entry for the selected mechanism. |
| `official-code/other/PartIII_Compositional_Agents_Process/partiii_compositional_agents/search.py:8` | `Search` | Pinned implementation entry for the selected mechanism. |
| `official-code/other/PartIII_Compositional_Agents_Process/partiii_compositional_agents/config.py:8` | `ProjectConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/rerank_eval_utils.py:26` | `EvalItem` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/rerank_eval_utils.py:34` | `build_agent_text_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/rerank_eval_utils.py:59` | `select_eval_qids` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/eval.py:20` | `_ideal_dcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/eval.py:25` | `_metrics_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_rec/eval.py:50` | `evaluate_sampled_knn_top10` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d33fdd4f1be6d6b050a3553b5c4977a7665d0d7b`. Paper page numbers refer to the fixed local proceedings PDF.
