# Exact source anchors

## Selected mechanism

Accumulate successful programs, abstract recurring code into validated tools, and reuse both through a dual-library loop.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | approach |
| Experimental setup | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | experiments |
| Results and ablations | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/state.py:12` | `PipelineState` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:209` | `get_timestamp` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:212` | `get_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents.py:17` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents.py:37` | `ProgramGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents.py:87` | `QualityJudge` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:8` | `program_generation_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:105` | `quality_judge_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:271` | `cluster_analysis_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_metrics.py:13` | `fuzzy_match` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_metrics.py:46` | `MetricEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_metrics.py:241` | `print_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/config.py:9` | `PipelineConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/config.py:103` | `create_config_from_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/models.py:10` | `Question` | Pinned implementation entry for the selected mechanism. |
| `official-code/models.py:20` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/models.py:53` | `Example` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:14` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c49bd4de5c8ffea34b1ae669fe863f2219b2061d`. Paper page numbers refer to the fixed local proceedings PDF.
