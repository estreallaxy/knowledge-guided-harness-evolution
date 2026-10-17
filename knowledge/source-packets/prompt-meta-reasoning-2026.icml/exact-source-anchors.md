# Exact source anchors

## Selected mechanism

To address these limitations, we propose the Meta-Reasoning Prompt Engineering Agent (MR.PEA), a self-supervised prompt optimization framework that operates with minimal input.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 4.3. Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agents/prompt_refinement_agent.py:10` | `PromptRefinementAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/web_search_agent.py:10` | `WebSearchAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/example_generation_agent.py:12` | `ExampleGenerationAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/evaluation_agent.py:10` | `EvaluationAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/base_agent.py:13` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/meta_decision_agent.py:11` | `MetaDecisionAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/persistent_memory.py:17` | `MemoryState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/persistent_memory.py:32` | `PersistentMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/abstraction_agent.py:11` | `AbstractionAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config_loader.py:14` | `load_main_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config_loader.py:34` | `get_default_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config_loader.py:91` | `load_prompt_configs` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:28` | `create_openai_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:50` | `create_linkup_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:70` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mrpea.py:19` | `MRPEAAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/eval_gsm8k.py:38` | `load_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/eval_gsm8k.py:44` | `load_prompt` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ad1d260a2922cc28f619f004dfe2f3a6f9af025d`. Paper page numbers refer to the fixed local proceedings PDF.
