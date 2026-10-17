# Exact source anchors

## Selected mechanism

To reconcile this conflict, we propose VIGIL , a framework that shifts the paradigm from restrictive isolation to a verify-before-commit protocol.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | System |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.1 Experimental Setup |
| Results and ablations | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | 5.3 Ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/vigil/goal_completion_evaluator.py:10` | `GoalCompletionEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/path_cache.py:9` | `VerifiedPath` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/path_cache.py:15` | `PathCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/enhanced_tools_loop.py:12` | `EnhancedToolsExecutionLoop` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/tool_sanitizer_element.py:18` | `ToolDocstringSanitizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/vigil_executor.py:15` | `vigil_tool_result_to_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/vigil_executor.py:21` | `VIGILToolsExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/vigil_executor.py:179` | `VIGILInitQuery` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/runtime_auditor.py:18` | `RuntimeAuditor` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/enhanced_executor.py:21` | `enhanced_tool_result_to_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/enhanced_executor.py:27` | `EnhancedVIGILToolsExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/enhanced_executor.py:1352` | `EnhancedVIGILInitQuery` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/config.py:5` | `VIGILConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/config.py:112` | `get_vigil_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/types.py:5` | `SecurityConstraint` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/types.py:20` | `ConstraintSet` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/types.py:30` | `AuditResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/vigil/conditional_llm.py:11` | `ConditionalLLM` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `af8eb9c70d32f8a3cc07b308e823c813b2285772`. Paper page numbers refer to the fixed local proceedings PDF.
