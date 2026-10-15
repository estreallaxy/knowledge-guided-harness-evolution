# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `conf/env_config_rdr2_main_storyline.json`
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
- `runner.py`
- `cradle/config/__init__.py`
- `cradle/config/config.py`
- `cradle/runner/app_runner.py`
- `cradle/runner/dealers_runner.py`
- `cradle/runner/rdr2_runner.py`
- `cradle/runner/skylines_runner.py`
- `cradle/runner/stardew_runner.py`

## Upstream command excerpts

```text
OA_OPENAI_KEY = "abc123abc123abc123abc123abc123ab"
RF_CLAUDE_AK = "abc123abc123abc123abc123abc123ab" # Access Key for Claude
RF_CLAUDE_SK = "123abc123abc123abc123abc123abc12" # Secret Access Key for Claude
AZ_OPENAI_KEY = "123abc123abc123abc123abc123abc12"
AZ_BASE_URL = "https://abc123.openai.azure.com/"
RF_CLAUDE_AK = "abc123abc123abc123abc123abc123ab"
RF_CLAUDE_SK = "123abc123abc123abc123abc123abc12"
IDE_NAME = "Code"
```

```text
# Clone the repository
git clone https://github.com/BAAI-Agents/Cradle.git
cd Cradle

# Create a new conda environment
conda create --name cradle-dev python=3.10
conda activate cradle-dev
pip install -r requirements.txt
```

```text
1. Option 1
# Download best-matching version of specific model for your spaCy installation
python -m spacy download en_core_web_lg

or

# pip install .tar.gz archive or .whl from path or URL
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1.tar.gz

2. Option 2
# Copy this url https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1.tar.gz
# Paste it in the browser and download the file to res/spacy/data
cd res/spacy/data
pip install en_core_web_lg-3.7.1.tar.gz
```

```text
Cradle
├── cache # Cache the GroundingDino model and the bert-base-uncased model
├── conf # ⭐⭐⭐ The configuration files for the environment and the llm model
│   ├── env_config_dealers.json
│   ├── env_config_rdr2_main_storyline.json
│   ├── env_config_rdr2_open_ended_mission.json
│   ├── env_config_skylines.json
│   ├── env_config_stardew_cultivation.json
│   ├── env_config_stardew_farm_clearup.json
│   ├── env_config_stardew_shopping.json
│   ├── openai_config.json
│   ├── claude_config.json
│   ├── restful_claude_config.json
│   └── ...
├── deps # The dependencies for the Cradle framework, ignore this folder
├── docs # The documentation for the Cradle framework, ignore this folder
├── res # The resources for the Cradle framework
│   ├── models # Ignore this folder
│   ├── tool # Subfinder for RDR2
│   ├── [game or software] # ⭐⭐⭐ The resources for game, exmpale: rdr2, dealers, skylines, stardew, outlook, chrome, capcut, meitu, feishu
│   │   ├── prompts # The prompts for the game
│   │   │   └── templates
│   │   │       ├── action_planning.prompt
│   │   │       ├── information_gathering.prompt
│   │   │       ├── self_reflection.prompt
│   │   │       └── task_inference.prompt
│   │   ├── skills # The skills json for the game, it will be generated automatically
│   │   ├── icons # The icons difficult for GPT-4 to recognize in the game can be replaced with text for better recognition using an icon replacer
│   │   └── saves # Save files in the game
│   └── ...
├── requirements.txt # The requirements for the Cradle framework
├── runner.py # The main entry for the Cradle 
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
