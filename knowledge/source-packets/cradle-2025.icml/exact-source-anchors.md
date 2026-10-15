# Exact source anchors

## Selected mechanism

Six-module GUI loop: information gathering, self-reflection, task inference, skill curation, action planning, and memory, with keyboard/mouse execution. It works with frozen MLLMs.

## Paper anchors

- p. 1: framework, as a preliminary attempt towards With a unified interface to interact with any soft-
- p. 3: results in effectively interacting with content on webpages,
- p. 4: framework should have the ability to understand and in- mouse operations, including key_press, key_hold,
- p. 9: Method Cultivation
- p. 16: ablation studies are not included. Since all the tasks were run 5 times except for OSWorld once, the total cost of getting all
- p. 17: Method
- p. 17: method struggles with getting out of the house and returning home due to the lack of visual input. Claude 3 Opus also
- p. 18: Evaluation Methods. Unlike conventional research benchmarks, which usually provide grounding signals for evaluation, it
- p. 39: method or effect of an action in the game, e.g., giving the price can only use the keyboard to input an integer in an abstract
- p. 41: evaluation metrics:
- p. 48: Algorithm 1 Skill Generation
- p. 55: approach (Yang et al., 2023a), by only utilizing SAM (Kirillov et al., 2023) to generate potential UI items bounding boxes

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `conf/env_config_rdr2_main_storyline.json`
- `res/capcut/prompts/inputs/action_planning.json`
- `res/chrome/prompts/inputs/action_planning.json`
- `res/feishu/prompts/inputs/action_planning.json`
- `res/outlook/prompts/inputs/action_planning.json`
- `res/rdr2/prompts/inputs/action_planning.json`
- `res/stardew/prompts/inputs/action_planning.json`
- `res/xiuxiu/prompts/inputs/action_planning.json`
- `conf/azure_text_config.json`
- `conf/azure_vis_config.json`
- `conf/claude_config.json`
- `conf/env_config_capcut.json`
- `conf/env_config_chrome.json`
- `conf/env_config_dealers.json`
- `conf/env_config_feishu.json`
- `conf/env_config_outlook.json`
- `conf/env_config_rdr2_open_ended_mission.json`
- `conf/env_config_skylines.json`
- `conf/env_config_stardew_cultivation.json`
- `conf/env_config_stardew_farm_clearup.json`
- `conf/env_config_stardew_shopping.json`
- `conf/env_config_xiuxiu.json`
- `conf/openai_config.json`
- `conf/openai_t_config.json`
- `conf/restful_claude_config.json`
- `cradle/provider/module/action_planning.py`
- `cradle/provider/process/action_planning.py`
- `cradle/environment/capcut/tool_skills/__init__.py`
- `cradle/environment/capcut/tool_skills/tools.py`
- `res/capcut/prompts/inputs/self_reflection.json`
- `res/chrome/prompts/inputs/self_reflection.json`
- `res/feishu/prompts/inputs/self_reflection.json`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Six-module GUI loop: information gathering, self-reflection, task inference, skill curation, action planning, and memory, with keyboard/mouse execution. It works with frozen MLLMs.

## Symbol-level code anchors

- `cradle/provider/module/action_planning.py:16` — `ActionPlanningProvider`
- `cradle/provider/process/action_planning.py:14` — `ActionPlanningPreprocessProvider`
- `cradle/environment/capcut/tool_skills/tools.py:17` — `get_information_from_video`
- `runner.py:12` — `main`
- `cradle/config/config.py:20` — `Config`
- `cradle/environment/environment_registry.py:3` — `register_environment`
- `cradle/environment/skill.py:19` — `Skill`
- `cradle/environment/skill_registry.py:31` — `register_skill`
- `cradle/environment/skill_registry_factory.py:6` — `SkillRegistryFactory`
- `cradle/environment/ui_control.py:5` — `UIControl`
- `cradle/environment/ui_control_factory.py:6` — `UIControlFactory`
- `cradle/environment/utils.py:10` — `serialize_skills`
