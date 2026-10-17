# Exact source anchors

## Selected mechanism

We introduce PSBench, the first benchmark specifically designed for image editing in Adobe Photoshop, consisting of 600 human-annotated tasks across three difficulty levels, with tasks drawn from official tutorials and popular real-world workflows.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/photoshop_evaluators.py:26` | `PhotoshopEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agent_base.py:10` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/llm_agents.py:17` | `ClaudeCUAAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/llm_agents.py:335` | `create_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_single_example.py:21` | `load_task_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_single_example.py:40` | `run_single_example` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_single_example.py:204` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:19` | `BenchmarkRunner` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:214` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/photoshop_env.py:29` | `PhotoshopProcessCrashedError` | Pinned implementation entry for the selected mechanism. |
| `official-code/photoshop_env.py:35` | `PhotoshopEnv` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `5a9a91119bc1fbbc03a4c4a86498741846f0fad1`. Paper page numbers refer to the fixed local proceedings PDF.
