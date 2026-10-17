# Exact source anchors

## Selected mechanism

To study this setting, we introduce AgentWebBench, a benchmark that evaluates how well a user agent synthesizes answers by interacting with website-specific content agents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.16; `paper/paper-icml2026.txt` marker `===== PDF p.16 =====` | Method |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | analysis |
| Limitations or failure conditions | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | failure analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/awbench/agents/base.py:11` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/agents/llm_client.py:64` | `get_gemini_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/agents/llm_client.py:76` | `get_openai_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/agents/llm_client.py:86` | `get_hf_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/agents/content_agent.py:21` | `ContentAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/agents/user_agent.py:31` | `UserAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/doc_retrieval.py:8` | `query_docs` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_kpr_async.py:22` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_kpr_async.py:49` | `KeyPointRecall` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_kpr_async.py:54` | `evaluate_single_key_point` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_citation_clueweb_async.py:30` | `CitationSupportValues` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_citation_clueweb_async.py:43` | `CitationSupport` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_citation_clueweb_async.py:48` | `ClaimEntry` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_quality_async.py:48` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_quality_async.py:84` | `evaluate_single_criterion` | Pinned implementation entry for the selected mechanism. |
| `official-code/awbench/evaluation/deepresearchgym/eval_quality_async.py:100` | `evaluate_answer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `30a996e5eea5196e8881cd62272951da802b1462`. Paper page numbers refer to the fixed local proceedings PDF.
