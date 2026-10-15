# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `config.yaml`
- `camel/configs.py`
- `run.py`

## Upstream command excerpts

```text
python generate_graph.py --node_num 10 --topology tree
```

```text
python run.py --task "Develop a basic Gomoku game." --name "Gomoku" [--type <software_category>]
```

```text
def aggregate(self, prompt: str, retry_limit: int, unit_num: int, layer_directory: str, graph_depth: int,
               store_dir: str) -> int:
     """Aggregate solutions from predecessors."""
     logging.info(f"Node {self.id} is aggregating with {len(self.pre_solutions)} solutions")

     with open("config.yaml", "r", encoding="utf-8") as f:
         cc_prompt = "\n\n".join(yaml.load(f.read(), Loader=yaml.FullLoader).get("Agent").get("cc_prompt"))
         cc_prompt = self.system_message + cc_prompt

     for file in self.pre_solutions:
         with open(layer_directory + "/solution_{}.txt".format(file), "w") as f:
             for key in self.pre_solutions[file].codebooks.keys():
                 f.write(str(key) + '\n\n' + self.pre_solutions[file].codebooks[key] + '\n\n')

     self.pool = Pool(len(self.pre_solutions), unit_num, layer_directory, self.model)
     for i in range(retry_limit):
         new_codes = self.pool.state_pool_add(layer_directory, cc_prompt, 6000000, prompt,
                                              Codes(),
                                              store_dir,
                                              temperature=1 - self.depth / graph_depth,
                                              )
         if new_codes is None:
             logging.info(f"Retry Aggregation at round {i}!")
         else:
             self.solution = new_codes
             logging.info(f"Node {self.id} has finished aggregation!")
             return 0
     print(f"ERROR: Node {self.id} has reached the retry limit!\n")
     return 1
```

```text
@inproceedings{qian2025scaling,
    title={Scaling Large Language Model-based Multi-Agent Collaboration},
    author={Chen Qian and Zihao Xie and YiFei Wang and Wei Liu and Kunlun Zhu and Hanchen Xia and Yufan Dang and Zhuoyun Du and Weize Chen and Cheng Yang and Zhiyuan Liu and Maosong Sun},
    booktitle={The Thirteenth International Conference on Learning Representations},
    year={2025},
    url={https://openreview.net/forum?id=K3n5jPkrU6}
}

@article{croto,
  title={Multi-Agent Collaboration via Cross-Team Orchestration},
  author={Zhuoyun Du and Chen Qian and Wei Liu and Zihao Xie and YiFei Wang and Rennai Qiu and Yufan Dang and Weize Chen and Cheng Yang and Ye Tian and Xuantang Xiong and Lei Han},
  journal={arXiv preprint arXiv:2406.08979},
  url = {https://arxiv.org/abs/2406.08979},
  year={2024}
}

@article{chatdev,
    title = {ChatDev: Communicative Agents for Software Development},
    author = {Chen Qian and Wei Liu and Hongzhang Liu and Nuo Chen and Yufan Dang and Jiahao Li and Cheng Yang and Weize Chen and Yusheng Su and Xin Cong and Juyuan Xu and Dahai Li and Zhiyuan Liu and Maosong Sun},
    journal = {arXiv preprint arXiv:2307.07924},
    url = {https://arxiv.org/abs/2307.07924},
    year = {2023}
}

@article{colearning,
    title = {Experiential Co-Learning of Software-Developing Agents},
    author = {Chen Qian and Yufan Dang and Jiahao Li and Wei Liu and Zihao Xie and Yifei Wang and Weize Chen and Cheng Yang and Xin Cong and Xiaoyin Che and Zhiyuan Liu and Maosong Sun},
    journal = {arXiv preprint arXiv:2312.17025},
    url = {https://arxiv.org/abs/
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
