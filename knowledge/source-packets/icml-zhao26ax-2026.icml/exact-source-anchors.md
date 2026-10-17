# Exact source anchors

## Selected mechanism

To investigate this question, we propose SUSVIBES, a benchmark consisting of 186 feature-request software engineering tasks from real-world open-source projects, for which human programmers committed vulnerable implementations.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | method |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.1. Experimental Setup |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/susvibes/core/agents/sweagent.py:10` | `SWEAgentPort` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/agents/claude.py:83` | `is_transient_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/agents/claude.py:90` | `block_to_dict` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/agents/claude.py:103` | `message_to_dict` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/test_adapter.py:13` | `adapter_command` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/test_adapter.py:37` | `parse_adapter_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/test_counts.py:9` | `strip_ansi` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/test_counts.py:13` | `validated_test_counts` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/core/test_counts.py:82` | `parse_test_counts` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/curate/env_setup/dev_tools.py:35` | `prologue` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/curate/env_setup/dev_tools.py:65` | `epilogue` | Pinned implementation entry for the selected mechanism. |
| `official-code/susvibes/curate/env_setup/dev_tools.py:155` | `pipeline` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/agent_import.py:22` | `import_agent_module` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_safety_hint.py:9` | `test_hint_is_strategy_generic_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_safety_hint.py:14` | `test_hint_applied_to_plain_statement` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_safety_hint.py:21` | `test_hint_format_matches_strategy_pipeline` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_prompt_template.py:20` | `test_template_has_anti_cheating_block` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_prompt_template.py:26` | `test_template_has_six_step_workflow` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `520f16f9b3f39b06c6013bc0eb57a38280b4deee`. Paper page numbers refer to the fixed local proceedings PDF.
