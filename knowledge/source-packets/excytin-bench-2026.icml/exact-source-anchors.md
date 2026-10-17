# Exact source anchors

## Selected mechanism

We present ExCyTIn-Bench, the first benchmark to Evaluate an LLM agent X on the task of Cyber Threat Investigation through security questions derived from investigation graphs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experiments |
| Results and ablations | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/secgym/agents/prompt_sauce_agent.py:55` | `PromptSauceAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/prompt_sauce_reflexion_agent.py:55` | `PromptSauceReflexionAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:8` | `parse_requirements` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/agent.py:8` | `Agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/agent_utils.py:15` | `msging` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/agent_utils.py:18` | `sql_parser` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/agent_utils.py:38` | `call_llm_foundry` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/expel_agent.py:43` | `ExpelAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/maset_slave_agent.py:43` | `MultiModelBaselineAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/react_agent.py:58` | `ReActAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/react_reflexion_agent.py:67` | `ReActReflexionAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/baseline_agent.py:65` | `BaselineAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/expel_train/experience_recall.py:13` | `format_context` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/expel_train/experience_recall.py:25` | `ExperiencePool` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/expel_train/insight_extraction.py:21` | `parse_arguments` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/expel_train/insight_extraction.py:172` | `ActionType` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/agents/expel_train/insight_extraction.py:181` | `Action` | Pinned implementation entry for the selected mechanism. |
| `official-code/secgym/evaluator.py:180` | `Evaluator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a1b234f7a846133f08b7b5e1614c5c63b96f3b5c`. Paper page numbers refer to the fixed local proceedings PDF.
