# Exact source anchors

## Selected mechanism

Building on this abstraction, we introduce an agentic system AOrchestra, where the central orchestrator concretizes the tuple at each step: it curates task-relevant context, selects tools and models, and delegates execution via on-the-fly automatic agent creation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | approach |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Limitations or failure conditions | PDF p.17; `paper/paper-icml2026.txt` marker `===== PDF p.17 =====` | DISCUSSION |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/benchmark/gaia/tools/google_search.py:14` | `GoogleSearchAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/base/agent/memory.py:12` | `Memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/aorchestra/tools/trace_formatter.py:12` | `StepLike` | Pinned implementation entry for the selected mechanism. |
| `official-code/aorchestra/tools/trace_formatter.py:21` | `ActionFormatter` | Pinned implementation entry for the selected mechanism. |
| `official-code/aorchestra/tools/trace_formatter.py:36` | `ObservationFormatter` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/gaia/tools/execute_code.py:11` | `ExecuteCodeAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/gaia/tools/extract_url_jina.py:17` | `ExtractUrlContentAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/gaia/tools/multimodal_toolkit.py:13` | `ImageAnalysisAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/gaia/tools/multimodal_toolkit.py:119` | `ParseAudioAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/terminalbench/docker_executor.py:16` | `DockerExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/aorchestra_gaia_agent.py:55` | `OrchestraGAIAAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/aorchestra_terminalbench_agent.py:71` | `ReAcTAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/aorchestra_swebench_agent.py:73` | `build_subagent_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/aorchestra_swebench_agent.py:108` | `parse_subagent_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/aorchestra_swebench_agent.py:232` | `SWEBenchSubAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/base/agent/base_action.py:6` | `BaseAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/aorchestra/tools/complete.py:12` | `CompleteTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/aorchestra/tools/submit.py:12` | `SubmitTool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `14a1a2051d6b03c479b706f8f555a60b8419e3b5`. Paper page numbers refer to the fixed local proceedings PDF.
