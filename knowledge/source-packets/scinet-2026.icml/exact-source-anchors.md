# Exact source anchors

## Selected mechanism

To address this limitation, we introduce SciNet , the first Sci entific Net work relation-aware dataset for information retrieval agents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | framework |
| Experimental setup | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Experimental Setup |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/Evaluation/task1-novelty-rank.py:21` | `build_reference_distribution` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-rank.py:52` | `transform_score_by_percentile` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-rank.py:63` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-disruption-rank.py:21` | `build_reference_distribution` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-disruption-rank.py:61` | `transform_score_by_percentile` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-disruption-rank.py:77` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-disruptive-sos.py:21` | `DisruptionCalculator` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-disruptive-sos.py:91` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task3-path-connectivity.py:24` | `get_references` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task3-path-connectivity.py:38` | `_is_sequence_connected` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task3-path-connectivity.py:60` | `check_path_connectivity` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-sos.py:23` | `ReferenceFetcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-sos.py:77` | `NoveltyQuerier` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-sos.py:132` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-llm.py:25` | `AbstractFetcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-llm.py:75` | `LLMScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-novelty-llm.py:123` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Evaluation/task1-disruptive-llm.py:24` | `AbstractFetcher` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ed5c76fb250a4face6224ea834a62e63b47ddabd`. Paper page numbers refer to the fixed local proceedings PDF.
