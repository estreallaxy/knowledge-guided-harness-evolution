# Exact source anchors

## Selected mechanism

Simulate user interaction, evaluate full traces, and attribute errors to actionable categories.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | framework |
| Results and ablations | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agent_inspect/metrics/scorer/tool_correctness.py:19` | `ToolCorrectnessMetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/metric.py:8` | `Metric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/llm_based_metric.py:11` | `LLMBasedMetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/auc.py:14` | `AUC` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/ppt.py:12` | `PPT` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/success.py:21` | `SuccessBasedMetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/success.py:114` | `SuccessScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/success.py:186` | `SuccessScoreFinalTurn` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/progress.py:25` | `ProgressBasedMetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/progress.py:52` | `ProgressScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_inspect/metrics/scorer/progress.py:176` | `ProgressScoresThroughTurns` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/environment/toolkit.py:17` | `ToolKitType` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/environment/toolkit.py:41` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/environment/toolkit.py:50` | `is_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/environment/tool.py:17` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/environment/tool.py:38` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/environment/tool.py:185` | `as_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_runners/tau2-bench/src/tau2/orchestrator/environment_manager.py:14` | `StartEnvironmentRequest` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `23c256af44af28f8f7b1b94be8acdb24c8ec80ea`. Paper page numbers refer to the fixed local proceedings PDF.
