# Exact source anchors

## Selected mechanism

Maintain an active world model and persistent symbolic memory, generate reusable tools, and orchestrate their execution for long-horizon tasks.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Method |
| Results and ablations | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/roga/prompt/tool_validator.py:1` | `ToolValidatorPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/prompt/tool_wrapper.py:1` | `ToolWrapperPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/prompt/tool_generator.py:3` | `ToolGeneratorPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/tool/tool_searcher.py:20` | `MiniSentenceTransformer` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/tool/tool_searcher.py:38` | `ToolVectorSearcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/prompt/planner.py:3` | `PlannerPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/core/assistant.py:17` | `OpenAI` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/core/assistant.py:83` | `Assistant` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/core/assistant.py:139` | `Planner` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/core/sandbox.py:15` | `Sandbox` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/core/session.py:28` | `Session` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/init_tools/call_llm.py:16` | `call_llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/tool/tool_wrapper.py:9` | `ToolWrapper` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/init_tools/get_table_metadata.py:3` | `get_metadata` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/init_tools/table2md.py:6` | `table2md` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/init_tools/table2md.py:35` | `sheet2md` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/tool/tool_creator.py:20` | `ToolGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/roga/tool/tool_creator.py:48` | `ToolValidator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `0f007ccc04caf79bb59f1968d48f0dbc3f6aae0d`. Paper page numbers refer to the fixed local proceedings PDF.
