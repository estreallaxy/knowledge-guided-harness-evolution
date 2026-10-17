# Exact source anchors

## Selected mechanism

We introduce CUDAnalyst, a unified analysis layer for controlled, generation-level attribution of planning decisions to feedback components via trajectory freezing and selective feedback injection.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.10; `paper/paper-icml2026.txt` marker `===== PDF p.10 =====` | framework |
| Results and ablations | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/cudanalyst/toolkit/grapher.py:31` | `Grapher` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/grapher.py:73` | `HostGrapher` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/grapher.py:166` | `KernGrapher` | Pinned implementation entry for the selected mechanism. |
| `official-code/demo.py:46` | `work` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/workflow.py:12` | `planning` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/workflow.py:16` | `intervene_sync` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/workflow.py:56` | `intervene_async` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/base.py:9` | `ToolContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/base.py:15` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/debugger.py:12` | `LintTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/debugger.py:68` | `SanitizeTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/profiler.py:14` | `PerfTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/analyzer.py:14` | `Element` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/analyzer.py:20` | `Param` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/toolkit/analyzer.py:36` | `Loop` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/module/prompts.py:5` | `PromptCfg` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/module/config.py:6` | `ModuleCfg` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cudanalyst/module/config.py:12` | `ModuleBits` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3c56c68775e8a7cf67e3fc935241030abb8822bb`. Paper page numbers refer to the fixed local proceedings PDF.
