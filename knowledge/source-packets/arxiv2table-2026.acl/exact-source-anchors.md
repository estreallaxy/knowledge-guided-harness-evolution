# Exact source anchors

## Selected mechanism

To support reproducible evaluation, we introduce arXiv2Table, a benchmark of 1,957 tables referencing 7,158 papers, with human-verified distractors and rewritten, schema-agnostic user demands.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | framework |
| Results and ablations | PDF p.24; `paper/paper-acl2026.txt` marker `===== PDF p.24 =====` | results |
| Limitations or failure conditions | PDF p.11; `paper/paper-acl2026.txt` marker `===== PDF p.11 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/benchmark_construction/parse_acl_paper.py:9` | `download_ACL_pdfs` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark_construction/parse_arxiv_paper.py:13` | `parse_table` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmark_construction/parse_arxiv_paper.py:35` | `parsing_ar5iv` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3e23a24fc27db4e980768e1b349ef3cff05b3d80`. Paper page numbers refer to the fixed local proceedings PDF.
