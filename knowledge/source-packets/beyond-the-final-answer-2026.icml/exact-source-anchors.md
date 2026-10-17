# Exact source anchors

## Selected mechanism

In this manner, we introduce TRACE, a reference free framework for the multi-dimensional evaluation of tool-augmented LLMs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/trace.py:6` | `_calculate_efficiency_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace.py:32` | `trace` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:1` | `create_hallucination_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:55` | `create_inefficiency_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:113` | `create_adaptivity_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:7` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_client.py:29` | `generate_response` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `dd0b5e868e32f112623916e523bc49ca170b3699`. Paper page numbers refer to the fixed local proceedings PDF.
