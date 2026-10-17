# LLMPrint Official Code

This is the official code implementation for the ACL 2026 Main paper, "Fingerprinting LLMs via Prompt Injection".

## Files

- `generate_pairs.py`: generate category-based single-token word pairs.
- `generate_adv_prompt.py`: optimize fingerprint suffixes for each token pair.
- `create_adv_prompt.py`: GCG helper used by `generate_adv_prompt.py`.
- `produce_prob_finetune_batch.py`: evaluate suspect models in gray-box and/or black-box mode and save probability sequences.
- `model_test_prob.py`: compute detection rates from saved probability sequences.
- `detect_func.py`: shared detection helpers.
- `model_lists/`: release model lists and validation negatives.

## Dependencies

The release environment is named `llmprint`.

For release, the exported environment file is:

```bash
environment.yml
```

You can recreate it with:

```bash
conda env create -f environment.yml
conda activate llmprint
```

If you need to recreate the environment manually, install at least:

```bash
pip install torch transformers huggingface_hub numpy tqdm
```

`generate_adv_prompt.py` also requires `nanogcg`.

## Standard Workflow

1. Generate token pairs.

```bash
python generate_pairs.py \
  --base-model meta-llama/Meta-Llama-3-8B \
  --num-pairs 300 \
  --output word_pairs_Meta-Llama-3-8B.pt
```

2. Optimize fingerprint suffixes.

```bash
python generate_adv_prompt.py \
  --base-model meta-llama/Meta-Llama-3-8B \
  --pairs-path word_pairs_Meta-Llama-3-8B.pt \
  --output-dir Meta-Llama-3-8B_adv_suffix_ids_target
```

3. Produce probability sequences for post-trained suspects and the base model.

```bash
python produce_prob_finetune_batch.py \
  --base-model meta-llama/Meta-Llama-3-8B \
  --model-list-path model_lists/llama3/post_train.pt \
  --include-base-model \
  --adv-dir ./Meta-Llama-3-8B_adv_suffix_ids_target \
  --pairs-path ./word_pairs_Meta-Llama-3-8B.pt \
  --modes graybox blackbox \
  --split-label relevant
```

4. Produce calibration results for validation negatives.

```bash
python produce_prob_finetune_batch.py \
  --base-model meta-llama/Meta-Llama-3-8B \
  --model-list-path model_lists/validation_negatives.pt \
  --adv-dir ./Meta-Llama-3-8B_adv_suffix_ids_target \
  --pairs-path ./word_pairs_Meta-Llama-3-8B.pt \
  --modes graybox blackbox \
  --split-label holdout
```

5. Optionally produce a second comparison split by passing another model list and a different `--split-label`, for example `irrelevant`.

6. Run detection.

`model_test_prob.py` uses `result_metadata.json` and `pair_manifest.json` when they are available, and it excludes the base model file from reported detection rates by default. Pass `--include-base-model-in-rate` if you want to count the base model itself in the comparison folder statistics.

Gray-box:

```bash
python model_test_prob.py \
  --base-model meta-llama/Meta-Llama-3-8B \
  --detect-type graybox \
  --adv-dir ./Meta-Llama-3-8B_adv_suffix_ids_target \
  --compare-split finetune=relevant
```

Black-box:

```bash
python model_test_prob.py \
  --base-model meta-llama/Meta-Llama-3-8B \
  --detect-type blackbox \
  --adv-dir ./Meta-Llama-3-8B_adv_suffix_ids_target \
  --compare-split finetune=relevant
```

If your comparison folders use different labels or locations, pass them explicitly with `--compare-folder`, `--base-sequence-path`, and `--irrelevant-folder`.

## Result Folder Naming

`produce_prob_finetune_batch.py` writes result folders under `--result-root` using the pattern:

```text
prob_<adv_type>_<num_pairs>_<base_model>_<mode>_<loss_type>_<split_label>
```

Use `--split-label` to separate `relevant`, `irrelevant`, and `holdout` runs.

Each result folder also contains:

- `result_metadata.json`: metadata used by `model_test_prob.py` to resolve folders without relying only on directory naming.
- `pair_manifest.json`: the exact ordered pair list used to generate the saved probability sequences.

At the root of `--result-root`, the batch script also writes split-specific files:

- `produce_prob_run_config_<split_label>.json`
- `produce_prob_run_summary_<split_label>.json`
