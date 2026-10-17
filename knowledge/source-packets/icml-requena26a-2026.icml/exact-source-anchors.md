# Exact source anchors

## Selected mechanism

We propose a minimal agentic baseline that enables systematic comparison across different AI-based theorem prover architectures.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 3. Architecture |
| Experimental setup | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 4. Experiments |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/unit/tools/test_lean_search.py:13` | `mock_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tools/test_lean_search.py:25` | `mock_session` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tools/test_lean_search.py:30` | `_build_post_cm` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/tools/web_search.py:20` | `SearchWebConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/tools/web_search.py:28` | `search_web` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/tools/web_search.py:83` | `SearchInput` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/tools/lean_search.py:26` | `SearchLeanSearchConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/tools/lean_search.py:39` | `lean_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/tools/lean_search.py:69` | `_lean_search_lifespan` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/evaluators.py:16` | `is_proven` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/evaluators.py:28` | `tool_usage` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/evaluators.py:59` | `number_of_iterations` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tools/test_registry.py:19` | `TestRegisterToolDecorator` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tools/test_registry.py:67` | `TestCreateTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tools/test_registry.py:169` | `TestCreateToolLifespans` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ax_prover/runtime.py:10` | `Runtime` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/test_evaluators.py:18` | `TestIsProven` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/test_evaluators.py:36` | `TestMetricEvaluators` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c8e845533d386e198b32fc3f00841fc3e77094c2`. Paper page numbers refer to the fixed local proceedings PDF.
