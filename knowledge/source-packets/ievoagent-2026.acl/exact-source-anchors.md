# Exact source anchors

## Selected mechanism

Retain the conditional feedback distribution matrix and inference-time prompt-evolution mechanism driven by observed user reactions; exclude offline KTO alignment.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | 3 Method |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.1 Experimental Setup |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 5.2 Ablation |
| Limitations or failure conditions | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agent/memory/test.py:336` | `calculate_advanced_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/utils/reward.py:9` | `compute_reward` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/utils/rewardFeedback.py:1` | `feedback_reward` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/dialogTraj.py:5` | `DialogTraj` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/JS.py:247` | `normalize_matrix` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/JS.py:264` | `calculate_matrix_jsd` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/oneHeatMap.py:256` | `get_merged_df` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/oneHeatMap.py:280` | `plot_single_heatmap` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/utils/rewardMutualInfo.py:25` | `_get_embedder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/utils/rewardMutualInfo.py:32` | `load_local_embedder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/utils/rewardMutualInfo.py:45` | `_build_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/rewriter/prompt_rewriter.py:6` | `parse_ai_review` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/rewriter/prompt_rewriter.py:37` | `PromptRewriter` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/feedbackMatrix.py:176` | `FeedbackMatrixManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/calculateFeedbackMat.py:176` | `load_pairs_from_directory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/calculateFeedbackMat.py:262` | `build_contingency_table` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memory/calculateFeedbackMat.py:281` | `chi_square_and_cramers_v` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/WildBench/test_agent.py:16` | `test_agent` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c37e2f6c4e6643302b15bd74277feb075dbd6a58`. Paper page numbers refer to the fixed local proceedings PDF.
