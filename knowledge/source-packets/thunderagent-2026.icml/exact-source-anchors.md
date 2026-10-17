# Exact source anchors

## Selected mechanism

To address the challenges, we propose ThunderAgent , a fast, simple, and program-aware agentic inference system.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 2.1. System |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5.1. Experimental setup |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 5.4. Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/docker.py:12` | `DockerEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/docker.py:47` | `DockerEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/extra/swerex_docker.py:10` | `SwerexDockerEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/extra/swerex_docker.py:20` | `SwerexDockerEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/image_cache.py:26` | `ImageCacheManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/image_cache.py:177` | `_parse_docker_size` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/rl_training/SkyRL/skyrl-agent/skyrl_agent/tools/cache.py:11` | `WebPageCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/rl_training/SkyRL/skyrl-agent/skyrl_agent/tools/local_search.py:19` | `LocalSearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/rl_training/SkyRL/skyrl-agent/skyrl_agent/tools/search_engine.py:10` | `SearchEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/rl_training/SkyRL/skyrl-agent/skyrl_agent/tools/youcom_search_engine.py:18` | `YouComSearchEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/rl_training/SkyRL/skyrl-agent/skyrl_agent/tools/search.py:28` | `FaissSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/codeact_agent/tools/prompt.py:12` | `refine_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/__init__.py:17` | `get_environment_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/__init__.py:28` | `get_environment` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/local.py:9` | `LocalEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/local.py:15` | `LocalEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/singularity.py:15` | `SingularityEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/inference/mini-swe-agent/src/minisweagent/environments/singularity.py:30` | `SingularityEnvironment` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7ddc8610270e56d3b109eed8796b3a4360fc67c9`. Paper page numbers refer to the fixed local proceedings PDF.
