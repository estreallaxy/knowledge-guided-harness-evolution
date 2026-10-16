# Exact source anchors

## Selected mechanism

Adapt KV-cache allocation for diffusion language-model inference using attention-derived cache utility.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | method |
| Results and ablations | PDF p.28; `paper/paper-iclr2026.txt` marker `===== PDF p.28 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/dream/model/configuration_dream.py:28` | `DreamConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/model/configuration_llada.py:55` | `StrEnum` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/model/configuration_llada.py:68` | `LayerNormType` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/model/configuration_llada.py:97` | `ActivationType` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/eval_llada.py:47` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/eval_llada.py:57` | `LLaDAEvalHarness` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/eval.py:51` | `Dream` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/postprocess_code.py:26` | `pass_at_1` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/postprocess_code.py:36` | `read_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/postprocess_code.py:55` | `write_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/postprocess_code.py:26` | `pass_at_1` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/postprocess_code.py:36` | `read_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/postprocess_code.py:55` | `write_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/sanitize.py:31` | `refine_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/sanitize.py:36` | `syntax_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/dream/sanitize.py:45` | `extract_longest_valid_code` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/sanitize.py:32` | `refine_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/llada/sanitize.py:37` | `syntax_check` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1960d8fc6231205a1ae4ebba3898d475e339f7e1`. Paper page numbers refer to the fixed local proceedings PDF.
