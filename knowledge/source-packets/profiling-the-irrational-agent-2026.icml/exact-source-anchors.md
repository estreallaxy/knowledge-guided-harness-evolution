# Exact source anchors

## Selected mechanism

We propose an interpretable cognitive modeling framework that couples a controlled elicitation paradigm, the Contextual Iowa Gambling Task (C-IGT), with a Generalized Rescorla–Wagner (GRW) architecture to decompose behavior into measurable mechanisms.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | architecture |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/mab/cigt_environment.py:19` | `JailbreakEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analysis/metrics.py:15` | `SingleFileEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analysis/metrics.py:119` | `BatchAggregator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/analysis/metrics.py:199` | `MetricsCalculator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/config.py:17` | `GlobalConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/config.py:75` | `get_model_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/config.py:121` | `print_available_platforms` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/fitting/batch_fitter.py:12` | `batch_fit_cognitive_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/fitting/strategies.py:48` | `get_strategy_for_group` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mab/models.py:23` | `MockLLMClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mab/models.py:35` | `LLMClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/settings.py:59` | `load_dotenv` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/settings.py:80` | `get_api_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/settings.py:105` | `get_runtime_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/utils.py:14` | `set_debug_mode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/utils.py:25` | `get_log_level` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/utils.py:30` | `setup_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mab/runner.py:17` | `JailbreakProbeRunner` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `00c7b48813138aeb0f8118a9e2a87599d0392087`. Paper page numbers refer to the fixed local proceedings PDF.
