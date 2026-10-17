# Exact source anchors

## Selected mechanism

We propose STAR-KV, an adaptive low-rank KV cache compression framework with fine-grained rank control.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | approach |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 6. Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/check_compression.py:25` | `_align_up` | Pinned implementation entry for the selected mechanism. |
| `official-code/check_compression.py:29` | `_is_compressed` | Pinned implementation entry for the selected mechanism. |
| `official-code/check_compression.py:36` | `_infer_geometry` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:75` | `_get_ppl_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:101` | `evaluate_ppl` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:135` | `evaluate_lmeval` | Pinned implementation entry for the selected mechanism. |
| `official-code/soft_thres_layer.py:6` | `soft_thres_layer` | Pinned implementation entry for the selected mechanism. |
| `official-code/soft_thres_layer.py:18` | `soft_thres_func` | Pinned implementation entry for the selected mechanism. |
| `official-code/LlamaLoRaAttention_headwise.py:11` | `apply_rotary_pos_emb_custom` | Pinned implementation entry for the selected mechanism. |
| `official-code/LlamaLoRaAttention_headwise.py:20` | `LlamaCustomAttention` | Pinned implementation entry for the selected mechanism. |
| `official-code/latency.py:39` | `load_baseline` | Pinned implementation entry for the selected mechanism. |
| `official-code/latency.py:48` | `load_starkv` | Pinned implementation entry for the selected mechanism. |
| `official-code/latency.py:71` | `_time` | Pinned implementation entry for the selected mechanism. |
| `official-code/abx_rope_batched.py:34` | `apply_rotary_pos_emb_custom` | Pinned implementation entry for the selected mechanism. |
| `official-code/abx_rope_batched.py:44` | `set_random_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/abx_rope_batched.py:53` | `get_freq_multi_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/kv_quant.py:76` | `n_outlier` | Pinned implementation entry for the selected mechanism. |
| `official-code/kv_quant.py:84` | `block_hadamard` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7ac7611534ff611d303d1fc790027aecb2205177`. Paper page numbers refer to the fixed local proceedings PDF.
