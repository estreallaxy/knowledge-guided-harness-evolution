# Tests and reported results

## Official verification entry points

- `eval_consistency/run_eval.sh`
- `eval_consistency/eval_probability_en_to.py`
- `eval_consistency/eval_probability_to_en.py`
- `eval_consistency/show_wrong_entities.py`
- `eval_consistency/src_tgt_tokenize_en_to.py`
- `eval_consistency/src_tgt_tokenize_to_en.py`

## Published result anchors

- p. 3: Table 1: Translation results with different translation window sizes. “#Missing Sents” represents the
- p. 7: Table 2: Test results on the IWSLT2017 dataset. Since the translations produced by the Doc2Doc
- p. 8: Table 3: Test results on the Guofeng dataset.
- p. 9: Table 4: Ablation Study.
- p. 9: Table 6. D ELTA improves the performance of pronoun
- p. 17: Table 8: Demonstrations of proper noun translation inconsistency, undertranslation, and low transla-
- p. 18: Table 9: Statistics of the test sets used in our experiments. “|S|” represents the number of sentences
- p. 18: Table 10: More detailed results of the ablation study.
- p. 19: Table 11: Effect of the Short-Term and Long-Term window size.
- p. 19: Table 12: Evaluation results on the Lt ⇒ En low-resource test set.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2025 |
| Official open-source implementation | https://github.com/YutongWang1216/DocMTAgent at `6dde70acc9e60fd2533c2ca467eb327884d20dab` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
