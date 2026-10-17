# Artifact manifest — *Persistent Semantic Entities in Tool-Augmented LLM Systems* (ICML 2026)

This file is the paper-section → script → config → raw-output mapping referenced in
Appendix E of the paper. Every run count in the paper's ledger (Appendix G, Table 23)
is recomputable from the files listed here.

**Verify the whole ledger in one command:**

```bash
python3 scripts/verify_artifacts.py          # recomputes all 13 rows + total
python3 scripts/verify_artifacts.py --sha    # also checks the SHA-256 manifest
```

Expected output ends with `[ok ] TOTAL 14293 (paper: 14293)`.

## Run ledger → artifacts

| # | Paper location | Runs | Experiment script | Raw output |
|---|---|---:|---|---|
| 1 | §4.1 H1 behavioral drift | 6,000 | `python_harness/src/pse_harness/experiments/behavioral_drift.py` | `data/results_large_scale/behavioral_drift/107216ab-…/{summary,runs,tasks}.json` |
| 2 | §4.2 H2 observability gap | 4,000 | `python_harness/src/pse_harness/experiments/observability.py` | `data/results_large_scale/observability/107216ab-…/{summary,runs}.json` |
| 3 | §4.3 H3 contamination ablation (Table 3) | 320 | `experiments/real_ablation_experiment.py` | `data/results/ablation_real/ablation_20260301_005346.json` (Gemini-2.0-Flash-Lite), `…_005729.json` (Llama-3.1-8B) |
| 4 | App C.1 scaling sweep (Table 12, Figs 3–4) | 1,100 | `experiments/icml_scaling_enhanced.py`, `icml_large_models_experiment.py`, `icml_claude_gemini_experiment.py` | `icml_scaling_enhanced/experiment_20260122_015037.json` (700), `icml_large_models_final/large_models_20260123_012134.json` (100), `icml_large_models_extended/extended_20260123_135623.json` (100), `icml_claude_gemini/experiment_20260128_200156.json` (200) |
| 5 | App C.2.1–C.2.4 seven-defense panel (Tables 14–15, Fig 5) | 880 | `experiments/llm_judge_contamination.py`, `icml_claude_self_reflection.py` | `icml_defense_final/experiment_20260123_032404.json` (700, GPT-4o-mini), `icml_claude_self_reflection/experiment_20260128_210708.json` (180, 3 models) |
| 6 | App C.2.5 cross-model CIV/SRV panel (main Tables 5, 7; Table 16) | 480 | `experiments/run_all_neurips_defense.sh`, `run_cloud_experiments.sh` | `defense_neurips/defense_20260327_195034.json`, `…_163802.json`; `defense_real/defense_20260301_004626.json`; `defense_cloud/defense_20260328_0105 22/010750/011608/011054/011801.json` |
| 7 | App C.3 temporal persistence, 20-turn (Table 17, Fig 6) | 480 | `experiments/icml_temporal_persistence.py` | `icml_temporal/experiment_20260122_012343.json` |
| 8 | §4.6 temporal persistence, 10-turn (Table 6, Fig 1 bottom) | 200 | `experiments/run_temporal_local_models.py` | `temporal_n10_vllm/temporal_llama31_8b_vllm_n10_20260501_134921.json` |
| 9 | App C.4 multi-agent cascade E3 (Table 18) | 300 | `experiments/icml_multi_agent_experiment.py` | `icml_multi_agent/experiment_20260122_034930.json` |
| 10 | App C.5 tool injection E4 (Table 19) | 300 | `experiments/icml_real_tool_injection.py` | `icml_tool_injection/experiment_20260122_235737.json` |
| 11 | §4.4 remediation operators (Table 4) | 63 | `experiments/pse_remediation_real.py` | `remediation_real/experiment_20260115_113813.json` |
| 12 | §2 RAG pollution (65% baseline) | 80 | `experiments/icml_rag_pollution.py` | `icml_rag_pollution/experiment_20260122_011539.json` |
| 13 | App C.1 cross-model H1 replication (Table 13) | 90 | `experiments/icml_cross_model_experiment.py` | `icml_cross_model/experiment_20260121_232937.json` |
| | **Total** | **14,293** | | |

Shared configuration: `configs/experiment_config.json`. All experiments use
temperature 0.0. Per-model seed ledger is in Appendix C.1 of the paper and in the
`n` column of Table 12.

## Detection / judging

| Experiment | Canonical labels | Diagnostic channels |
|---|---|---|
| H1, H2 | task-level drift / visibility metrics | — |
| Scaling sweep | keyword + cosine (`cos > 0.7`) | threshold sweep [0.5, 0.9] |
| Ablation, defense, temporal, multi-agent, tool injection | LLM-as-judge (Gemini-2.0-Flash-Lite, context-isolated) | keyword channel |

Keyword-vs-judge comparison (n=180, Cohen's κ=0.22 overall; 83% keyword FP rate on
factual-correction responses): `temporal_judge_comparison/comparison_20260328_161941.json`.

## Not reproducible from this release

These are flagged as descriptive historical observations in the paper; their
run-level artifacts were not retained and are **not** in this repository:

- the earlier uncontaminated-setting factorial and its interaction statistic (§4.3);
- the H1 significance test (Table 2 caption);
- the B3/M5/M9 rows and the utility / half-life columns of the original operator study (Table 4 caption);
- the secondary-judge agreement check (Llama-3.1-8B vs. Gemini, κ=0.88, App C.6).

## Supporting runs not in the ledger

Exploratory, superseded, or side experiments that no paper number depends on are
retained for transparency but excluded from the ledger — e.g. earlier scaling
pilots (`icml_scaling/`), larger tool-injection sweeps (`icml_tool_injection/*_005816`,
`*_031308`), cross-provider probes (`temporal_cloud/`, `provider_diagnosis/`,
`temporal_local_control/`, `temporal_neurips/`), `red_blue/`, `information_theory/`,
`iterative_contamination/`, `controlled_persistence/`, and additional ablation
models (`ablation_real/ablation_20260427_*`). One aborted run was truncated
mid-write and is kept with a `.partial.json` suffix
(`icml_cross_model/experiment_20260121_232758.partial.json`); it is superseded by
`experiment_20260121_232937.json` and is not parsed by any analysis.
