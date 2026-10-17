# Exact source anchors

## Selected mechanism

To address this gap, we introduce Vision2Web, a hierarchical benchmark for visual website development, spanning from static UI-to-code generation, interactive multi-page frontend reproduction, to long-horizon full-stack website development.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 3.2. Design |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/vision2web/evaluation/visual_scorer.py:17` | `VisualScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/config.py:9` | `SandboxConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/config.py:17` | `InferenceConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/config.py:30` | `EvaluationConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/logger.py:10` | `setup_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/logger.py:57` | `get_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/logger.py:62` | `LoggerContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/dataset.py:10` | `Project` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/dataset.py:48` | `DatasetManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/evaluation/functional_tester.py:14` | `FunctionalTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/sandbox.py:25` | `SandboxManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/utils.py:13` | `build_claude_code_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/utils.py:85` | `build_codex_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/core/utils.py:112` | `build_openhands_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/inference/prompts.py:451` | `get_prompt_for_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/evaluation/engine.py:17` | `EvaluationEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/cli.py:18` | `cli` | Pinned implementation entry for the selected mechanism. |
| `official-code/vision2web/cli.py:43` | `inference` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d80a4a3d0ea7326541ad87314294269a633789e4`. Paper page numbers refer to the fixed local proceedings PDF.
