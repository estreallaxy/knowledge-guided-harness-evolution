# Exact source anchors

## Selected mechanism

We introduce a tournament graph framework that provides a principled foundation for $k$-wise ranking.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.19; `paper/paper-icml2026.txt` marker `===== PDF p.19 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | design |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Main Results |
| Limitations or failure conditions | PDF p.39; `paper/paper-icml2026.txt` marker `===== PDF p.39 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/test_evaluate.py:12` | `test_evaluate` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/toy_setup.py:12` | `ToyCompareOracle` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/toy_setup.py:25` | `make_shuffled_items` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/toy_setup.py:34` | `ToyNonTransitiveFullPairwiseOracle` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/evaluator.py:10` | `trec_eval` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/evaluator.py:51` | `remove_duplicate` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/evaluator.py:61` | `clean_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/engine/algorithms/tournament_graph/test_transitive.py:16` | `_verify_top_m` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/engine/algorithms/tournament_graph/test_transitive.py:26` | `test_25_horses_puzzle_7_oracle_calls` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/engine/algorithms/tournament_graph/test_transitive.py:41` | `test_n_equals_k_single_match` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/engine/algorithms/tournament_graph/test_non_transitive.py:20` | `_get_bucket` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/engine/algorithms/tournament_graph/test_non_transitive.py:24` | `_verify_results_from_buckets` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/engine/algorithms/tournament_graph/test_non_transitive.py:39` | `test_single_3_cycle_graph_structure` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/compare_oracle.py:6` | `Item` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/compare_oracle.py:21` | `OracleResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/compare_oracle.py:26` | `make_edges_from_linear_order` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/tournament_graph.py:11` | `RoundOutput` | Pinned implementation entry for the selected mechanism. |
| `official-code/blitzrank/engine/algorithms/tournament_graph/tournament_graph.py:37` | `TournamentGraph` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `076018cf6153608203029e29562c36f50273b348`. Paper page numbers refer to the fixed local proceedings PDF.
