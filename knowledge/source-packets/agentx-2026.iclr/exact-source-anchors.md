# Exact source anchors

## Selected mechanism

Evaluate multi-step vision-centric agent trajectories with multimodal tools and step-level reasoning evidence.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Method |
| Experimental setup | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | 4.1 Experimental Setup |
| Limitations or failure conditions | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agentlego/agentlego/tools/search/google.py:10` | `GoogleSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/open_source_models/InternVL/clip_benchmark/clip_benchmark/metrics/zeroshot_retrieval.py:8` | `evaluate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/open_source_models/InternVL/clip_benchmark/clip_benchmark/metrics/zeroshot_retrieval.py:93` | `dataloader_with_indices` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/open_source_models/InternVL/clip_benchmark/clip_benchmark/metrics/zeroshot_retrieval.py:102` | `recall_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/open_source_models/InternVL/internvl_chat/tools/reasoning_data_pipeline/utils/accuracy_reward.py:8` | `EvalAIAnswerProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/open_source_models/InternVL/internvl_chat/tools/reasoning_data_pipeline/utils/accuracy_reward.py:222` | `TextVQAAccuracyEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/scripts/open_source_models/InternVL/internvl_chat/tools/reasoning_data_pipeline/utils/accuracy_reward.py:266` | `isfloat` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/testing/setup_tool.py:7` | `setup_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/opencompass/tools/prompt_viewer.py:18` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/opencompass/tools/prompt_viewer.py:37` | `parse_model_cfg` | Pinned implementation entry for the selected mechanism. |
| `official-code/opencompass/tools/prompt_viewer.py:44` | `parse_dataset_cfg` | Pinned implementation entry for the selected mechanism. |
| `official-code/opencompass/opencompass/metrics/mme_score.py:10` | `MMEMetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/tools/base.py:10` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/tools/func.py:11` | `_FuncTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/tools/func.py:26` | `_FuncToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/tools/func.py:56` | `make_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/tools/remote.py:16` | `RemoteTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentlego/agentlego/tools/image_canny/image_to_canny.py:8` | `ImageToCanny` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1dcd5a66267f0582898c692a5eef9d4a52d0dc2f`. Paper page numbers refer to the fixed local proceedings PDF.
