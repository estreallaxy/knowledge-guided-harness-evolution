# Exact source anchors

## Selected mechanism

To bridge this gap, we introduce PriAgent, a novel framework that approaches compliance auditing as a multi-stage, AI-driven reasoning task.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-aaai2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-aaai2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-aaai2026.txt` marker `===== PDF p.5 =====` | Experiments |
| Results and ablations | PDF p.6; `paper/paper-aaai2026.txt` marker `===== PDF p.6 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/workflow/priagent_graph.py:48` | `PriAgentState` | Pinned implementation entry for the selected mechanism. |
| `official-code/workflow/priagent_graph.py:76` | `SingleFlowState` | Pinned implementation entry for the selected mechanism. |
| `official-code/workflow/priagent_graph.py:87` | `node_flow_shaper` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/policy_scanner.py:19` | `_PolicyScanOutput` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/policy_scanner.py:50` | `PolicyScannerAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/code_summarizer.py:45` | `CodeSummarizerAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/code_tools.py:27` | `register_decompiled_code` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/code_tools.py:34` | `get_method_source` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/code_tools.py:61` | `count_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/compliance_arbiter.py:27` | `_ArbiterOutput` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/compliance_arbiter.py:74` | `_format_claims` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/compliance_arbiter.py:89` | `ComplianceArbiterAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/locus_finder.py:29` | `_LocusItem` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/locus_finder.py:41` | `_LocusFinderOutput` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/locus_finder.py:82` | `_dynamic_tau` | Pinned implementation entry for the selected mechanism. |
| `official-code/memory/audit_memory.py:28` | `_SummaryBufferMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/memory/audit_memory.py:71` | `AuditMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/flow_shaper.py:29` | `_extract_package` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b4b863d022a4226cac2a41292f9d3cba1348b356`. Paper page numbers refer to the fixed local proceedings PDF.
