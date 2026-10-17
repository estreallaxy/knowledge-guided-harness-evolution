# Exact source anchors

## Selected mechanism

Retain the four-stage memory-processing interface—Prepare Memory, Compute Relevancy, Retrieval, and Apply to Inference—and its stage-wise profiling and heterogeneous dispatch logic.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Results and ablations | PDF p.14; `paper/paper-icml2026.txt` marker `===== PDF p.14 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/toolchain/backend/lib/python/rag_apply_memory.py:1` | `get_documents` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/rag_apply_memory.py:12` | `_has_chat_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/rag_apply_memory.py:21` | `_build_context_string` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/steps/memory_retrieval.h:40` | `MemoryRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/steps/memory_retrieval.h:159` | `TopKRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/steps/memory_retrieval.h:200` | `ThresholdRetrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/launch_bm25.py:7` | `fpga_retriever_setup` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/launch_bm25.py:200` | `fpga_retriver_launch` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/bm25_loader_xrt.py:65` | `Timer` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/bm25_loader_xrt.py:82` | `TermFreqEntry` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/backend/lib/python/bm25_loader_xrt.py:89` | `DocumentTermFrequencies` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/types/score.h:31` | `Score` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/types/score.h:41` | `VectorScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/types/score.h:78` | `MatrixScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/steps/compute_score.h:44` | `ComputeScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolchain/frontend/dev/steps/compute_score.h:172` | `InnerProductCompute` | Pinned implementation entry for the selected mechanism. |
| `official-code/p2p_comm/python_api/examples/gpu_to_fpga_demo.py:16` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/p2p_comm/python_api/examples/p2p_demo.py:17` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `71524a94fc48c08d349fcbc47ced6e51581754a6`. Paper page numbers refer to the fixed local proceedings PDF.
