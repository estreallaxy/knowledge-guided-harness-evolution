# Exact source anchors

## Selected mechanism

Specialized review roles plus a QA-Checker supervisor that checks relevance to the original question before aggregation. Ablations compare agent/supervisor contributions.

## Paper anchors

- p. 1: results demonstrate CodeAgent’s effective- et al., 2023) to perform a task. Agent-based ap-
- p. 3: framework. The roles of the characters are il-
- p. 7: Ablation Study. As shown in Table 2, we con- Average CodeBERT GPT-3.5 GPT-4.0 COT ReAct CodeAgent Imp (pp)
- p. 9: Limitations
- p. 9: limitations. Further, more comprehensive testing nerability detection: Are we there yet? IEEE Trans-
- p. 13: method to enhance answer quality. This frame-
- p. 15: method for suggesting comments during code re- coherence, avoiding unproductive loops, and fos-
- p. 19: Algorithm 1 Integrated Workflow of
- p. 25: method, the check for 'is_authenticated' has been removed, which is inconsistent with the commit message. It would be helpful
- p. 25: method, update the commit message to reflect the change in keys from 'user_id' and 'client_id' to 'user' and 'client'.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `PR/README.md`
- `PR/requirements.txt`
- `Example/c/c__closed__5f93cf43dd6f809d7927abb79884285ad77e8a58__20240124084751/requirements.txt`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124013316/requirements.txt`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124041718/requirements.txt`
- `Example/javascript/javascript__closed__6e9a80d93b470aef4978677ed0b7c9996fddbe20__20240124080405/requirements.txt`
- `Example/php/php__closed__6679f059b9a0972a90df198471188da652f5c547__20240124053337/requirements.txt`
- `Example/ruby/ruby__merged__584f72e7f4c65066ccbd2183af76bf380b6eb974__20240124012950/requirements.txt`
- `Example/video-exmple-3-security/javascript__merged__de00740e21aa6c5371e4a274dd433128bc9aa5af__20240124011600/requirements.txt`
- `camel/configs.py`
- `camel/agents/critic_agent.py`
- `camel/agents/tool_agents/__init__.py`
- `camel/agents/tool_agents/base.py`
- `camel/agents/tool_agents/hugging_face_tool_agent.py`
- `CompanyConfig/Default/ChatChainConfig.json`
- `CompanyConfig/Default/PhaseConfig.json`
- `CompanyConfig/Default/RoleConfig.json`
- `Example/c#/c#__merged__0e231c7a81b318e9eade972f7b877e66128ed67d__20240124023440/ChatChainConfig.json`
- `Example/c#/c#__merged__0e231c7a81b318e9eade972f7b877e66128ed67d__20240124023440/PhaseConfig.json`
- `Example/c#/c#__merged__0e231c7a81b318e9eade972f7b877e66128ed67d__20240124023440/RoleConfig.json`
- `Example/c/c__closed__5f93cf43dd6f809d7927abb79884285ad77e8a58__20240124084751/ChatChainConfig.json`
- `Example/c/c__closed__5f93cf43dd6f809d7927abb79884285ad77e8a58__20240124084751/PhaseConfig.json`
- `Example/c/c__closed__5f93cf43dd6f809d7927abb79884285ad77e8a58__20240124084751/RoleConfig.json`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124013316/ChatChainConfig.json`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124013316/PhaseConfig.json`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124013316/RoleConfig.json`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124041718/ChatChainConfig.json`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124041718/PhaseConfig.json`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124041718/RoleConfig.json`
- `Example/javascript/javascript__closed__6e9a80d93b470aef4978677ed0b7c9996fddbe20__20240124080405/ChatChainConfig.json`
- `Example/javascript/javascript__closed__6e9a80d93b470aef4978677ed0b7c9996fddbe20__20240124080405/PhaseConfig.json`
- `Example/javascript/javascript__closed__6e9a80d93b470aef4978677ed0b7c9996fddbe20__20240124080405/RoleConfig.json`
- `Example/php/php__closed__6679f059b9a0972a90df198471188da652f5c547__20240124053337/ChatChainConfig.json`
- `Example/php/php__closed__6679f059b9a0972a90df198471188da652f5c547__20240124053337/PhaseConfig.json`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Specialized review roles plus a QA-Checker supervisor that checks relevance to the original question before aggregation. Ablations compare agent/supervisor contributions.

## Symbol-level code anchors

- `Example/video-exmple-3-security/javascript__merged__de00740e21aa6c5371e4a274dd433128bc9aa5af__20240124011600/requirements.txt:1` — `registerReqListeners`
- `camel/configs.py:19` — `ChatGPTConfig`
- `camel/agents/critic_agent.py:27` — `CriticAgent`
- `camel/agents/tool_agents/base.py:17` — `BaseToolAgent`
- `camel/agents/tool_agents/hugging_face_tool_agent.py:20` — `HuggingFaceToolAgent`
- `Baselines/codeBERT.py:11` — `classify_text`
- `Baselines/codeT5.py:8` — `zero_shot_classification`
- `camel/generators.py:21` — `SystemMessageGenerator`
- `camel/human.py:22` — `Human`
- `camel/model_backend.py:27` — `ModelBackend`
- `camel/typing.py:17` — `TaskType`
- `camel/utils.py:31` — `count_tokens_openai_chat_models`
