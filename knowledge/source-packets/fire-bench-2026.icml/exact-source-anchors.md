# Exact source anchors

## Selected mechanism

We introduce FIRE-BENCH (Full-cycle Insight Rediscovery Evaluation), which instead asks agents to rediscover established, verifiable findings from recent, high-impact machine learning research.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Approach |
| Experimental setup | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | results |
| Limitations or failure conditions | PDF p.30; `paper/paper-icml2026.txt` marker `===== PDF p.30 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_agent.py:33` | `normalize_model_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_agent.py:40` | `update_config_toml` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_agent.py:63` | `run_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/claude/run.py:14` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/codex/run.py:16` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/openhands/run.py:12` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/simple/run.py:42` | `extract_code_blocks` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/simple/run.py:48` | `extract_conclusion` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/simple/run.py:55` | `run_code` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a7017c95f680ea233b76445c53fd5e56b48cc159`. Paper page numbers refer to the fixed local proceedings PDF.
