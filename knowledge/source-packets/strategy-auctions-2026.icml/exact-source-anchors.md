# Exact source anchors

## Selected mechanism

Small language models are viewed as a promising, cost-effective approach to agentic AI, yet how their performance scales with task complexity remains unclear.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Experimental setup | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 3. Experimental Setup |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 6. Results |
| Limitations or failure conditions | PDF p.41; `paper/paper-icml2026.txt` marker `===== PDF p.41 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/enrich_search_tasks.py:103` | `hf_token` | Pinned implementation entry for the selected mechanism. |
| `official-code/enrich_search_tasks.py:117` | `_auth_headers` | Pinned implementation entry for the selected mechanism. |
| `official-code/enrich_search_tasks.py:121` | `_resolve_url` | Pinned implementation entry for the selected mechanism. |
| `official-code/enrich_coding_tasks.py:90` | `hf_token` | Pinned implementation entry for the selected mechanism. |
| `official-code/enrich_coding_tasks.py:104` | `_auth_headers` | Pinned implementation entry for the selected mechanism. |
| `official-code/enrich_coding_tasks.py:108` | `_resolve_url` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `fbff975f6cd5e8e543f443b81e8f4a13e4805917`. Paper page numbers refer to the fixed local proceedings PDF.
