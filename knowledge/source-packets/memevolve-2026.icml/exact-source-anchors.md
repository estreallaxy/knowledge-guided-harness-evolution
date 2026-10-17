# Exact source anchors

## Selected mechanism

To address this gap, we propose MemEvolve, a meta-evolutionary framework that jointly evolves agents’ experiential knowledge and their memory architecture, allowing agent systems not only to accumulate experience but also to progressively refine how they learn from it.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | architecture |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5.2. Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/docker.py:11` | `DockerEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/docker.py:36` | `DockerEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/extra/swerex_docker.py:10` | `SwerexDockerEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/extra/swerex_docker.py:20` | `SwerexDockerEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_docker.py:10` | `is_docker_available` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_docker.py:19` | `is_podman_available` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_docker.py:44` | `test_docker_environment_config_defaults` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/extra/test_swerex_docker.py:7` | `test_swerex_docker_basic_execution` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/extra/test_swerex_docker.py:21` | `test_swerex_docker_command_failure` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/__init__.py:17` | `get_environment_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/__init__.py:28` | `get_environment` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/local.py:9` | `LocalEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/local.py:15` | `LocalEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/singularity.py:15` | `SingularityEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/singularity.py:30` | `SingularityEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/extra/bubblewrap.py:26` | `BubblewrapEnvironmentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/extra/bubblewrap.py:68` | `BubblewrapEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_init.py:7` | `TestGetEnvironmentClass` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `6035d5659d7a092dbfa6a87b1a32a3cee652ba54`. Paper page numbers refer to the fixed local proceedings PDF.
