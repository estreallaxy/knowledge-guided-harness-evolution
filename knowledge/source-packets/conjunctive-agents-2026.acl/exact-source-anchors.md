# Exact source anchors

## Selected mechanism

Most LLM safety work studies single-agent models, but many real applications rely on multiple interacting agents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/system_defenses.py:12` | `authorize_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/system_defenses.py:17` | `least_privilege_segment` | Pinned implementation entry for the selected mechanism. |
| `official-code/system_defenses.py:22` | `enforce_json_schema` | Pinned implementation entry for the selected mechanism. |
| `official-code/simulate_agents.py:20` | `run_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/simulate_agents.py:24` | `apply_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/simulate_agents.py:37` | `build_agent_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation.py:12` | `activation_predicate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation.py:21` | `_surrogate_from_both_records` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation.py:43` | `evaluate` | Pinned implementation entry for the selected mechanism. |
| `official-code/topology.py:3` | `star` | Pinned implementation entry for the selected mechanism. |
| `official-code/topology.py:6` | `chain` | Pinned implementation entry for the selected mechanism. |
| `official-code/topology.py:13` | `dag` | Pinned implementation entry for the selected mechanism. |
| `official-code/models.py:8` | `load_generator` | Pinned implementation entry for the selected mechanism. |
| `official-code/routing.py:7` | `make_segments` | Pinned implementation entry for the selected mechanism. |
| `official-code/routing.py:21` | `_clamp01` | Pinned implementation entry for the selected mechanism. |
| `official-code/routing.py:25` | `route_segment` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_p1.py:11` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_p2.py:15` | `pearson_r` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2373a4f3f49bd37f45edfe59c2b1d6f315526b18`. Paper page numbers refer to the fixed local proceedings PDF.
