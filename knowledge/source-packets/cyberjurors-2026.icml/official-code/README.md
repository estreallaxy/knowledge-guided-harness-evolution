# CyberJurors: A Multi-Agent Simulation Task for E-Commerce Disputes Verdict

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key
Edit `court_models_config.yaml` to configure the API key and model settings:
```yaml
api_key: "your_yunwu_api_key"  
base_url: "https://yunwu.ai/v1"
model_name: "your_model_name"
```
Visit https://yunwu.ai to sign up and obtain an API key.

### 3. Run tests 

```bash
python run_multi_agent_debate.py # process all cases

python run_multi_agent_debate.py --num_cases 10 # process a specified number of cases

python run_multi_agent_debate.py --start_idx 100 --num_cases 50 # start from a specified case
```

## Key Configuration

Edit `court_models_config.yaml` to change parameters:

```yaml
# Parallel settings
parallel_cases: 16 # number of parallel cases

# Jury simulation settings
num_agents: 17 # number of agent jurors
max_epochs: 3 # maximum discussion rounds

use_social_network: true    # whether to use the jury simulation module
following_network_path: "./config/following_network_17.json"  # path for jury network initialization

# IVCoT settings
max_iterations_buyer: 3     # max iterations from buyer cues grounding
max_iterations_seller: 3    # max iterations from seller cues grounding

# Verdict Precedent settings
use_social_consensus: true   # whether to use the precedent base
use_mean_field: true         # whether to use mean-field
early_stop_consensus: 0.8    # consensus threshold

# Data settings
dataset_path: "your_path_to_dataset"  # path to dataset JSON file, e.g., .dataset/test_new.json
output_dir: "./results/multi_agent_debate"   # output directory
experiment_name: "results"      # results are saved under output_dir/experiment_name
```

## Dataset

Download path:

## Preprocessing Module
The code in the `preprocess` folder performs data preprocessing:

- `data_preprocess.py`: fills missing textual evidence and generates descriptions for corresponding image and video evidence.
- `build_social_consensus.py`: builds the precedent base and generates verdict guidelines.

## License

MIT





