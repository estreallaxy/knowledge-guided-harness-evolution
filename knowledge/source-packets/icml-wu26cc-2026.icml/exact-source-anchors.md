# Exact source anchors

## Selected mechanism

In this paper, we propose a dynamic defense paradigm that models MAS communication as a signed directed acyclic graph and computes each agent’s contribution to the final decision via backward propagation, enabling accurate identification and isolation of malicious agents to secure multi-agent task collaboration.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | experiments |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4.2. Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run.py:15` | `load_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:20` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/graph.py:6` | `ChatTurn` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/graph.py:22` | `EdgeGraph` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/graph.py:50` | `run_round` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/prompts.py:51` | `_flatten` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/prompts.py:55` | `wrong_choice` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/prompts.py:59` | `start_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/llm.py:12` | `init_llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/llm.py:19` | `log_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/llm.py:25` | `ask` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/bpd.py:10` | `extract_choice` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/bpd.py:15` | `majority_choice` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/bpd.py:26` | `backward_propagate` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/runner.py:20` | `build_question` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/runner.py:27` | `_init_answers` | Pinned implementation entry for the selected mechanism. |
| `official-code/mas/runner.py:35` | `_first_answer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9e1619fedf6744a23264b4d27a2a4ab0aab7e53f`. Paper page numbers refer to the fixed local proceedings PDF.
