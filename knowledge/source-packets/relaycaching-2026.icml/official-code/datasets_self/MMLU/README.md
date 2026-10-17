# MMLU Dataset

This directory contains the [MMLU](https://arxiv.org/abs/2009.03300) benchmark used by `experiments/main/run_mmlu.py`, the layer profiler, and observation scripts.

## What you need to run RelayCaching experiments

**After `git clone`, you can start MMLU experiments immediately.** No extra download is required.

| Directory | Used by this repo? | Purpose |
|-----------|-------------------|---------|
| `data/test/` | **Yes** (default) | Main evaluation split (`run_mmlu.py --mmlu_split test`) |
| `data/dev/` | Optional | Few-shot / alternate split |
| `data/val/` | Optional | Validation split |
| `data/auxiliary_train/` | **No** | Official auxiliary fine-tuning data (not used by our scripts) |

`run_mmlu.py` loads CSV files only from the split you choose (default: `test`):

```bash
python experiments/main/run_mmlu.py \
    --mmlu_data_dir datasets_self/MMLU/data \
    --mmlu_split test
```

Profiler / observation with MMLU use the same path via `--data ./datasets_self/MMLU/data --dataset-type mmlu`.

## About `race.csv` (not required)

The file `data/auxiliary_train/race.csv` (~147 MB) is **not** included on GitHub because it exceeds GitHub’s 100 MB per-file limit.

**You do not need this file** to reproduce paper experiments. Our evaluation pipeline never reads `auxiliary_train/`.

Download it only if you run your own MMLU auxiliary fine-tuning or analysis on that split.

## Optional: download the full official package

To fetch the complete Hendrycks release (including `race.csv`) from Berkeley:

```bash
# From the repository root, with your venv activated
python datasets_self/MMLU/download.py
```

This script:

1. Downloads `data.tar` from https://people.eecs.berkeley.edu/~hendrycks/data.tar into this directory (if missing).
2. Extracts to `data/` **only if `data/` does not already exist**.

If you already cloned this repo and have `data/`, the script will **not** re-extract. To replace everything with the official tarball:

```bash
cd datasets_self/MMLU
rm -rf data/
python download.py
```

To add only `race.csv` without removing existing CSVs:

```bash
cd datasets_self/MMLU
curl -L -o data.tar https://people.eecs.berkeley.edu/~hendrycks/data.tar
tar -xf data.tar data/auxiliary_train/race.csv
# Move race.csv into data/auxiliary_train/ if tar created a nested layout
rm -f data.tar
```

## Directory layout

```
datasets_self/MMLU/
├── README.md           # This file
├── download.py         # Official data.tar downloader
└── data/
    ├── README.txt      # Original MMLU dataset readme (citation)
    ├── dev/            # *.csv per subject
    ├── val/
    ├── test/           # Default evaluation split
    └── auxiliary_train/  # Optional; race.csv may be missing on GitHub
```

## Citation

If you use MMLU, please cite the original benchmark (see `data/README.txt`).
