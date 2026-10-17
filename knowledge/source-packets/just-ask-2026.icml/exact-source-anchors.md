# Exact source anchors

## Selected mechanism

Autonomous code agents built on large language models are reshaping software and AI development through tool use, long-horizon reasoning, and self-directed interaction.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | system |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.10; `paper/paper-icml2026.txt` marker `===== PDF p.10 =====` | analysis |
| Limitations or failure conditions | PDF p.25; `paper/paper-icml2026.txt` marker `===== PDF p.25 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/score_local_embeddings.py:34` | `load_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/score_local_embeddings.py:42` | `compute_similarity` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/score_local_embeddings.py:51` | `score_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/score_production_responses.py:42` | `get_embedding` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/score_production_responses.py:53` | `compute_similarity` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/score_production_responses.py:67` | `score_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run_full_agent_eval.py:145` | `TargetModel` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run_full_agent_eval.py:184` | `AgentEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run_full_agent_eval.py:403` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analyze_full_agent.py:10` | `load_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analyze_full_agent.py:15` | `analyze_single_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analyze_full_agent.py:58` | `compare_to_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analyze_prompts.py:13` | `analyze_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analyze_prompts.py:104` | `load_and_analyze_all` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analyze_prompts.py:138` | `print_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation.py:21` | `cross_validate` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation.py:84` | `check_self_consistency` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run_production_eval.py:168` | `get_openrouter_client` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `bc295b851302cab5fd11289bc4c3cd924d4f478e`. Paper page numbers refer to the fixed local proceedings PDF.
