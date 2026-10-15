import time
import os
import json
import copy
import sys
from tqdm import tqdm
from chatarena.arena_new import Arena
from chatarena.config import ArenaConfig
from chatarena.model_mapping import check_model_available


class Competition_Under_Cover():
    def __init__(self,topics_dir='topics_release'):
        # load previous game settings
        self.random_setting = False
        self.win_count = {"undercover":0, "non-undercover":0}
        
        
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)

        # 获取当前文件的目录
        current_dir = os.path.dirname(current_file)        
        
        self.setting_dir = os.path.join(current_dir, f'{topics_dir}/undercover/settings')
        
        
    def run(self,config_dir, competition, path, test_player_model_name, base_player_model_name='gpt-4', fix_base_model=False, num_of_game=20):
        
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

        # set player models
        if "non_undercover" in competition:
            test_player_role = "non-undercover"
            base_player_role = "undercover"
        elif "undercover" in competition:
            test_player_role = "undercover"
            base_player_role = "non-undercover"
        else:
            assert 0, f"The competition name is not legal {competition}"
            raise AssertionError("error")
        
        arena_config_base["environment"]["competition"][test_player_role]["model"] = test_player_model_name
        arena_config_base["environment"]["competition"][base_player_role]["model"] = base_player_model_name
        if fix_base_model: # if fix base model, add -fix for base player
            arena_config_base["environment"]["competition"][base_player_role]["model"] += '-fix'
        arena_config_base["environment"]["competition"][test_player_role]["backend_type"] = test_player_backend
        arena_config_base["environment"]["competition"][base_player_role]["backend_type"] = base_player_backend

        # set environment type
        if test_player_model_name.find("-pgm")>=0: # change environment to PGM based
            arena_config_base["environment"]["env_type"] = "undercover_competition_pgm"




        for game_id in tqdm(range(0,num_of_game)):
            arena_config = copy.deepcopy(arena_config_base)
            gs_name = f"{self.setting_dir}/{game_id}.json"
            if not os.path.exists(gs_name):
                print(f"cannot find the setting: {gs_name}")
                continue
            fname = f"{save_dir}/{game_id}{postfix}.json"
            if os.path.exists(fname):
                print("skip", fname)
                game_id += 1
                continue
            with open(gs_name) as f:
                d = json.load(f)
                gs = d["game_setting"]
                undercover_name = gs["undercover_name"]
                arena_config["environment"]["competition"]["random"] = False
                arena_config["environment"]["competition"]["undercover_code"] = gs["undercover_code"]
                arena_config["environment"]["competition"]["non_undercover_code"] = gs["non_undercover_code"]
                arena_config["environment"]["competition"]["undercover_name"] = gs["undercover_name"]

                for player_config in arena_config["players"]:
                    if "clues" in d:
                        player_config["clues"] = d["clues"][player_config["name"]]  
                    else:
                        player_config["clues"] = None     

                    player_config["role"] = "undercover" if player_config["name"] == undercover_name else "non-undercover"

                    player_config["backend"]["model"] = arena_config["environment"]["competition"][player_config["role"]]["model"]
                    player_config["backend"]["backend_type"] = arena_config["environment"]["competition"][player_config["role"]]["backend_type"]

            arena = Arena.from_config(arena_config)
            arena.run(num_steps=50)
            win_group = arena.environment.get_win_group()
            self.win_count[win_group] += 1
            
            arena.environment.log_game(fname)



