# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `PR/requirements.txt`
- `Example/c/c__closed__5f93cf43dd6f809d7927abb79884285ad77e8a58__20240124084751/requirements.txt`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124013316/requirements.txt`
- `Example/java/java__merged__6e3c6d17d943f5ac70b421653eb167e0c34b119f__20240124041718/requirements.txt`
- `Example/javascript/javascript__closed__6e9a80d93b470aef4978677ed0b7c9996fddbe20__20240124080405/requirements.txt`
- `Example/php/php__closed__6679f059b9a0972a90df198471188da652f5c547__20240124053337/requirements.txt`
- `Example/ruby/ruby__merged__584f72e7f4c65066ccbd2183af76bf380b6eb974__20240124012950/requirements.txt`
- `Example/video-exmple-3-security/javascript__merged__de00740e21aa6c5371e4a274dd433128bc9aa5af__20240124011600/requirements.txt`
- `camel/configs.py`
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
- `Example/php/php__closed__6679f059b9a0972a90df198471188da652f5c547__20240124053337/RoleConfig.json`

## Upstream command excerpts

```text
CodeAgent/
├── EMNLP-CodeAgent 2/
│   ├── Languages/
│   │   ├── c/
│   │   ├── c#/
│   │   ├── c++/
│   │   ├── go/
│   │   ├── java/
│   │   ├── javascript/
│   │   ├── php/
│   │   ├── python/
│   │   └── ruby/
│   ├── online_log/
│   │   ├── static/
│   │   │   ├── avatars/
│   │   │   ├── replay/
│   │   │   │   ├── css/
│   │   │   │   └── js/
│   │   │   └── other files
│   └── ScriptTest/
│       ├── top_Perl_repos.json
│       ├── codeagent_data.py
│       ├── config.json
│       └── codeagent.log
└── __MACOSX/
```

```text
conda activate CodeAgent_conda_env
```

```text
export OPENAI_API_KEY="your_openai_api_key"
```

```text
python3 run.py --ifcode "commit" --name "eccl-codereview" --commit "Diff-CodeAgent4.0/6e3c6d17d943f5ac70b421653eb167e0c34b119f-commit.txt" --commitmessage "Diff-CodeAgent4.0/6e3c6d17d943f5ac70b421653eb167e0c34b119f-message.txt" --originalfile "Diff-CodeAgent4.0/6e3c6d17d943f5ac70b421653eb167e0c34b119f-context.txt"
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
