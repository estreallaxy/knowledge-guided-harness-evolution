# Exact source anchors

## Selected mechanism

Guided by these insights, we propose a calibration-driven Interactive Learning Strategy (ILS) that selects clarification queries by optimizing calibration error, providing both theoretical guarantees and empirical gains for reliability.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.23; `paper/paper-acl2026.txt` marker `===== PDF p.23 =====` | System |
| Results and ablations | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | ablation |
| Limitations or failure conditions | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/utils/trace_writer.py:10` | `TraceWriter` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/trace_writer.py:26` | `sanitize_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/trace_writer.py:36` | `log_request` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config_loader.py:10` | `LLMConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/config_loader.py:25` | `load_llm_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/main.py:46` | `ILSPipelineConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/main.py:87` | `_js_divergence_local` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/main.py:104` | `select_question_random` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/LLM/PolicyLLM.py:16` | `PolicyLLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/LLM/ResponseLLM.py:17` | `ResponseLLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/utils.py:13` | `GeneratedSample` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/utils.py:19` | `render_prompt_with_fallback` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/utils.py:67` | `_safe_json_loads` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a01023107ca6c46ec5ea6cb131306f0035080d5c`. Paper page numbers refer to the fixed local proceedings PDF.
