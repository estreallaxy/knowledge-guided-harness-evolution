# CUARewardBench Dataset Card

## Dataset Summary

CUARewardBench is a benchmark for evaluating reward models on Computer-Using Agent (CUA) trajectories. It is designed to test whether a reward model can judge trajectory-level task success and identify step-level action quality from desktop-agent rollouts.

Current release candidate snapshot:

| Item | Value |
| --- | --- |
| Annotation file | `data/annotations/cuarewardbench-v0.4.json` |
| Annotated trajectories | 272 |
| Screenshots | 3016 |
| Payload size | ~1.28 GB after normalization |
| Trajectory root | `data/trajectories/osworld_verified/` |
| Manifest | `data/manifest.jsonl` |

## Tasks and Trajectories

The benchmark uses OSWorld-style desktop tasks. Each data item is identified by:

```text
(model_setting, task_type, task_id)
```

The normalized trajectory layout is:

```text
data/trajectories/osworld_verified/
└── {model_setting}/
    └── {task_type}/
        └── {task_id}/
            ├── step_*.png
            ├── traj.jsonl
            ├── traj_tran.jsonl      # derived/auxiliary when present
            ├── result.txt
            └── runtime.log
```

`traj.jsonl` is the primary action trace. `traj_tran.jsonl`, when present, is auxiliary and is not required by the benchmark evaluator if `traj.jsonl` is available.

## Labels

The annotation file contains:

- trajectory-level success labels via `result`;
- task metadata: `model_setting`, `task_type`, `task_id`, `instruction`, `step_num`;
- step-level annotation lists such as `key_good_in_success`, `key_bad_in_success`, and `key_good_after_bad_in_success`.

See `docs/annotation_protocol.md` and `docs/data_format.md` for schema details.

## Intended Uses

Recommended uses:

- evaluate outcome reward models (ORM) on CUA trajectory success;
- evaluate process reward models (PRM) on annotated key steps;
- compare reward prompt modes such as `zerogui` and `sewsm_thinking`;
- reproduce the CUARewardBench results reported in the associated paper;
- run UPE / majority voting experiments over multiple reward model outputs.

Out-of-scope uses:

- training or deploying autonomous agents directly from the annotations without additional validation;
- using reward predictions as the only safety gate for high-risk real-world actions;
- treating benchmark labels as exhaustive explanations of every trajectory step.

## Data Access and Verification

Full trajectory images are not committed to GitHub. Use:

```bash
bash scripts/download_data.sh
python3 scripts/verify_data.py --trajectory_root ../data_build_workspace/prepared/osworld_verified
```

The download pipeline normalizes raw archives and verifies the resulting files against `data/manifest.jsonl` using file size and SHA-256 checksums.

## License and Redistribution

- Repository-authored code, annotations, metadata, and documentation are licensed under Apache-2.0.
- Trajectory screenshots/images and raw archives are not redistributed by this repository; users must comply with upstream source terms.
- `traj_tran.jsonl` is kept as-is where present in the current normalized manifest.

## Known Limitations

- Reward-model reruns can be stochastic even with the same prompt and nominal model name.
- Some images are large; model API write timeouts can happen on slow endpoints.
- Labels focus on benchmark-relevant success and key actions, not a full natural-language explanation of every step.

## Citation

If you use this dataset, cite:

```bibtex
@misc{lin2025cuarewardbench,
  title         = {CUARewardBench: A Benchmark for Evaluating Reward Models on Computer-using Agent},
  author        = {Haojia Lin and Xiaoyu Tan and Yulei Qin and Zihan Xu and Yuchen Shi and Zongyi Li and Gang Li and Shaofei Cai and Siqi Cai and Chaoyou Fu and Ke Li and Xing Sun},
  year          = {2025},
  eprint        = {2510.18596},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SE},
  doi           = {10.48550/arXiv.2510.18596},
  url           = {https://arxiv.org/abs/2510.18596}
}
```
