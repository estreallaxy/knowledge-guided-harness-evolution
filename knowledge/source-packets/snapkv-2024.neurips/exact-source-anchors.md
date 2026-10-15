# Exact source anchors

## Selected mechanism

Use an observation window to estimate head-specific salient prompt positions, pool nearby positions, and retain only the selected KV cache.

## Paper anchors

- p. 2: method, SnapKV, which can smartly identify the attention allocation pattern and compress the KV
- p. 7: implementation encounters OOM error with 33k input tokens (white dashed line).
- p. 8: 5.2 Ablation Study of Effectiveness of Pooling
- p. 9: results (Fig. 8). Note that throughout our experiments, the choice between max pooling and average
- p. 10: results also indicate the effectiveness of SnapKV in compressing the prompt KV cache. For these 4
- p. 10: experiment with a kernel size of 1, representing a configuration without pooling. This analysis
- p. 17: evaluation. While "[Yes] " is generally preferable to "[No] ", it is perfectly acceptable to answer
- p. 18: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 20: experiment details in Sec. 5
- p. 20: results?
- p. 23: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `experiments/LongBench/README.md`
- `experiments/LongBench/config/dataset2prompt.json`
- `experiments/LongBench/config/ablation_c1024_w32_k7_maxpool.json`
- `experiments/LongBench/config/ablation_c2048_w32_k7_maxpool.json`
- `experiments/LongBench/config/ablation_c4096_w32_k7_maxpool.json`
- `experiments/LongBench/config/dataset2maxlen.json`
- `experiments/LongBench/config/model2maxlen.json`
- `experiments/LongBench/config/model2path.json`
- `experiments/LongBench/eval.py`
- `experiments/LongBench/scripts/run_longbench.sh`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. It is a tuning-free inference patch. Main-track experiments cover long-context QA/retrieval/code and the repository provides HuggingFace integration, kernels, configs, and evaluation scripts.

## Symbol-level code anchors

- `experiments/LongBench/eval.py:42` — `parse_args`
