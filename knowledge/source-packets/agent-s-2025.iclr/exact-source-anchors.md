# Exact source anchors

## Selected mechanism

Combine experience-augmented hierarchical planning, continual non-parametric memory, and a GUI Agent–Computer Interface with state-aware replanning.

## Paper anchors

- p. 9: Method OS (6) Office (17) Daily (16) Profess. (10) Workflow (16) Overall (65)
- p. 10: Method Office Web Browser Windows System Coding Media & Video Windows Utils Overall
- p. 16: Method
- p. 18: Method

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `gui_agents/s1/README.md`
- `integrations/openclaw/README.md`
- `tests/test_providers.py`
- `gui_agents/s1/core/ProceduralMemory.py`
- `gui_agents/s2/memory/procedural_memory.py`
- `gui_agents/s2_5/memory/procedural_memory.py`
- `gui_agents/s3/memory/procedural_memory.py`
- `gui_agents/utils.py`
- `gui_agents/s1/cli_app.py`
- `gui_agents/s2/cli_app.py`
- `gui_agents/s2_5/cli_app.py`
- `gui_agents/s3/cli_app.py`
- `integrations/openclaw/agent_s_wrapper.py`
- `osworld_setup/s1/lib_run_single.py`
- `osworld_setup/s1/run.py`
- `osworld_setup/s2/lib_run_single.py`
- `osworld_setup/s2/run.py`
- `osworld_setup/s2_5/lib_run_single.py`
- `osworld_setup/s2_5/lib_run_single_local.py`
- `osworld_setup/s2_5/run.py`
- `osworld_setup/s2_5/run_local.py`
- `osworld_setup/s3/lib_run_single.py`
- `osworld_setup/s3/run.py`
- `osworld_setup/s3/run.sh`
- `osworld_setup/s3/run_local.py`
- `gui_agents/s1/aci/ACI.py`
- `gui_agents/s1/aci/LinuxOSACI.py`
- `gui_agents/s1/aci/MacOSACI.py`
- `gui_agents/s1/aci/WindowsOSACI.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The deployable harness uses prompted MLLMs and persistent experience rather than parameter updates. The paper reports OS/Android results and the repository exposes planners, memory, grounding, action execution, and runners.

## Symbol-level code anchors

- `tests/test_providers.py:8` — `TestProviders`
- `gui_agents/s1/core/ProceduralMemory.py:5` — `PROCEDURAL_MEMORY`
- `gui_agents/s2/memory/procedural_memory.py:5` — `PROCEDURAL_MEMORY`
- `gui_agents/s2_5/memory/procedural_memory.py:5` — `PROCEDURAL_MEMORY`
- `gui_agents/s3/memory/procedural_memory.py:5` — `PROCEDURAL_MEMORY`
- `gui_agents/utils.py:10` — `download_kb_data`
- `gui_agents/s1/cli_app.py:21` — `get_char`
- `gui_agents/s2/cli_app.py:23` — `get_char`
- `gui_agents/s2_5/cli_app.py:23` — `get_char`
- `gui_agents/s3/cli_app.py:24` — `get_char`
- `integrations/openclaw/agent_s_wrapper.py:17` — `run_agent_s`
- `osworld_setup/s1/lib_run_single.py:11` — `run_single_example`
