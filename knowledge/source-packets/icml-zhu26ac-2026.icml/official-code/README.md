# Talk, Judge, Cooperate: Gossip-Driven Indirect Reciprocity in Self-Interested LLM Agents
This repository implements ALIGN ([ICML 2026](https://icml.cc/Conferences/2026)) in our paper [Talk, Judge, Cooperate: Gossip-Driven Indirect Reciprocity in Self-Interested LLM Agents](https://arxiv.org/abs/2602.07777).

![DecisionProcess](https://shuhui-zhu.github.io/images/DecisionProcess.jpg)
![AgentArchitecture](https://shuhui-zhu.github.io/images/AgentLLM_EG.jpg)


## Initialization
1. Create a virtual environment by `conda create -n gossip python=3.13.1`
2. Activate this environment by `conda activate gossip`
3. Setup your environment by running `pip install -r requirements.txt`
4. Log wandb by `wandb login`

## Usage
1. Save all ur api keys in `~/.bashrc` or `~/.zshrc`, then execute `bash ~/.bashrc` or `bash ~/.zshrc` in the terminal.
2. Specify your hyperparameters (which game, llms, api, etc) in `conf/`. The configuration will automatically be passed to `main.py`. 
    - Modify `conf/config.yaml` to change the default experiment (game), llm model, and api.
    - Modify `conf/experiment/*.yaml` to change the environment/game settings.
3. Run the simulation via `python main.py`. Set WANDB_MODE to "disabled" in `main.py` if you don't want to log to wandb.

## Citation

If you use this code or the ALIGN framework, please cite our paper. 

BibTeX:

```bibtex
@inproceedings{zhu2026talk,
  title={Talk, Judge, Cooperate: Gossip-Driven Indirect Reciprocity in Self-Interested {LLM} Agents},
  author={Zhu, Shuhui and Lin, Yue and Kaistha, Shriya and Li, Wenhao and Wang, Baoxiang and Zha, Hongyuan and Hadfield, Gillian K. and Poupart, Pascal},
  booktitle={Forty-third International Conference on Machine Learning},
  year={2026}
}
```
