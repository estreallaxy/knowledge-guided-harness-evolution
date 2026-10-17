# Exact source anchors

## Selected mechanism

Retain the Persistent Semantic Entity abstraction, name-binding and event-trigger probes, cross-session propagation tests, and context-isolated self-verification defense.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Design |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 6. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/python_harness/src/pse_harness/metrics/collectors.py:17` | `ExperimentMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/metrics/collectors.py:70` | `MetricsCollector` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/metrics/analysis.py:16` | `TestResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/metrics/analysis.py:38` | `StatisticalTests` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/metrics/analysis.py:165` | `MetricsAnalyzer` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/base.py:18` | `AgentStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/base.py:28` | `ToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/base.py:51` | `AgentStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/openai_agent.py:28` | `OpenAIAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/langchain_agent.py:29` | `convert_to_langchain_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/langchain_agent.py:44` | `LangChainAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/experiments/security_boundary.py:22` | `SecurityBoundaryExperiment` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/pse_agent.py:31` | `PseAgentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/pse_agent.py:38` | `PseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/agents/pse_agent.py:271` | `MultiAgentPseSystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/python_harness/src/pse_harness/tasks/tool_intensive.py:18` | `ToolIntensiveTaskGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/real_defense_evaluation.py:56` | `call_openai` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/real_defense_evaluation.py:72` | `call_ollama` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b228461bf010e53fe729f292078a770cb33752c7`. Paper page numbers refer to the fixed local proceedings PDF.
