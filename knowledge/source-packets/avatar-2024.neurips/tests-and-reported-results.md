# Tests and reported results

## Official verification entry points

- `scripts/eval.py`
- `scripts/eval_avatar_by_indices.py`
- `scripts/eval_avatar_flickr30k_entities.sh`
- `scripts/eval_avatar_stark.sh`
- `scripts/eval_react_flickr30k_entities.sh`
- `scripts/eval_react_stark.sh`

## Published result anchors

- p. 5: Table 1: Key differences between AVATA R and prevailing agent methods. AVATA R demonstrates
- p. 8: Table 2: Retrieval performance (%) on STA RK benchmark. Last row shows the relative improvements
- p. 10: Table 3: Performance (%) on three QA benchmarks. Last row shows the relative improvements over
- p. 17: Table 4: Retrieval performance (%) on STA RK benchmark. Last row shows the relative improvements
- p. 17: Table 5: Retrieval performance (%) on the leave-out sets of human-generated queries in STA RK.
- p. 17: Table 6: Performance metrics for different models on the subset of the STA RK-MAG dataset.
- p. 18: Table 7: Hit@1 results for different combinations of ℓ and h values on the STA RK-A MAZON dataset.
- p. 22: Table 8: Function library on STA RK
- p. 23: Table 9: Function library on Flickr30K Entities

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/zou-group/avatar at `244a0546fc4e882d3ab0f2e2670d66f89acac92f` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
