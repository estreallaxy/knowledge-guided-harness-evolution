# Exact source anchors

## Selected mechanism

In this paper, we introduce EpiCache, a training-free KV cache management framework for long conversational question answering (LongConvQA) under fixed memory budgets.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | method |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.1. Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_gpt_eval.py:18` | `gpt_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_gpt_eval.py:60` | `evaluate_json_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_gpt_eval.py:122` | `print_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metric.py:9` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metric.py:46` | `rouge_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metric.py:55` | `f1_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/attention/score.py:12` | `KVScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/attention/kvcache.py:13` | `EvictCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/model/monkeypatch.py:9` | `replace_attn` | Pinned implementation entry for the selected mechanism. |
| `official-code/model/template.py:6` | `template` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/func.py:9` | `save_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/func.py:20` | `inplace_softmax` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/func.py:29` | `gmem` | Pinned implementation entry for the selected mechanism. |
| `official-code/model/load.py:10` | `get_model_id` | Pinned implementation entry for the selected mechanism. |
| `official-code/model/load.py:33` | `get_dtype` | Pinned implementation entry for the selected mechanism. |
| `official-code/model/load.py:44` | `load_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/csrc/build.py:28` | `get_cuda_bare_metal_version` | Pinned implementation entry for the selected mechanism. |
| `official-code/attention/attn.py:23` | `llama_flash_attn2_forward` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `e3b31e40ad45e7b1c0e596c731af1a5bf9b931ba`. Paper page numbers refer to the fixed local proceedings PDF.
