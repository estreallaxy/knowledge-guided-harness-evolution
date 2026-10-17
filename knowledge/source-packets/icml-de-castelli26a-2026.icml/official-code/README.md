# Long-range Adaptive Memory Propagation (LAMP)

Official reference implementation of

> **Adaptive Memory Retention in Dynamic Graphs.**
> *Fabrizio De Castelli, Alessio Gravina, Moshe Eliasof, Carola-Bibiane Schönlieb, Davide Bacciu,*
> ICML 2026 Spotlight.

LAMP is a differential-equation-based GNN for discrete-time dynamic graphs
(D-TDGs). It treats incoming graph snapshots as **impulses** driving a neural
impulsive ODE: an antisymmetric (non-dissipative) parameterization propagates
information conservatively across space and time, while a learned, channel-wise
**adaptive dissipation** term $\Gamma$ regulates how much information is retained or
erased. This yields stable long-range spatio-temporal propagation with
task-driven filtering of noisy or redundant signals.

The model lives in [`src/models/lamp.py`](src/models/lamp.py) (registry key
`LAMP`), with the core dynamics in
[`src/layers/convolutions/lamp_conv.py`](src/layers/convolutions/lamp_conv.py).
Baselines are under `src/models/baseline/`.

The goal of this repository is **reproducibility**: clone it, let the datasets
download automatically, and re-run the paper's experiments.

## 1. Installation

The environment is managed with [`uv`](https://docs.astral.sh/uv/). Pinned
dependencies (including the CUDA `torch` / PyG wheels) are declared in
`pyproject.toml` and locked in `uv.lock`. The experiment environment targets
**CUDA Linux** machines (the paper's experiments ran on NVIDIA V100 GPUs):

```bash
git clone https://github.com/FabriDeCastelli/LAMP.git
cd LAMP
uv sync
```

All commands below are run through `uv run`.

## 2. Data

All datasets are **downloaded automatically on first use**: nothing has to be
generated or preprocessed manually, so results reproduce exactly.

### Data root

Downloaded datasets are stored under a single, user-configurable root
(`config.paths.DATA_ROOT`). It defaults to the repository's `data/` folder and
can be pointed elsewhere (e.g. shared storage) with the `LAMP_DATA_ROOT`
environment variable. Each dataset gets its own subfolder (e.g.
`<DATA_ROOT>/ColoredLeafCounting/`).

### Colored Leaf Counting (CLC)

The `ColoredLeafCounting` long-range benchmark introduced in the paper is
published, in compact form, on the Hugging Face Hub so that everyone uses the
*exact* same sequences and splits:

**https://huggingface.co/datasets/FabrizioDeCastelli/ColoredLeafCounting**

The first time a CLC setting is used, only that setting's folder and the shared
`spider.pt` topology are fetched into `<DATA_ROOT>/ColoredLeafCounting/` (via
`huggingface_hub.snapshot_download`, reused if already present). If the Hub
repository requires authentication, log in once with `hf auth login` (or set
`HF_TOKEN`). The published layout is:

```
<DATA_ROOT>/ColoredLeafCounting/
├── spider.pt                         shared rooted-tree topology (51 nodes)
├── T=200-BinaryColor/    data.pt  splits.json     (K=1)
├── T=200-ThreeColors/    data.pt  splits.json     (K=3)
├── T=400-BinaryColor/    …
├── T=400-ThreeColors/    …
├── T=600-BinaryColor/    …
└── T=600-ThreeColors/    …
```

Each `data.pt` stores the 600 samples of a setting in compact form (leaf
signals only); the loader reconstructs the dense per-snapshot node features
(`[T+H, 51, K]`) in memory on load. `splits.json` holds the exact
train/val/test indices used in the paper. The six settings map to the
`(T, num_colors)` grid in
`configurations/datasets/leaf_counting/SpiderW5H10.yaml`
(BinaryColor ⇒ K=1, ThreeColors ⇒ K=3).

You can exercise the loader directly:

```bash
uv run python -m src.datasets.tasks.leaf_counting --config T=200-ThreeColors
```

### Node prediction

ChickenPox Hungary, Twitter Tennis, and Wikipedia Math are fetched into
`data/pyg/` on first use via `torch_geometric_temporal`, and use the data
splits and evaluation protocols established in the original works.

### Link prediction

AS-733 and Bitcoin-α are fetched from the Hugging Face Hub repo
`FabrizioDeCastelli/temporal-link-level-prediction` into
`<DATA_ROOT>/temporal-link-level-prediction/<name>/` on first use. They are
published **already split**, with negative samples included, so the exact same
splits and negatives from the paper are reused.

### Traffic forecasting

METR-LA and PeMS-Bay are downloaded automatically by
[`tsl`](https://torch-spatiotemporal.readthedocs.io/) on first use of the
traffic runner (see below).

## 3. Reproducing the results

### Leaf counting, node prediction, link prediction

Reproducing a table entry is two stages: **model selection** (`main.py`, the
hyperparameter grid search) followed by **model assessment** (`run_reinit.py`,
which retrains the selected configuration `N_REINIT` times and reports the
mean ± standard deviation that the paper's tables show).

#### Stage 1 — model selection

`main.py` runs the hyperparameter grid defined under
`configurations/hyperparameters/<task>/<dataset>/` for the chosen model:

```bash
uv run python main.py --model LAMP --task leaf_counting   --dataset SpiderW5H10
uv run python main.py --model LAMP --task node_prediction --dataset ChickenPox
uv run python main.py --model LAMP --task node_prediction --dataset TwitterTennis
uv run python main.py --model LAMP --task node_prediction --dataset WikiMat
uv run python main.py --model LAMP --task link_prediction --dataset As-733
uv run python main.py --model LAMP --task link_prediction --dataset BitcoinAlpha
```

Baselines are run the same way by swapping `--model` (e.g. `--model DCRNN` for
leaf counting; the available grids are the YAML files under
`configurations/hyperparameters/<task>/<dataset>/`).

Useful flags:

- `--gpus 0 1 2 3` — GPU ids to parallelize the grid over
- `--workers N` — parallel workers per GPU
- `--debug` — single-process, CPU only (no Ray)
- `--load-checkpoint` — skip configurations that already completed
- `--wandb` — log to Weights & Biases (disabled by default)

Results and checkpoints are written under `experiments/tuning/`, one folder per
grid configuration, and the winning trial index is recorded in `best_run.txt`.

#### Stage 2 — model assessment

`run_reinit.py` reloads the configuration selected in stage 1 and retrains it
`N_REINIT` times (5 for leaf counting and link prediction, 10 for node
prediction — set per dataset in `configurations/datasets/`), changing only the
seed:

```bash
uv run python run_reinit.py --model LAMP --task node_prediction --dataset ChickenPox
```

It accepts the same `--gpus` / `--workers` / `--debug` / `--load-checkpoint`
flags as `main.py`, plus `--runs N` to override `N_REINIT` and `--trial N` to
assess a specific grid configuration instead of the selected one. Per-run
results go to `experiments/reinit/<task>/<dataset>/<settings>/<model>/run_<i>/`
and the mean/std aggregate to `scores.csv` in the model directory.

### Traffic forecasting (METR-LA, PeMS-Bay)

The traffic experiments are standalone and built on `tsl`:

```bash
cd traffic_forecasting
uv run python run_traffic_experiment.py --dataset la    # METR-LA
uv run python run_traffic_experiment.py --dataset bay   # PeMS-Bay
```

Hyperparameters live in `traffic_forecasting/la.yaml` / `bay.yaml` and can be
overridden on the command line with the usual Hydra syntax (e.g.
`model.hparams.hidden_size=256`).

## 4. Repository layout

```
config/                  project paths and run configuration
configurations/
  datasets/              dataset config YAMLs + frozen split files (3 tasks)
  hyperparameters/       model hyperparameter grids (paper-canonical)
src/
  datasets/              tasks (leaf counting, node / link prediction), scalers
  layers/                LAMP convolution, adaptive dissipation, discretization, readouts
  models/                the model (lamp.py) and baselines (baseline/)
  training/              trainer, training loops, checkpointing
  validation/            grid search + hyperparameter validation
traffic_forecasting/     standalone tsl-based traffic experiments (METR-LA, PeMS-Bay)
main.py                  entry point for model selection (the grid search)
run_reinit.py            entry point for model assessment (the N_REINIT runs)
```

## 5. Citation

If you use LAMP or the `ColoredLeafCounting` benchmark in your research,
please cite:

```bibtex
@inproceedings{
    castelli2026adaptive,
    title={Adaptive Memory Retention in Dynamic Graphs},
    author={Fabrizio De Castelli and Alessio Gravina and Moshe Eliasof and Carola-Bibiane Sch{\"o}nlieb and Davide Bacciu},
    booktitle={Forty-third International Conference on Machine Learning},
    year={2026},
    url={https://openreview.net/forum?id=x7NGYPNlgs}
}
```

## 6. License

This project is released under the [MIT License](LICENSE).
