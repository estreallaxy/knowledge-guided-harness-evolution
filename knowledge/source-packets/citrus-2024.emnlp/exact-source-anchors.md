# Exact source anchors

## Selected mechanism

Process long input in chunks and evict recurrent/KV states according to their instruction-aware relevance under a fixed state budget.

## Paper anchors

- p. 2: method, Chunked Instruction-aware State Evic- search area in natural language processing (Tiezzi
- p. 2: approach can be seen as analogous to ideas from ther training of the model to handle long sequence
- p. 6: results on each dataset is provided in Appendix C.
- p. 7: results are bolded. R-1, R-2, and R-L represent ROUGE-
- p. 7: 6 Results shows the superiority of CItruS for long document
- p. 7: method achieves performance comparable to all the for Llama 2 13B Chat in the passkey retrieval tasks where all
- p. 8: results are bolded. “Param.” stands for hyperparameters.
- p. 9: Limitations
- p. 16: Results are separately presented by grouping text with different source lengths.
- p. 16: Results show: 1) There is a large gap between the
- p. 16: results are shown in Table 16, Table 17, and Ta-
- p. 17: results.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `run_on_longbench.sh`
- `src/baselines/attention_sink.py`
- `src/longbench/dataset2prompt.json`
- `src/longbench/dataset2prompt_new.json`
- `src/citrus_methods.py`
- `src/usage_longbench.py`
- `src/usage_sample.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The paper explicitly reports a training-free method and same-budget comparisons. The official code/data release contains chunk processing, eviction policies, configs, and experiments.

## Symbol-level code anchors

- `src/baselines/attention_sink.py:51` — `scorer_e`
- `src/citrus_methods.py:8` — `decoding`
- `src/usage_longbench.py:48` — `scorer_e`
- `src/usage_sample.py:4` — `main`
