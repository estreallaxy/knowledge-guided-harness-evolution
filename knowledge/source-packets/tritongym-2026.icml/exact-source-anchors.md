# Exact source anchors

## Selected mechanism

We introduce TritonGym , a benchmark and orchestration framework for evaluating agentic workflows in GPU code generation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.1. Experimental Setup |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/benchmark/agents/base.py:7` | `GenerationResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/base.py:16` | `CodeGenAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/oneshot_agent.py:5` | `OneShotAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/alphaevolve_agent.py:10` | `AlphaEvolveAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/alphaevolve_agent.py:130` | `PromptDatabase` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/geak_agent.py:12` | `GeakAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/leader_agent.py:16` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/leader_agent.py:26` | `TaskState` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/leader_agent.py:38` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/clients/base.py:4` | `CodeGenClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/clients/meta_client.py:8` | `MetaClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/clients/anthropic_client.py:8` | `AnthropicClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/clients/deepseek_client.py:8` | `DeepSeekClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/data_v2/tests/attention_score.py:12` | `test_attention_score_compare` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/clients/openai_client.py:8` | `OpenAIClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/agents/clients/google_client.py:9` | `GoogleClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/tests/test_tools.py:8` | `_ensure_benchmark_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark/tests/test_tools.py:16` | `_Gen` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `5d646344c354228fe0d06480e0bd4cd0c8e9f423`. Paper page numbers refer to the fixed local proceedings PDF.
