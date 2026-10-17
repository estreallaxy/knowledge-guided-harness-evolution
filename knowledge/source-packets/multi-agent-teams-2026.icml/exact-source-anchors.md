# Exact source anchors

## Selected mechanism

Multi-agent LLM systems are increasingly deployed as autonomous collaborators, where agents interact freely rather than execute fixed, pre-specified workflows.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Method |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Results |
| Limitations or failure conditions | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/test_agent.py:9` | `ContextualBackend` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_agent.py:22` | `_make_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_agent.py:32` | `test_agent_trajectory_independence_from_global` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_hle_text_only_eval.py:8` | `test_hle_task_initialization` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_hle_text_only_eval.py:30` | `test_hle_get_task_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_hle_text_only_eval.py:55` | `test_hle_get_ground_truth` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_multiple_choice_eval.py:10` | `DummyMultipleChoiceTask` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_multiple_choice_eval.py:31` | `test_normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_multiple_choice_eval.py:64` | `test_extract_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_short_answer_eval.py:10` | `ConcreteShortAnswerTask` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_short_answer_eval.py:17` | `TestCollaborativeShortAnswerTaskEvaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_math_eval.py:8` | `TestCollaborativeMathTaskEvaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/teamwork/agent.py:10` | `TeamAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/conftest.py:7` | `_ensure_project_on_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_conversation.py:5` | `test_trajectory_append_and_last_turn` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_conversation.py:17` | `test_trajectory_extend_multiple_turns` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_conversation.py:32` | `test_trajectory_from_dict` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_turn_scheduling.py:7` | `test_balanced_turn_schedule_consistent_order` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a8833a2c6322b78b68842ee4efc3ef11ae29fdc4`. Paper page numbers refer to the fixed local proceedings PDF.
