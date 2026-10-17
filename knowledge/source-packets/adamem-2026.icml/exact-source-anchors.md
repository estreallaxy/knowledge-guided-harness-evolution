# Exact source anchors

## Selected mechanism

To address this rigidity, we propose the Adaptive Memory Agent (AdaMEM), a novel framework for agent test-time adaptation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experiments |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/eval/evaluate_vision_dagger.py:10` | `evaluate_vision_dagger` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/eval/evaluate_dqn.py:10` | `evaluate_dqn` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/eval/evaluate_dagger.py:11` | `evaluate_dagger` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/gen/agents/deterministic_planner_agent.py:4` | `DeterministicPlannerAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/gen/agents/semantic_map_planner_agent.py:9` | `SemanticMapPlannerAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/modules/memory.py:14` | `PrioritizedReplayMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/modules/memory.py:281` | `DaggerReplayMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/coco_eval.py:19` | `CocoEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/coco_eval.py:158` | `convert_to_xywh` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/coco_eval.py:163` | `merge` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/environment/__init__.py:1` | `get_environment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/transforms.py:7` | `_flip_coco_person_keypoints` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/transforms.py:17` | `Compose` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/transforms.py:27` | `RandomHorizontalFlip` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/mrcnn.py:12` | `get_model_instance_segmentation` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/mrcnn.py:39` | `load_pretrained_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/environment/alfred_hybrid.py:7` | `AlfredHybrid` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/gen/agents/agent_base.py:6` | `AgentBase` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `4ea93e239f8dbec2fa6013a28bc8555419037e12`. Paper page numbers refer to the fixed local proceedings PDF.
