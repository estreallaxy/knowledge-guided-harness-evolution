# Exact source anchors

## Selected mechanism

Based on an analysis of representative workload classes, we introduce invocation distance, a unified abstraction that estimates the relative order in which agents will issue future LLM requests.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | system |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/sgl-router/src/tool_parser/state.rs:41` | `new` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/state.rs:56` | `reset` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/state.rs:65` | `process_char` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/metrics.rs:13` | `default` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/metrics.rs:20` | `init_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/metrics.rs:240` | `start_prometheus` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/tests.rs:10` | `test_parse_state_new` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/tests.rs:21` | `test_parse_state_process_char` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/tests.rs:49` | `test_token_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/config/validation.rs:8` | `validate` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/config/validation.rs:36` | `validate_mode` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/config/validation.rs:103` | `validate_policy` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/traits.rs:22` | `detect_format` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/traits.rs:28` | `parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/traits.rs:31` | `is_complete` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/types.rs:52` | `iter_pairs` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/registry.rs:25` | `new` | Pinned implementation entry for the selected mechanism. |
| `official-code/sgl-router/src/tool_parser/registry.rs:31` | `new_for_testing` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7ef897eaedc16626a281ccfe0d453fae80251e8f`. Paper page numbers refer to the fixed local proceedings PDF.
