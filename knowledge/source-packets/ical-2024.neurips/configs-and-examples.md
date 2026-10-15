# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `Ego4d/requirements.txt`
- `Ego4d/setup.py`
- `TEACh/requirements.txt`
- `VisualWebArena/requirements.txt`
- `VisualWebArena/setup.cfg`
- `VisualWebArena/setup.py`
- `Ego4d/Tracking-Anything-with-DEVA/pyproject.toml`
- `TEACh/teach/pyproject.toml`
- `TEACh/teach/requirements.txt`
- `TEACh/teach/setup.cfg`
- `TEACh/teach/setup.py`
- `Ego4d/SoM/ops/setup.py`
- `TEACh/SOLQ/models/ops/setup.py`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_failure.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_resize_failure_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_resize_failure_2.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_resize_template.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_success.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/func_eval_fail.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/func_eval_success.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/func_url_func_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_content_element_exact_match.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_content_exact_match.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_content_url_comb.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_required_values_failure_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_required_values_success_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/image_evaluator_yes.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/image_evaluator_yes_direct_img.json`

## Upstream command excerpts

```text
ICAL
├── README.md
├── Ego4D
│   ├── README.md
│   ├── domain_files
│   └── environment
├── VisualWebArena
│   ├── README.md
│   ├── domain_files
│   └── environment
└── TEACh
    ├── README.md
    ├── domain_files
    └── environment
```

```text
git clone https://github.com/Gabesarch/ICAL.git
    cd ICAL
```

```text
@article{sarch2024ical,
  title={ICAL: Continual Learning of Multimodal Agents by Transforming Trajectories into Actionable Insights},
  author={},
  journal={},
  year={2024}
}
```

```text
@inproceedings{sarch2024vlm,
  title={VLM Agents Generate Their Own Memories: Distilling Experience into Embodied Programs of Thought},
  author={Sarch, Gabriel Herbert and Jang, Lawrence and Tarr, Michael J and Cohen, William W and Marino, Kenneth and Fragkiadaki, Katerina},
  booktitle={The Thirty-eighth Annual Conference on Neural Information Processing Systems},
  year={2024}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
