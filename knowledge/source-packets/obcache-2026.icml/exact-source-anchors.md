# Exact source anchors

## Selected mechanism

We propose Optimal Brain Cache (OBCache), a principled framework that formulates cache eviction as a layer-wise structured pruning problem.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.20; `paper/paper-icml2026.txt` marker `===== PDF p.20 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluation/benchmarks/ruler/calculate_metrics.py:10` | `string_match_part` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/benchmarks/ruler/calculate_metrics.py:19` | `string_match_all` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/benchmarks/ruler/calculate_metrics.py:30` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/benchmarks/longbench/calculate_metrics.py:14` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/benchmarks/longbench/calculate_metrics.py:22` | `calculate_metrics_e` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/benchmarks/longbench/calculate_metrics.py:31` | `scorer_e` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/obcache_scorer.py:14` | `triton_is_available` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/obcache_scorer.py:18` | `require_triton` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/obcache_scorer.py:84` | `get_kernel_launch_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate.py:44` | `EvaluationConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate.py:188` | `_load_yaml_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate.py:198` | `_coerce_bool_config_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/scorer_press.py:17` | `ScorerPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/benchmarks/ruler/create_huggingface_dataset.py:39` | `get_dataframe` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/obcache_press.py:14` | `OBCacheScoringMixin` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/obcache_press.py:299` | `OBCacheObservedWindowPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/obcache_press.py:348` | `OBCacheSnapKVPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/utils.py:12` | `get_prerope_query_states` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `189ffadd7b2f29eaf311e67f39dbf2a26f5f4dd3`. Paper page numbers refer to the fixed local proceedings PDF.
