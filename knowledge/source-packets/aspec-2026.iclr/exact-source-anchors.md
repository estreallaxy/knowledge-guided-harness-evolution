# Exact source anchors

## Selected mechanism

Persist task state and specialize an agent system at runtime while retaining an explicit adaptation history.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | system |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/aspec/meta/memory/scorer.py:17` | `SpecialistScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lib/tools/tool_utils.py:4` | `create_tool_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/backend.py:11` | `MemoryBackend` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/chat_history.py:13` | `ChatHistoryManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/schema.py:9` | `MemorySection` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/schema.py:26` | `classify_heading` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/schema.py:43` | `StructuredMemoryEntry` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lib/tools/tools_registry.py:69` | `_SafeEval` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lib/tools/tools_registry.py:95` | `MathCalculatorTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lib/tools/tools_registry.py:105` | `CodeExecutionTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/distiller.py:35` | `MemoryDistiller` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/parser.py:29` | `parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/parser.py:89` | `serialize` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/parser.py:115` | `extract_section` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/manager.py:26` | `SpecialistMemoryManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/store.py:30` | `resolve_memory_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/store.py:54` | `MemoryStore` | Pinned implementation entry for the selected mechanism. |
| `official-code/aspec/meta/memory/backends/markdown.py:14` | `MarkdownFileBackend` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `f34e038e65310b867c5bff3ef65c0d83b1c647eb`. Paper page numbers refer to the fixed local proceedings PDF.
