# Exact source anchors

## Selected mechanism

Retain the Bayesian orchestrator, specialist-agent coordination, and online reliability updates used at inference time; the selected orchestration does not pre-train or fine-tune a neural module.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | framework |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 6 Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/main.py:13` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_multiagent_llm.py:28` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_promptllm.py:22` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_coherence_agents.py:22` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_multiagent.py:22` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_rl_agents.py:22` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_gametheory_agents.py:26` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm/prompt_templates.py:7` | `PromptTemplates` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm/negotiator_multiagent.py:14` | `GameState` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm/negotiator_multiagent.py:25` | `DebtNegotiator` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/helpers.py:21` | `load_scenarios` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/helpers.py:91` | `save_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/helpers.py:96` | `json_serializer` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_baseline.py:22` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/statistical_analysis.py:11` | `bootstrap_ci` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/statistical_analysis.py:48` | `wilson_score_ci` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/statistical_analysis.py:82` | `analyze_negotiation_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/run_all_datasets.py:30` | `run_experiment_on_dataset` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `dc8d5dea42d52d6478410db706b167f769571b5d`. Paper page numbers refer to the fixed local proceedings PDF.
