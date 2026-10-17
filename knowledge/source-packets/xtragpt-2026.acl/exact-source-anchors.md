# Exact source anchors

## Selected mechanism

To address these scenarios, we propose a human-AI collaboration framework for academic paper revision, centered on criteria-guided intent alignment and context-aware modeling.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | method |
| Experimental setup | PDF p.4; `paper/paper-acl2026.txt` marker `===== PDF p.4 =====` | Experimental Setup |
| Results and ablations | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 4.5 Ablation |
| Limitations or failure conditions | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/paper_revision_bench/paper_revision_bench/metrics/__init__.py:37` | `_result_to_alpaca_df` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/metrics/__init__.py:58` | `get_length_controlled_winrate` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/metrics/__init__.py:101` | `compute_weighted_overall` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/metrics/glm_winrate.py:53` | `_convert_to_dataframe` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/metrics/glm_winrate.py:59` | `_load_or_convert_to_dataframe` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/metrics/glm_winrate.py:70` | `_get_winrate` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/openclaw-demo/extract_paper.py:19` | `between` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/openclaw-demo/run_demo.py:65` | `load_skill` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/openclaw-demo/run_demo.py:70` | `render_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/openclaw-demo/run_demo.py:83` | `call_backend` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/paper_prompts.py:73` | `get_paper_eval_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/paper_revision_bench/paper_prompts.py:91` | `list_paper_sections` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference_example.py:10` | `load_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference_example.py:22` | `revise_paper_section` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference_example.py:83` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/examples/async_batch.py:10` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/examples/reproduce_xtragpt.py:11` | `load_predictions` | Pinned implementation entry for the selected mechanism. |
| `official-code/paper_revision_bench/examples/reproduce_xtragpt.py:24` | `load_prompts` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9f4be5c69878b16b5836a3769745bd190b585572`. Paper page numbers refer to the fixed local proceedings PDF.
