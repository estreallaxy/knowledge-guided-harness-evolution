# Exact source anchors

## Selected mechanism

We present CausalTrace , a detection system that reframes prompt-injection defense as causal inference.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 4. Method |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5.1. Experimental Setup |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/CausalTrace/graph/agentdojo_inference.py:108` | `ExtractedData` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/agentdojo_inference.py:118` | `AgentDojoEdgeInferenceEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/detection/metrics.py:23` | `EvaluationMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/detection/metrics.py:140` | `compute_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/detection/metrics.py:209` | `compute_roc_curve` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/detection/evaluator.py:21` | `BenchmarkResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/detection/evaluator.py:43` | `BenchmarkEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/detection/evaluator.py:370` | `evaluate_multiple_detectors` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalBench/core/trajectory_logger.py:16` | `EventType` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalBench/core/trajectory_logger.py:25` | `TrustLevel` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalBench/core/trajectory_logger.py:31` | `EdgeType` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/validators.py:13` | `validate_dag` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/validators.py:29` | `validate_edge_consistency` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/validators.py:76` | `validate_edge_types` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/edge_enhancer.py:18` | `enhance_graph_edges` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/edge_enhancer.py:68` | `_add_sequential_edges` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/edge_enhancer.py:91` | `_add_dataflow_edges` | Pinned implementation entry for the selected mechanism. |
| `official-code/CausalTrace/graph/provenance.py:39` | `ProvenanceComputer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b3285686564b522cbfbe9bcbbed2c6b6ac8e1227`. Paper page numbers refer to the fixed local proceedings PDF.
