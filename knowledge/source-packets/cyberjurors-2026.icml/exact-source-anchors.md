# Exact source anchors

## Selected mechanism

To bridge this gap, we introduce a pioneering task, E-commerce Dispute Verdicts (EDV), and present VerdictBench , a multimodal benchmark comprising 6,000 real-world cases designed to reflect crowdsourced jury decisions.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | framework |
| Experimental setup | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 5. Experiments |
| Results and ablations | PDF p.10; `paper/paper-icml2026.txt` marker `===== PDF p.10 =====` | 5.2. Ablation |
| Limitations or failure conditions | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_multi_agent_debate.py:37` | `load_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_multi_agent_debate.py:43` | `load_cases` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_multi_agent_debate.py:56` | `compute_accuracy` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi_agent_debate.py:30` | `MeanField` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi_agent_debate.py:42` | `MultiAgentDebateSystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/single_agent.py:15` | `AgentOpinion` | Pinned implementation entry for the selected mechanism. |
| `official-code/single_agent.py:23` | `SingleAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils_syh.py:13` | `load_real_cases` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils_syh.py:38` | `parse_case_to_standard_format` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils_syh.py:124` | `load_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/Social_Consensus.py:38` | `_ensure_cache_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/Social_Consensus.py:43` | `_normalize_entry` | Pinned implementation entry for the selected mechanism. |
| `official-code/Social_Consensus.py:96` | `_prepare_index` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/prompt.py:190` | `get_case_info_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/profiles/distribution.py:5` | `age_distribution` | Pinned implementation entry for the selected mechanism. |
| `official-code/profiles/distribution.py:18` | `init_atti_distribution` | Pinned implementation entry for the selected mechanism. |
| `official-code/profiles/distribution.py:26` | `conformity_distribution` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/network.py:9` | `create_graph` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `e4d7dac530ca8e37cd7f49e968601cf8335e2826`. Paper page numbers refer to the fixed local proceedings PDF.
