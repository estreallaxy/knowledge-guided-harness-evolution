# Exact source anchors

## Selected mechanism

Retain runtime KV-cache decomposition, shared-base cache management, low-rank adapter-cache storage, and Flash-LoRA-Attention; existing adapters are inputs and are not trained by the selected mechanism.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | architecture |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/langchain/agents/agent_toolkits/conversational_retrieval/tool.py:5` | `create_retriever_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/agents/agent_toolkits/conversational_retrieval/openai_functions.py:17` | `_get_default_system_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/agents/agent_toolkits/conversational_retrieval/openai_functions.py:27` | `create_conversational_retrieval_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/retrievers/contextual_compression.py:13` | `ContextualCompressionRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/examples/legacy/seq2seq/old_test_fsmt_bleu_score.py:33` | `ModelEvalTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/agents/agent_toolkits/openapi/planner.py:54` | `_get_default_llm_chain` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/agents/agent_toolkits/openapi/planner.py:61` | `_get_default_llm_chain_factory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/agents/agent_toolkits/openapi/planner.py:68` | `RequestsGetToolWithParsing` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/tests/agents/test_search.py:23` | `DuckDuckGoSearchToolTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/chains/router/multi_retrieval_qa.py:21` | `MultiRetrievalQAChain` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/tests/agents/test_tools_common.py:38` | `create_inputs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/tests/agents/test_tools_common.py:58` | `output_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/tests/agents/test_tools_common.py:70` | `ToolTesterMixin` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/evaluation/agents/trajectory_eval_chain.py:39` | `TrajectoryEval` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/evaluation/agents/trajectory_eval_chain.py:48` | `TrajectoryOutputParser` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/langchain/evaluation/agents/trajectory_eval_chain.py:98` | `TrajectoryEvalChain` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/src/transformers/agents/evaluate_agent.py:22` | `classifier` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/transformers/src/transformers/agents/evaluate_agent.py:26` | `translator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `578ff6021127d827bc46e0b00b0f62b0c32dd56c`. Paper page numbers refer to the fixed local proceedings PDF.
