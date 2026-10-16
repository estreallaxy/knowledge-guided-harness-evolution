# Exact source anchors

## Selected mechanism

Enable KV reuse and parallel decoding for diffusion language models through a training-free inference path.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | method |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/fast_ddrive/eval/evaluate_waymo_metrics.py:74` | `extract_trajectory` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_ddrive/eval/evaluate_waymo_metrics.py:107` | `_finite_diff_velocity` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_ddrive/eval/evaluate_waymo_metrics.py:121` | `_finite_diff_accel` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/dream/model/configuration_dream.py:28` | `DreamConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/llada/model/configuration_llada.py:55` | `StrEnum` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/llada/model/configuration_llada.py:68` | `LayerNormType` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/llada/model/configuration_llada.py:97` | `ActivationType` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/eval.py:40` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/eval.py:50` | `Fast_dLLM_v2EvalHarness` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_dvlm/vlmeval_run.py:31` | `write_vlmeval_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_dvlm/vlmeval_run.py:72` | `Fast_dVLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_dvlm/vlmeval_run.py:363` | `_launch_vlmeval` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_ddrive/eval/waymo_rfs_utils.py:10` | `get_lat_lng_thresholds` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_ddrive/eval/waymo_rfs_utils.py:30` | `process_rater_specified_trajectories` | Pinned implementation entry for the selected mechanism. |
| `official-code/fast_ddrive/eval/waymo_rfs_utils.py:151` | `get_rater_feedback_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/llada/eval_llada.py:40` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/llada/eval_llada.py:50` | `LLaDAEvalHarness` | Pinned implementation entry for the selected mechanism. |
| `official-code/v1/dream/eval.py:51` | `Dream` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a9b81e4caa240c8cad4f7dc1889ff4852a0fca5b`. Paper page numbers refer to the fixed local proceedings PDF.
