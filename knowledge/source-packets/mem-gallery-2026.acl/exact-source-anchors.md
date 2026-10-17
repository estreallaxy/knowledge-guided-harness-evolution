# Exact source anchors

## Selected mechanism

Thus, we introduce Mem-Gallery, a new benchmark for evaluating multimodal long-term conversational memory in MLLM agents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | architecture |
| Results and ablations | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/benchmark/memengine/memory/FUMemory.py:7` | `FUMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/STMemory.py:7` | `STMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/LTMemory.py:7` | `LTMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/BaseMemory.py:3` | `BaseMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/BaseMemory.py:34` | `ExplicitMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/BaseMemory.py:65` | `ImplicitMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/RFMemory.py:8` | `RFMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/MMFUMemory.py:7` | `MMFUMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/MMMemory.py:8` | `MMMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/NGMemory.py:8` | `NGMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/GAMemory.py:8` | `GAMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/UniversalRAGMemory.py:9` | `UniversalRAGMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/MGMemory.py:7` | `MGMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/memory/AUGUSTUSMemory.py:10` | `AUGUSTUSMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/function/UniversalRAGRetrieval.py:1` | `UniversalRAGRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/function/MultiModalRetrieval.py:7` | `MultiModalRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/function/Retrieval.py:6` | `BaseRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/memengine/function/Retrieval.py:37` | `LinearRetrieval` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a93959e1e978a6a7d77798ae92c2ffe41c538c62`. Paper page numbers refer to the fixed local proceedings PDF.
