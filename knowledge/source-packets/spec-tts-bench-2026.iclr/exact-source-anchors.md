# Exact source anchors

## Selected mechanism

Benchmark inference-time speculative decoding policies under test-time scaling and expose accuracy, acceptance-rate, latency, and compute trade-offs without model fine-tuning.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | method |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/code/model/samd/tools/build_static_sam.py:18` | `tokenize_fn` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/recycling/kv_cache.py:4` | `KVCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/recycling/kv_cache.py:69` | `initialize_past_key_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/pia/kv_cache.py:4` | `KVCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/pia/kv_cache.py:69` | `initialize_past_key_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/samd/cache.py:7` | `SamdCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/samd/cache.py:36` | `SamdStaticCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/eagle3/kv_cache.py:4` | `KVCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/eagle3/kv_cache.py:69` | `initialize_past_key_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/pia/lookahead_cache.py:13` | `Node` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/pia/lookahead_cache.py:24` | `Tree` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/pia/lookahead_cache.py:367` | `LookaheadCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/samd/samd_config.py:10` | `SamdConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/samd/samd_config.py:52` | `ForwardType` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/samd/samd_config.py:58` | `ForwardState` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/rest/rest/model/kv_cache.py:6` | `KVCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/rest/rest/model/kv_cache.py:71` | `initialize_past_key_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/code/model/eagle3/configs.py:2` | `EConfig` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `6b33e4a780740b91249162a8f11202819bd7c852`. Paper page numbers refer to the fixed local proceedings PDF.
