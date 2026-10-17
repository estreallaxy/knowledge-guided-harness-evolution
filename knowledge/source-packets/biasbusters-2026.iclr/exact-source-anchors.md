# Exact source anchors

## Selected mechanism

Measure provider-selection bias and apply inference-time tool presentation and selection controls; exclude model-training paths.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | approach |
| Experimental setup | PDF p.28; `paper/paper-iclr2026.txt` marker `===== PDF p.28 =====` | experiments |
| Results and ablations | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | results |
| Limitations or failure conditions | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/toolbench/retrieval/api_evaluator.py:42` | `compute_ndcg_for_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/retrieval/api_evaluator.py:58` | `APIEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators_comparison.py:18` | `get_most_preferred` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators_comparison.py:28` | `agreement_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators_comparison.py:37` | `get_correlation` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/__init__.py:7` | `load_registered_automatic_evaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/utils.py:12` | `register_evaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/utils.py:19` | `get_evaluator_cls` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/utils.py:29` | `OpenaiPoolRequest` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/base.py:7` | `process_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/base.py:14` | `process_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/base.py:21` | `BaseEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/tooleval.py:16` | `OpenAIEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/tooleval.py:50` | `OpenAINormalizedEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/rtl.py:16` | `AnswerStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/rtl.py:21` | `TaskStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/rtl.py:26` | `AnswerPass` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbench/model/compression.py:11` | `CompressionConfig` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `bdebc4ae796509222be24c7e985ebe183aa280f0`. Paper page numbers refer to the fixed local proceedings PDF.
