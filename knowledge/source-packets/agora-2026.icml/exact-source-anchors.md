# Exact source anchors

## Selected mechanism

We present Agora, a domain-aware multi-agent framework that integrates hypothesis-driven testing with LLM capabilities for systematic protocol verification.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | system |
| Experimental setup | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent/prompts/orchestrator.py:21` | `get_orchestrator_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_pattern_memory.py:7` | `test_pattern_memory_add_and_get` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_memory_persistence.py:10` | `test_repo_knowledge_persists` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_memory_persistence.py:41` | `test_create_memory_server_persists_paths` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_baseline_prompts.py:33` | `TestBaselineSystemPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_baseline_prompts.py:71` | `TestRepoCoreFiles` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_baseline_prompts.py:118` | `TestGetCoreFiles` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/utils/metrics.py:32` | `APICallRecord` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/utils/metrics.py:51` | `IterationMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/utils/metrics.py:68` | `SessionMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_orchestrator.py:34` | `MockOrchestrator` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_orchestrator.py:76` | `mock_orchestrator` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_orchestrator.py:86` | `mock_orchestrator_with_responses` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_tools.py:33` | `TestMemoryServerCreation` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_tools.py:70` | `TestPatternMemoryTools` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_tools.py:182` | `TestRepoKnowledgeTools` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_executor.py:28` | `TestExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tests/test_executor.py:175` | `TestErrorAnalysis` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `f93ffec09d3abec30b9d232e304ff3834560405f`. Paper page numbers refer to the fixed local proceedings PDF.
