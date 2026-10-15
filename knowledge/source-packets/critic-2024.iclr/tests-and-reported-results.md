# Tests and reported results

## Official verification entry points

- `src/program/evaluate.py`
- `src/qa/evaluate.py`
- `src/toxicity/evaluate.py`
- `src/toxicity/evaluate_ppl.py`

## Published result anchors

- p. 6: Table 1: Results of free-form question answering. See Table 8 in
- p. 7: Table 2: Mathematical program synthesis results. See Table
- p. 8: Table 3: Results of toxicity reduction. Avg. Max toxicity 20
- p. 22: Table 4: Comparison with related works on NL feedback and self-correction. Note that the methods
- p. 24: Table 5: Self-verification (i.e., Hallucination detection) results. We compare different methods using
- p. 25: Table 6: Types and corresponding percentages of success and failure modes of CRITIC and CoT on
- p. 26: Table 7: Error Analysis on Mathematical Program Synthesis tasks.
- p. 27: Table 8: LLaMA-2 Results of free-form question answering. ∗ indicates an oracle setting where we
- p. 28: Table 9: LLaMA-2 results of mathematical program synthesis.
- p. 28: Table 10: Additional mathematical program synthesis results. ∗ indicates an oracle setting where we

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/microsoft/ProphetNet at `5cf70eb41cdaa1d8faa3e1265d95ee5792d49a53` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
