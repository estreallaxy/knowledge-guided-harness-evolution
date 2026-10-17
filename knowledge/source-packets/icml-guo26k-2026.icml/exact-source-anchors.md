# Exact source anchors

## Selected mechanism

Retain the constrained-environment benchmark, upward-deception taxonomy, action-level indicators, and mitigation evaluation for agents facing unavailable tools or mismatched information.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.11; `paper/paper-icml2026.txt` marker `===== PDF p.11 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 3. Experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 4. Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluation.py:22` | `generate_random_content` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation.py:27` | `create_dummy_pptx` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation.py:55` | `_contains_semantic_char` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/incorrect_tools.py:11` | `unzip_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/incorrect_tools.py:33` | `speech_to_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/incorrect_tools.py:44` | `analyze_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/correct_tools.py:106` | `_encode_pillow_image_to_base64` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/correct_tools.py:116` | `_get_file_mime_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/correct_tools.py:122` | `speech_to_text` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b26151c7195111271feba64fb15db6227f25f51b`. Paper page numbers refer to the fixed local proceedings PDF.
