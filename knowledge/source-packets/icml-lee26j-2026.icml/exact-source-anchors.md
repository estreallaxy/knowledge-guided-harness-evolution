# Exact source anchors

## Selected mechanism

We present Stochastic Additive No-mulT Attention (SANTA), a method that sparsifies value-cache access by sampling $S \ll n_k$ indices from the post-softmax distribution and aggregates only those value rows.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | design |
| Results and ablations | PDF p.21; `paper/paper-icml2026.txt` marker `===== PDF p.21 =====` | 2025) results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tutorial_code/runtime_common.py:22` | `PreparedExample` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/runtime_common.py:34` | `PreparedBatch` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/runtime_common.py:57` | `ensure_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/santa_fused_proportional_tile_budgets/setup.py:11` | `_sanitize_arch_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/benchmark_longctx.py:40` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/benchmark_longctx.py:99` | `apply_quick_mode` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/benchmark_longctx.py:111` | `_canonical_outputs_field` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/compare_outputs.py:9` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/compare_outputs.py:20` | `normalize_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/compare_outputs.py:25` | `load_rows` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/env_utils.py:10` | `_normalize_mode` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/env_utils.py:17` | `_find_conda_runtime` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/env_utils.py:37` | `_split_env_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/inference_tutorial.py:30` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/inference_tutorial.py:77` | `read_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/inference_tutorial.py:83` | `smoke_test_backends` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/hf_generate_bridge.py:21` | `HFGenerateTrace` | Pinned implementation entry for the selected mechanism. |
| `official-code/tutorial_code/hf_generate_bridge.py:41` | `ensure_hf_custom_generate_available` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2e5f861196ec3d634d4b64729609fa7d687937b5`. Paper page numbers refer to the fixed local proceedings PDF.
