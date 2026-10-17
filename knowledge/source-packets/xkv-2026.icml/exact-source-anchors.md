# Exact source anchors

## Selected mechanism

Motivated by this observation, we propose xKV, a post-training compression method that jointly factorizes grouped-layer KV-Cache into a shared low-rank subspace, substantially reducing KV-Cache memory.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | method |
| Experimental setup | PDF p.18; `paper/paper-icml2026.txt` marker `===== PDF p.18 =====` | experiments |
| Results and ablations | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 2. Analysis |
| Limitations or failure conditions | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 2.2. Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluate/evaluator.py:30` | `_is_custom_llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/evaluator.py:35` | `_model_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/evaluator.py:39` | `_hf_generate` | Pinned implementation entry for the selected mechanism. |
| `official-code/efficiency/tests/test_shadowkv_retrieval_correctness.py:36` | `_run_case` | Pinned implementation entry for the selected mechanism. |
| `official-code/efficiency/tests/test_shadowkv_retrieval_correctness.py:66` | `test_retrieval_selects_deliberately_relevant_chunks` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/get_multiturn_scores.py:9` | `extract_xkv_index` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/get_multiturn_scores.py:13` | `process_jsonl_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_cache_integration.py:21` | `cuda_device` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_cache_integration.py:28` | `test_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_cache_integration.py:40` | `cache_instance` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_cache_integration_pytest.py:21` | `device` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_cache_integration_pytest.py:27` | `test_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_cache_integration_pytest.py:40` | `TestCacheIntegration` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/eval_acc.py:55` | `seed_everything` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/eval_acc.py:65` | `DistConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/eval_acc.py:74` | `init_dist` | Pinned implementation entry for the selected mechanism. |
| `official-code/group_layers.py:9` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:12` | `get_obj_from_str` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `05d91ecb0d698279aa4220fda5d7a5108036d692`. Paper page numbers refer to the fixed local proceedings PDF.
