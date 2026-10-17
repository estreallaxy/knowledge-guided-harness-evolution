# Exact source anchors

## Selected mechanism

We introduce ParisKV , a drift-robust, GPU-native KV-cache retrieval framework based on collision-based candidate selection, followed by a quantized inner-product reranking estimator.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | framework |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | experimental setup |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/cache_hub/collision_fused/collision_test.py:16` | `generate_test_input` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision_fused/collision_test.py:56` | `update_cache_cnt_overall_ref` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision_fused/collision_test.py:80` | `update_cache_cnt_ref` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/cache.py:4` | `KV_Cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/polar_cache.py:31` | `MultiDimBlockQuantizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/polar_cache.py:101` | `polar_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/polar_cache_atten_value_indices_adaptive_k.py:55` | `MultiDimBlockQuantizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/polar_cache_atten_value_indices_adaptive_k.py:142` | `polar_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/polar_cache_adaptivek_varlen.py:83` | `MultiDimBlockQuantizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/polar_cache_adaptivek_varlen.py:170` | `polar_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/gather/cpp_gather.py:11` | `load_gather_ext` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision_fused/collison_interface.py:9` | `_prepare_for_load` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision_fused/collison_interface.py:19` | `load_kernel_module` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision_fused/collison_interface.py:60` | `update_cache_cnt_cuda_interface` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision/collision.py:11` | `generate_test_input` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision/collision.py:29` | `update_cache_cnt_ref` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/collision/collision.py:49` | `_prepare_for_load` | Pinned implementation entry for the selected mechanism. |
| `official-code/cache_hub/gather_trans/trans_h2d.py:13` | `_prepare_for_load` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `db7ad7f59ebe5670f9f2e1092b1b689802dda7c5`. Paper page numbers refer to the fixed local proceedings PDF.
