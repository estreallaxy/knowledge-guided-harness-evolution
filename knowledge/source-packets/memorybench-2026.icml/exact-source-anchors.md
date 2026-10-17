# Exact source anchors

## Selected mechanism

Therefore, we propose a user feedback simulation framework and a comprehensive benchmark covering multiple domains, languages, and types of tasks to evaluate the continual learning abilities of LLMsys.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 3.2. Experimental Setup |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agent/evaluators/writingprompts_evaluator.py:6` | `WritingPromptsEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/base_evaluator.py:5` | `EvaluationContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/base_evaluator.py:32` | `BaseEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/lexeval_evaluator.py:6` | `LexEvalEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/hellobench_evaluator.py:6` | `HelloBenchEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/nfcats_evaluator.py:5` | `NFCatsEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/evaluator_factory.py:13` | `EvaluatorFactory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/writingbench_evaluator.py:6` | `WritingBenchEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/ideabench_evaluator.py:6` | `IdeaBenchEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/judge_evaluator.py:6` | `JuDGEEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/jrel_evaluator.py:6` | `JRELEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/evaluators/limitgen_evaluator.py:6` | `LimitGenEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/mem0/embedchain/tests/evaluation/test_context_relevancy_metric.py:9` | `mock_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/mem0/embedchain/tests/evaluation/test_context_relevancy_metric.py:30` | `mock_context_relevance_metric` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/mem0/embedchain/tests/evaluation/test_context_relevancy_metric.py:36` | `test_context_relevance_init` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memoryos.py:12` | `MemoryOSAgentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/memoryos.py:27` | `MemoryOSAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/mem0/mem0/memory/memgraph_memory.py:29` | `MemoryGraph` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `247ba8c1e327fa297c0d57aaad0e3cbd66bac656`. Paper page numbers refer to the fixed local proceedings PDF.
