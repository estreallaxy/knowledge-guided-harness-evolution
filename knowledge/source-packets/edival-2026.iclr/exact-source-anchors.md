# Exact source anchors

## Selected mechanism

Use object-centric state tracking to evaluate fine-grained correctness across multi-turn editing trajectories.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Design |
| Results and ablations | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/update_hps_scores.py:9` | `_resolve_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/update_hps_scores.py:23` | `_gather_tasks_for_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/update_hps_scores.py:102` | `_set_value_in_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:53` | `EvaluationModels` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:63` | `ImagePaths` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:70` | `TaskRateCollector` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/demo/test_ap_on_coco.py:24` | `load_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/demo/test_ap_on_coco.py:34` | `CocoDetection` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/demo/test_ap_on_coco.py:66` | `PostProcessCocoGrounding` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate.py:40` | `QwenImageEditGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate.py:80` | `process_single_image_on_gpu` | Pinned implementation entry for the selected mechanism. |
| `official-code/generate.py:173` | `worker_process` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/setup.py:30` | `install_torch` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/setup.py:56` | `write_version_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/setup.py:68` | `get_extensions` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/demo/create_coco_dataset.py:9` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/demo/gradio_app.py:42` | `load_model_hf` | Pinned implementation entry for the selected mechanism. |
| `official-code/GroundingDINO/demo/gradio_app.py:54` | `image_transform_grounding` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `96d34b00d7ea2dc3de90f2bb01f292f6dec6294a`. Paper page numbers refer to the fixed local proceedings PDF.
