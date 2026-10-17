# Exact source anchors

## Selected mechanism

In this paper, we propose Threat2Traffic, a multi-agent framework that extracts sample-specific dependencies from threat intelligence, reconstructs tailored environments, and captures malware traffic.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | system |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Results |
| Limitations or failure conditions | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5. Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/Task1/agents/threat_intel_agent.py:10` | `ThreatIntelAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/agents/static_agent.py:10` | `StaticAnalysisAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/agents/behavior_agent.py:10` | `BehaviorAnalysisAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/agents/base_agent.py:33` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/orchestrator.py:27` | `Stage1Orchestrator` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/orchestrator.py:290` | `analyze_sample` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/models.py:10` | `NodeType` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/models.py:24` | `EdgeType` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/models.py:40` | `SourceType` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/invariants.py:11` | `InvariantViolationType` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/invariants.py:22` | `InvariantViolation` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/invariants.py:30` | `GraphInvariantChecker` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task2/schema/prompt_builder.py:14` | `PromptBuilder` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/evidence_graph/graph.py:19` | `EvidenceGraph` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task2/config.py:12` | `TencentCloudConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task2/config.py:20` | `QemuConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task2/config.py:28` | `Stage2Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/Task1/config.py:12` | `VTConfig` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d475a2d20f50abe19c14c04d86f8963bcfd1b21a`. Paper page numbers refer to the fixed local proceedings PDF.
