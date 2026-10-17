# Exact source anchors

## Selected mechanism

To address this challenge, we propose EngiAgent, a multi-agent system with a fully connected coordinator that simulates expert workflows through specialized agents for problem analysis, modeling, verification, solving, and solution evaluation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | system |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | analysis |
| Limitations or failure conditions | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/EngiLLM_modeling_evaluator.py:38` | `EngiLLMModelingEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/EngiLLM_modeling_evaluator.py:1070` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/EngiLLM_modeling_evaluator.py:1137` | `EngiLLMReportEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_agents.py:11` | `MessageType` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_agents.py:19` | `Message` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_agents.py:37` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/hmml_retriever.py:16` | `HMMLMethod` | Pinned implementation entry for the selected mechanism. |
| `official-code/hmml_retriever.py:29` | `HMMLRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/hmml_retriever.py:166` | `DomainMatcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/specialized_agents.py:16` | `smart_escape_braces` | Pinned implementation entry for the selected mechanism. |
| `official-code/specialized_agents.py:120` | `call_gpt_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/specialized_agents.py:241` | `reset_token_usage` | Pinned implementation entry for the selected mechanism. |
| `official-code/json_tracking_manager.py:10` | `JSONTrackingManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/json_tracking_manager.py:213` | `JSONTrackingIntegrator` | Pinned implementation entry for the selected mechanism. |
| `official-code/json_tracking_manager.py:367` | `create_json_tracking_manager` | Pinned implementation entry for the selected mechanism. |
| `official-code/automated_engillm_pipeline.py:32` | `EngiLLMFileManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/automated_engillm_pipeline.py:174` | `AutomatedEngiLLMPipeline` | Pinned implementation entry for the selected mechanism. |
| `official-code/automated_engillm_pipeline.py:575` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1f104b36cea95e892ef247b0201f3ddc553f5e77`. Paper page numbers refer to the fixed local proceedings PDF.
