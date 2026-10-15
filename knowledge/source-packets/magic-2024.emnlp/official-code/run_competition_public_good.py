import time
import os
import sys
import json
import copy
from tqdm import tqdm
from chatarena.config import ArenaConfig
from chatarena.arena_new import Arena
from prompts.public_good_prompt import global_prompt,global_prompt_nopenalty_v1, role_desc_pgm, global_prompt_nopenalty_v2
from chatarena.model_mapping import check_model_available




class Competition_Public_Good():
    def __init__(self, topics_dir='topics_release'):
        self.win_count = {"win":0, "lose":0}
        
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)

        # 获取当前文件的目录
        current_dir = os.path.dirname(current_file)     
        
        self.setting_dir = os.path.join(current_dir, f'{topics_dir}/public_good/settings')
            
    def run(self,config_dir, competition, path, test_player_model_name, base_player_model_name='gpt-4', fix_base_model=False, num_of_game=21):

        config_dir=config_dir
        competition = competition
        save_root = path
        postfix=""  

        # check backend_types
        test_player_backend = check_model_available(test_player_model_name)
        assert test_player_backend, f"{test_player_model_name} is not supported!"
        base_player_backend = check_model_available(base_player_model_name)
        assert base_player_backend, f"{base_player_model_name} is not supported!"

        config_path = f"{config_dir}/{competition}.json"
        assert os.path.exists(config_path), f"Cannot find the config path:{config_path}"

        with open(config_path) as f:
            config = json.load(f)
        arena_config_base = ArenaConfig(config)

        save_dir = f"{save_root}/{test_player_model_name}_{competition}_vs_{base_player_model_name}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # set environment type
        if test_player_model_name.find("-pgm")>=0: # change environment to PGM based
            arena_config_base["environment"]["env_type"] = "public_good_pgm"
        
        arena_config_base["environment"]["competition"]["test_player"]["model"] = test_player_model_name
        arena_config_base["environment"]["competition"]["non-test_player"]["model"] = base_player_model_name
        if fix_base_model: # if fix base model, add -fix for base player
            arena_config_base["environment"]["competition"]["non-test_player"]["model"] += '-fix'
        arena_config_base["environment"]["competition"]["test_player"]["backend_type"] = test_player_backend
        arena_config_base["environment"]["competition"]["non-test_player"]["backend_type"] = base_player_backend

        for game_id in tqdm(range(0,num_of_game)):
            with open(f"{self.setting_dir}/{game_id}.json") as f:
                gs = json.load(f)
        
            fname = f"{save_dir}/{game_id}{postfix}.json"
            if os.path.exists(fname):
                print(f"skip {fname}")
                continue
            arena_config = copy.deepcopy(arena_config_base)
            test_player_name = gs["test_player_name"]
            arena_config["environment"]["competition"]["test_player_name"] = test_player_name
            arena_config["environment"]["competition"]["random"] = False
            arena_config["global_prompt"] = global_prompt_nopenalty_v2.format(game_round=gs["game_round"], multiplier=gs["multiplier"])
            arena_config["environment"]["competition"]["game_round"] = gs["game_round"]
            arena_config["environment"]["competition"]["multiplier"] = gs["multiplier"]

            for player_config in arena_config["players"]:
                player_config["role"] = "test_player" if player_config["name"] == test_player_name else "non-test_player"
                player_config["backend"]["model"] = arena_config["environment"]["competition"][player_config["role"]]["model"]
                player_config["backend"]["backend_type"] = arena_config["environment"]["competition"][player_config["role"]]["backend_type"]

                if player_config["backend"]["model"].find("pgm")>=0:
                    player_config["role_desc"] = role_desc_pgm
                    player_config["backend"]["max_tokens"] = 256


            arena = Arena.from_config(arena_config)
            arena.run(num_steps=100)
            result = arena.environment.log_game(fname)
            self.win_count[result] += 1
