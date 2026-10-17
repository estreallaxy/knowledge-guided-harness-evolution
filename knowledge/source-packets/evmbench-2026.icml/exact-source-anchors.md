# Exact source anchors

## Selected mechanism

We introduce EVMbench, an evaluation that measures the ability of agents to detect, patch, and exploit smart contract vulnerabilities.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.11; `paper/paper-icml2026.txt` marker `===== PDF p.11 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Results |
| Limitations or failure conditions | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/project/common/nanoeval/nanoeval/metrics/agents.py:11` | `_compute_metrics_plus_outcome_aggregations` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/common/nanoeval/nanoeval/metrics/agents.py:47` | `get_summary_error_aware` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/paperbench/paperbench/solvers/basicagent/tools/base.py:11` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/paperbench/paperbench/solvers/basicagent/tools/base.py:45` | `ToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/paperbench/paperbench/solvers/basicagent/tools/basic.py:10` | `SubmitTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/paperbench/paperbench/solvers/basicagent/tools/basic.py:38` | `BashTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/paperbench/paperbench/solvers/basicagent/tools/basic.py:68` | `PythonTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/common/nanoeval/nanoeval/metrics/standard_test.py:13` | `test_metrics_handle_ragged_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/common/nanoeval/nanoeval/metrics/standard_test.py:130` | `test_compute_metrics_on_correctness_without_answer_groups` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/common/nanoeval/nanoeval/solvers/computer_tasks/demo/agent.py:13` | `demo` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/common/nanoeval/nanoeval/solvers/computer_tasks/demo/runtime.py:17` | `demo` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/evmbench/evmbench/agents/run.py:16` | `get_elapsed_time_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/evmbench/evmbench/agents/run.py:23` | `execute_agent_in_computer` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/evmbench/evmbench/agents/run.py:65` | `run_agent_in_computer` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/evmbench/evmbench/agents/agent.py:20` | `Agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/evmbench/evmbench/agents/agent.py:31` | `AgentOutput` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/evmbench/evmbench/agents/agent.py:36` | `AgentRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/project/common/nanoeval/nanoeval/metrics/standard.py:12` | `_validate_input_data` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b78dab1da774a6456b1ed9c48c9ff194ee3ff36d`. Paper page numbers refer to the fixed local proceedings PDF.
