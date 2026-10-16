# Exact source anchors

## Selected mechanism

Retrieve and retain useful KV-cache entries at inference time without training a new compressor.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | approach |
| Results and ablations | PDF p.13; `paper/paper-iclr2026.txt` marker `===== PDF p.13 =====` | analysis |
| Limitations or failure conditions | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/source/freekv_cpp/src/gen_dispatch.py:12` | `write_if_different` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv/kv_cache.py:10` | `PagePool` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv/kv_cache.py:45` | `KvPool` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv/kv_cache.py:77` | `KvCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv/infer_state.py:16` | `InferState` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/setup.py:9` | `CMakeExtension` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/setup.py:15` | `CMakeBuild` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/kvc/patch/tuple_kv_cache.py:29` | `_get_unpad_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/kvc/patch/tuple_kv_cache.py:43` | `old_flash_attention_2_forward` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/kvc/patch/tuple_kv_cache.py:150` | `_flash_attention_forward` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv_cpp/src/thread_pool.h:14` | `ThreadPool` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv_cpp/src/flashinfer_ops.h:95` | `BatchPrefillWithPagedKVCachePyTorchWrapper` | Pinned implementation entry for the selected mechanism. |
| `official-code/source/freekv_cpp/src/flashinfer_ops.h:119` | `BatchDecodeWithPagedKVCachePyTorchWrapper` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/eval/util.py:24` | `parse_common_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/eval/util.py:94` | `get_out_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/eval/util.py:165` | `build_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/eval/reasoning/eval.py:9` | `parse_agrs` | Pinned implementation entry for the selected mechanism. |
| `official-code/accuracy/eval/reasoning/eval.py:19` | `get_trimmed_average` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2c8a7d25c9f3c7c15ce15b2f84cd03f477bd7469`. Paper page numbers refer to the fixed local proceedings PDF.
