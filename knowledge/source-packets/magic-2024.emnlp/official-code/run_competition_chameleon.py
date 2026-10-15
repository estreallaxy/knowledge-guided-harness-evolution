import time
import os
import json
import copy
from tqdm import tqdm
from chatarena.config import ArenaConfig
from chatarena.arena_new import Arena
from chatarena.model_mapping import check_model_available


class Competition_Chameleon():
    def __init__(self, topics_dir='topics_release'):
        
        
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)

        # 获取当前文件的目录
        current_dir = os.path.dirname(current_file)
        
        self.setting_dir = os.path.join(current_dir, f'{topics_dir}/chameleon/settings')
        
        self.win_count = {"chameleon":0, "non-chameleon":0}
        
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
        # check competition template
        config_path = f"{config_dir}/{competition}.json"
        assert os.path.exists(config_path), f"Cannot find the config path:{config_path}"
        
        # folder for saving all competitions
        save_dir = f"{save_root}/{test_player_model_name}_{competition}_vs_{base_player_model_name}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # initial competition setting
        with open(config_path) as f:
            config = json.load(f)
        arena_config_base = ArenaConfig(config)

        # set environment type
        if test_player_model_name.find("-pgm")>=0: # change environment to PGM based
            arena_config_base["environment"]["env_type"] = "chameleon_competition_pgm"


        # set player models
        if "non_chameleon" in competition:
            test_player_role = "non-chameleon"
            base_player_role = "chameleon"
        elif "chameleon" in competition:
            test_player_role = "chameleon"
            base_player_role = "non-chameleon"
        else:
            assert 0, f"The competition name is not legal{competition}"
            raise AssertionError("error")
            
        arena_config_base["environment"]["competition"][test_player_role]["model"] = test_player_model_name
        arena_config_base["environment"]["competition"][base_player_role]["model"] = base_player_model_name
        if fix_base_model: # if fix base model, add -fix for base player
            arena_config_base["environment"]["competition"][base_player_role]["model"] += '-fix'
        arena_config_base["environment"]["competition"][test_player_role]["backend_type"] = test_player_backend
        arena_config_base["environment"]["competition"][base_player_role]["backend_type"] = base_player_backend
        


        # execute for num_of_game times
        for game_id in tqdm(range(0,num_of_game)):
            arena_config = copy.deepcopy(arena_config_base)
            # load game setting
            gs_name = f"{self.setting_dir}/{game_id}.json"
            if not os.path.exists(gs_name):
                print("setting not exist", gs_name)
                continue
            # save game file
            fname = f"{save_dir}/{game_id}{postfix}.json"
            if os.path.exists(fname): # skip already executed games
                game_id += 1
                print(f"{fname} exists, skip")
                continue
           
            with open(gs_name) as f:
                game_json = json.load(f)
                if "game_setting" in game_json:
                    gs = game_json["game_setting"]
                else:
                    gs = game_json
                
            # update game settings
            chameleon_name = gs["chameleon_name"]
            arena_config["environment"]["competition"]["random"] = False
            arena_config["environment"]["competition"]["topic"] = gs["topic"]
            arena_config["environment"]["competition"]["code"] = gs["code"]
            arena_config["environment"]["competition"]["chameleon_name"] = gs["chameleon_name"]

            # set backends for each player
            for player_config in arena_config["players"]:
                # base players have predefined clues to fix environment
                if "clue" not in game_json:
                    player_config["clue"] = None
                else:
                    player_config["clue"] = game_json["clue"][player_config["name"]]
                # set role, model and backend for a player
                player_config["role"] = "chameleon" if player_config["name"] == chameleon_name else "non-chameleon"
                player_config["backend"]["model"] = arena_config["environment"]["competition"][player_config["role"]]["model"]
                player_config["backend"]["backend_type"] = arena_config["environment"]["competition"][player_config["role"]]["backend_type"]
                        
            arena = Arena.from_config(arena_config)

            arena.run(num_steps=500)
            win_group = arena.environment.get_win_group()
            self.win_count[win_group] += 1
            arena.environment.log_game(fname)
