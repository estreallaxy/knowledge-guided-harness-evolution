# PSE-ICML2026

Code and experimental data for **"Persistent Semantic Entities in Tool-Augmented LLM Systems"** (ICML 2026).

> Tool-augmented LLM agents can harbor implicit state that persists across sessions, activates through events, and propagates across agent boundaries — largely invisible to standard debugging. We formalize this as **Persistent Semantic Entities (PSE)**: constructs defined by name binding, event triggering, and cross-boundary propagation. Experiments across 24 models from 11 families (1.5B–1T parameters; a 20-model/10-family susceptibility panel plus four defense-panel models) characterize susceptibility (20–100%), type-dependent temporal persistence, an oracle-free self-verification defense (20–79% reduction, median 36.5%), and 1.9× compounding across a four-stage multi-agent pipeline (40%→75%).

## Repository layout

```
rust_core/             Rust ground-truth simulator (deterministic registry, events, propagation graph)
python_harness/        Python orchestration — connects to 20 models across 10 model families
experiments/           Per-hypothesis experiment scripts (H1 drift, H2 observability, H3 ablation, E1–E5, defenses)
configs/               Experiment configurations (model lists, scenario definitions)
scripts/               Utility scripts (data processing, plotting helpers)
analysis/              Post-hoc analysis and figure generation
data/results/          Aggregated results used in the paper
data/results_large_scale/  Per-run outputs for H1 (behavioral_drift) and H2 (observability)
run_experiments.py     Top-level experiment runner
```

## Setup

### Python harness

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r python_harness/requirements.txt   # if present, else install per-import
cp .env.example .env                              # fill in your API keys
```

### Rust core

```bash
cd rust_core && cargo build --release
```

## Reproducing key results

**[`ARTIFACTS.md`](ARTIFACTS.md) is the full manifest**: paper section → script → config →
raw output JSON for every row of the paper's run ledger, plus the detection/judging
routing and an explicit list of results that are *not* reproducible from this release.

Verify the entire ledger in one command:

```bash
python3 scripts/verify_artifacts.py         # recomputes all 13 rows; ends with TOTAL 14293
python3 scripts/verify_artifacts.py --sha   # additionally checks SHA256SUMS
```

| Paper finding | Entry point |
|---|---|
| H1 — behavioral drift across configurations | `python_harness/src/pse_harness/experiments/behavioral_drift.py` |
| H2 — observability gap (standard vs. enhanced logs) | `python_harness/src/pse_harness/experiments/observability.py` |
| H3 — 2³ contamination ablation (N × T × P, all 8 configs; per-factor Cohen's d) | `experiments/real_ablation_experiment.py`, `data/results/ablation_real/` |
| Scaling sweep (20 models) | `experiments/icml_scaling_enhanced.py`, `icml_large_models_experiment.py`, `icml_claude_gemini_experiment.py` |
| E5 — temporal persistence by contamination type | `experiments/icml_temporal_persistence.py`, `run_temporal_local_models.py` |
| Defenses — self-verification (CIV), Shadow Registry Validation (SRV/M5), external validation | `experiments/llm_judge_contamination.py`, `data/results/defense_*` |
| E3 / E4 — multi-agent cascade, tool injection | `experiments/icml_multi_agent_experiment.py`, `icml_real_tool_injection.py` |

All experiments use temperature 0.0 for reproducibility; per-model sample sizes are `n=20–100` (open-weight models at n=100, frontier cloud models at n=20–50 due to API budget — see Appendix C.1 of the paper).

**Reproducibility scope.** The released artifacts reproduce the **14,293-run** corpus summarized in Appendix G of the paper (24 models, 11 families: the 20-model/10-family susceptibility panel plus four defense-panel models). Results flagged in the paper as withdrawn or descriptive-only — the earlier uncontaminated-setting factorial statistic, the H1 significance test, the B3/M5/M9/utility/half-life columns of the original operator study, and the secondary-judge agreement check — have no released run-level artifacts and are not re-executable from this repository. See [`ARTIFACTS.md`](ARTIFACTS.md#not-reproducible-from-this-release).

## Citation

```bibtex
@inproceedings{wang2026pse,
  title  = {Persistent Semantic Entities in Tool-Augmented {LLM} Systems},
  author = {Wang, Zhaohui},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  series = {ICML 2026},
  year   = {2026}
}
```

## Contact

Zhaohui Wang — `zwang000@usc.edu` — USC Viterbi School of Engineering

## License

See [LICENSE](LICENSE).
