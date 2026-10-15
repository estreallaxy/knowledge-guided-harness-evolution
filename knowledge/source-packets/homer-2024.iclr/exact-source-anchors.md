# Exact source anchors

## Selected mechanism

Split context, process chunks, repeatedly merge/prune KV representations into a fixed target budget, then decode from the compact prefix.

## Paper anchors

- p. 2: Evaluation length (Tokens) Context length Context length
- p. 5: Algorithm 1 Memory-efficient computation ordering
- p. 5: implementation by simply replacing it for the generation process.
- p. 7: Method limit 4K 8K 16K 32K 4K 8K 16K 32K
- p. 7: method (NTK), achieving 38.8% accuracy. This demonstrates that language models extended with
- p. 8: Method limit 4K 8K 16K 32K 64K 4K 8K 16K 32K 64K
- p. 8: method that maintains reasonable fluency even when conditioned on very long contexts. Moreover,
- p. 8: Method Accuracy Method Accuracy
- p. 9: Limitations and future work. Although our work focuses on training-free extension of context
- p. 10: Evaluation (IITP) grant funded by the Korea government (MSIT) (No.2019-0-00075, Artificial In-
- p. 18: Evaluation length (Tokens)
- p. 19: Evaluation length (Tokens)

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `src/homer/modeling_llama.py`
- `src/passkey.py`
- `src/perplexity.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. HOMER is explicitly training-free; calibration artifacts do not update model weights. The paper reports long-context/perplexity results and the repository exposes create_homer_prefix, patching, configs, and tests.

## Additional retained implementation anchors

## Symbol-level code anchors

- `src/homer/modeling_llama.py:64` — `MergeManager`
- `src/passkey.py:13` — `parse_answer`
- `src/perplexity.py:13` — `gather_logits`
