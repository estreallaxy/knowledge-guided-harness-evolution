# Exact source anchors

## Selected mechanism

To address these challenges, we introduce (1) VeRO (Versioning, Rewards, and Observations), an outer harness that provides versioned snapshots, budget-controlled evaluation, and structured execution traces of target harnesses , and (2) VeRO-Bench, a benchmark suite of target agents and tasks with reference evaluation procedures.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | framework |
| Experimental setup | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | experiments |
| Results and ablations | PDF p.13; `paper/paper-icml2026.txt` marker `===== PDF p.13 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/vero/examples/harbor-circle-packing/environment/sidecar/harness/evaluate.py:21` | `Validation` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/sidecar/harness/evaluate.py:31` | `_load_candidate` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/sidecar/harness/evaluate.py:40` | `_seed_runtime` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/vero-agents/agents/tau-bench/tau_bench/envs/airline/tools/search_direct_flight.py:9` | `SearchDirectFlight` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/vero-agents/agents/tau-bench/tau_bench/envs/airline/tools/search_onestop_flight.py:9` | `SearchOnestopFlight` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-seed/packing.py:16` | `construct_packing` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-seed/packing.py:43` | `compute_max_radii` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-seed/packing.py:58` | `run_packing` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-baseline/packing.py:16` | `construct_packing` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-baseline/packing.py:43` | `compute_max_radii` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-baseline/packing.py:58` | `run_packing` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/tools/planning.py:10` | `think` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/tools/planning.py:15` | `TodoStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/tools/planning.py:25` | `TodoList` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/tools/sub_agent.py:20` | `default_sub_agent_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/tools/sub_agent.py:34` | `SubAgentSession` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/tools/sub_agent.py:58` | `SubAgentTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/vero/src/vero/runtime/context.py:51` | `context_digest` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d1400011917ff66b7c122e7a787d547372f43e97`. Paper page numbers refer to the fixed local proceedings PDF.
