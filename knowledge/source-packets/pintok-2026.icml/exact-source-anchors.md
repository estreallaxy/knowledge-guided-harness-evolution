# Exact source anchors

## Selected mechanism

In this paper, we present the Pinned Tokenizer (PinTok), a novel tokenizer architecture that reduces redundant hardware, operating system, and networking overhead through three key innovations: core and memory pinning, scheduling and context switch avoidance, and duplicate network packet copy and processing avoidance.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/python/examples/agentic_app/rag_workflow.py:8` | `RAGWorkflow` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/config.py:4` | `Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/setup.py:12` | `run_command` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/setup.py:29` | `check_service` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/setup.py:50` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/test_components.py:13` | `test_vector_store` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/test_components.py:46` | `test_llm_service` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/test_components.py:81` | `test_rag_workflow` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/test_app.py:13` | `test_health` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/test_app.py:26` | `add_sample_documents` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/test_app.py:65` | `test_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/models.py:5` | `Document` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/models.py:11` | `DocumentResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/models.py:17` | `AddDocumentsRequest` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/llm_service.py:9` | `LLMService` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/vector_store.py:14` | `CustomEmbeddingFunction` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/vector_store.py:27` | `VectorStore` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/python/examples/agentic_app/utils.py:12` | `DocumentProcessor` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `92572ede9a9c17b7a14813c44449daee8514dac9`. Paper page numbers refer to the fixed local proceedings PDF.
