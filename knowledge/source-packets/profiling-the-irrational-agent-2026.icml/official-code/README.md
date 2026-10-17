# Profiling the Irrational Agent: Cognitive Modeling of LLM Behaviors in Sequential Jailbreaks

Official code release for **Profiling the Irrational Agent: Cognitive Modeling of LLM Behaviors in Sequential Jailbreaks**, accepted to **ICML 2026**.

This repository provides a reproducible framework for profiling large language models as sequential decision-making agents under controlled safety-evaluation settings. The core idea is to move beyond outcome-only attack success rates and estimate interpretable behavioral descriptors from multi-turn trajectories.

[Paper PDF](paper/icml2026_paper.pdf) · [Citation](CITATION.cff) · [License](LICENSE)

<p align="center">
  <img src="assets/overview.png" alt="Overview of the C-IGT and GRW cognitive profiling framework" width="92%">
</p>

<p align="center">
  <em>Overview of the C-IGT evaluation protocol and GRW cognitive profiling pipeline.</em>
</p>

## Overview

The framework has three components:

- **C-IGT evaluation**: a Contextual Iowa Gambling Task protocol that elicits refusal/compliance trajectories across reward, framing, and counterfactual-feedback conditions.
- **GRW cognitive modeling**: a Generalized Rescorla-Wagner model that fits interpretable parameters such as asymmetric learning, choice inertia, risk curvature, reward amplification, and framing bias.
- **Analysis pipeline**: scripts for running experiments, computing behavioral metrics, fitting parameters, and generating cognitive profiles.

The default configuration is intentionally safe: it runs in mock mode on a small bundled demo dataset. Lightweight AdvBench and AgentHarm demo files are included for checking dataset-compatible workflows and must be selected explicitly.

## Installation

```bash
git clone https://github.com/YancyKahn/JailbreakCognitiveModeling.git
cd JailbreakCognitiveModeling

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The code is tested with Python 3.10+.

## Quick Smoke Test

Run the unit/integration tests:

```bash
python tests/test_new_architecture.py
```

Run a complete mock C-IGT experiment without API keys:

```bash
python scripts/experiment/run_experiments.py \
  --mock \
  --max_instructions 1 \
  --trials 2
```

Generated outputs are written under `logs/`, which is ignored by git. With the default configuration, batch results are saved as scenario-group CSV files under `logs/cigt-smoke/mock-model/`.

## Running Experiments

The main batch entry point is:

```bash
python scripts/experiment/run_experiments.py
```

By default, it reads `scripts/config/experiments.json`, uses `data/AdvBench/demo_harmful_behaviors_custom.csv`, and runs with mock responses.

To evaluate a user-provided dataset, prepare a CSV with a `goal` column and run:

```bash
python scripts/experiment/run_experiments.py \
  --dataset path/to/your_dataset.csv \
  --output_dir logs/cigt-real \
  --trials 50
```

For a single-instruction debug run:

```bash
python scripts/experiment/run_mab.py \
  --source ollama \
  --model mock-model \
  --instruction "explain account recovery safety" \
  --trials 2 \
  --mock
```

## API Configuration

The LLM client supports OpenAI-compatible chat completion endpoints. To run real API experiments, copy `.env.example` to `.env` locally and fill in the provider credentials. The `.env` file is intentionally ignored by git.

Supported provider prefixes include:

- `OPENAI`
- `SILICONFLOW`
- `DASHSCOPE`
- `DMXAPI`
- `NV`
- `OLLAMA`

You can verify the local configuration with:

```bash
python scripts/config/config_manager.py check
```

## Data

```text
data/
  AdvBench/
    demo_harmful_behaviors_custom.csv      AdvBench-format demo CSV
  AgentHarm/
    demo_harmful_behaviors_all_dedup.csv   AgentHarm-format demo CSV
```

The default smoke test uses the AdvBench-format demo CSV in mock mode. To run a dataset-compatible experiment with one of the included demo files, pass it explicitly:

```bash
python scripts/experiment/run_experiments.py \
  --dataset data/AdvBench/demo_harmful_behaviors_custom.csv \
  --output_dir logs/cigt-advbench \
  --trials 50
```

## Analysis and GRW Fitting

After an experiment finishes, fit cognitive parameters with:

```bash
python scripts/analysis/fit_params.py \
  --folder logs/cigt-smoke/mock-model/
```

Compute behavioral metrics or visualizations with:

```bash
python scripts/analysis/analyze.py \
  --folder logs/cigt-smoke/mock-model/ \
  --type metrics
```

The GRW report estimates:

| Parameter | Interpretation |
| --- | --- |
| `alpha_pos` | learning rate for positive prediction errors |
| `alpha_neg` | learning rate for negative prediction errors |
| `rho` | risk/utility curvature |
| `theta` | static decision or framing bias |
| `lambda` | choice inertia |
| `phi` | memory decay |
| `beta` | choice sensitivity |
| `R_perc` | perceptual reward amplification |
| `lambda_LA` | loss-aversion coefficient |

## C-IGT Scenario Groups

| Group | Paper-facing condition |
| --- | --- |
| `Baseline` | neutral standard control |
| `Optimism` | high reward probability |
| `Stimulus` | exaggerated or salient language feedback |
| `Magnitude` | high scalar reward salience |
| `Punishment` | explicit negative feedback |
| `Threat` | survival/threat framing |
| `Authority` | authority/root-access framing |
| `Regret` | counterfactual feedback |

## Repository Structure

```text
src/
  mab/          C-IGT scenarios, environment, prompt runner, LLM client
  fitting/      GRW parameter fitting and baseline comparison models
  analysis/     metrics, drift plots, radar/profile plots
scripts/
  experiment/   batch, single-run, and pipeline entry points
  analysis/     parameter fitting and analysis entry points
  config/       public configs and configuration checker
data/           demo datasets and experiment data interfaces
paper/          accepted paper PDF
tests/          integration tests
```

## Safety and Intended Use

This repository is intended for controlled LLM safety evaluation, reproducibility, and behavioral analysis. It should not be used to deploy jailbreak systems, automate harmful behavior, or construct attack services. The default configuration uses benign prompts and mock outputs so that new users can verify the pipeline without invoking real models or unsafe content.

## Citation

```bibtex
@inproceedings{yang2026profiling,
  title = {Profiling the Irrational Agent: Cognitive Modeling of LLM Behaviors in Sequential Jailbreaks},
  author = {Yang, Xikang and Zhou, Biyu and Tang, Xuehai and Han, Jizhong and Hu, Songlin},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  year = {2026}
}
```

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
