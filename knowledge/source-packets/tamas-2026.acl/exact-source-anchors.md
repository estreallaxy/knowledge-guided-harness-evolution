# Exact source anchors

## Selected mechanism

To address this gap, we introduce T hreats and A ttacks in M ulti- A gent S ystems ( TAMAS ), a benchmark designed to evaluate the robustness and safety of multi-agent LLM systems.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | system |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.3 Evaluation Setup |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 6 Results |
| Limitations or failure conditions | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/autogen_run.py:97` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/crewai_run.py:25` | `resolve` | Pinned implementation entry for the selected mechanism. |
| `official-code/crewai_run.py:186` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_dpi.py:10` | `eval_dpi` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_dpi.py:49` | `get_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_byzantine.py:13` | `eval_byzantine` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_contradicting.py:12` | `eval_contradicting` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_impersonation.py:12` | `is_refusal` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/eval_collusion.py:12` | `eval_colluding` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `545c112af9aab93b7ef2b0b60831d93c81c365c3`. Paper page numbers refer to the fixed local proceedings PDF.
