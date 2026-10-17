# Exact source anchors

## Selected mechanism

To address these gaps, we introduce SWE-Compass, a comprehensive benchmark that unifies heterogeneous code-related evaluations into a structured and production-aligned framework.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Main Results |
| Limitations or failure conditions | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/swecompass/evaluators/configuration_deployment/eval_executor.py:22` | `log` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/configuration_deployment/eval_executor.py:27` | `parse_log` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/configuration_deployment/eval_executor.py:222` | `run_cmd` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/state.py:25` | `State` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/state.py:32` | `AgentState` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/state.py:129` | `auto_catch` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/setup.py:34` | `SetupAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/setup.py:55` | `SetupObservation` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/setup.py:62` | `SetupActionParser` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/verify.py:41` | `VerifyAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/verify.py:59` | `VerifyObservation` | Pinned implementation entry for the selected mechanism. |
| `official-code/launch/launch/agent/verify.py:65` | `VerifyActionParser` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/selected/eval_executor.py:22` | `log` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/selected/eval_executor.py:29` | `run_cmd` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/selected/eval_executor.py:49` | `docker_load_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/performance_optimization/eval_executor.py:25` | `log` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/performance_optimization/eval_executor.py:30` | `run_cmd` | Pinned implementation entry for the selected mechanism. |
| `official-code/swecompass/evaluators/performance_optimization/eval_executor.py:46` | `docker_load_image` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `f7d8e099581add4862ab2cef3a5a42f3f1251ca7`. Paper page numbers refer to the fixed local proceedings PDF.
