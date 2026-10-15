import time
import os
import sys
import json
import copy
from tqdm import tqdm
from chatarena.config import ArenaConfig
from chatarena.arena_new import Arena
from prompts.airportfee_prompt import role_desc_pgm, global_prompt
from chatarena.model_mapping import check_model_available



class Competition_Airportfee():
    def __init__(self,topics_dir='topics_release'):
        
        self.first_msg_template='''As Player {player}, representing Airline {airline}, I propose the following cost distribution:
        Airline A: {a}%
        Airline B: {b}%
        Airline C: {c}%\"
        '''
        self.win_count = {"agree":0, "fail":0}
        self.max_turns=5
        
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)

        # 获取当前文件的目录
        current_dir = os.path.dirname(current_file)        
        
        self.setting_dir = os.path.join(current_dir, f'{topics_dir}/airportfee/settings')
        
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
            arena_config_base["environment"]["env_type"] = "airport_fee_allocation_pgm"

        arena_config_base["environment"]["competition"]["test_player"]["model"] = test_player_model_name
        arena_config_base["environment"]["competition"]["non-test_player"]["model"] = base_player_model_name
        if fix_base_model: # if fix base model, add -fix for base player
            arena_config_base["environment"]["competition"]["non-test_player"]["model"] += '-fix'
        arena_config_base["environment"]["competition"]["test_player"]["backend_type"] = test_player_backend
        arena_config_base["environment"]["competition"]["non-test_player"]["backend_type"] = base_player_backend
        
        
        player_names =["Player 1","Player 2","Player 3"]
        airlines = ["Airline A", "Airline B","Airline C"]
        for game_id in tqdm(range(0,num_of_game)):
            with open(f"{self.setting_dir}/{game_id}.json") as f:
                gs = json.load(f)

            fname = f"{save_dir}/{game_id}.json"
            if os.path.exists(fname):
                print("skip: ", fname)
                continue

            # print(gs["topic"]) 
            arena_config = copy.deepcopy(arena_config_base)
            test_player_name = gs["test_player_name"]
            arena_config["global_prompt"] = global_prompt.format(max_turns=self.max_turns)
            arena_config["environment"]["competition"]["test_player_name"] = test_player_name
            arena_config["environment"]["competition"]["random"] = False
            arena_config["environment"]["competition"]["topic"] = gs["topic"]
            arena_config["environment"]["competition"]["max_turns"] = self.max_turns

            for player_config in arena_config["players"]:
                
                pr = gs["proposal"][player_config["name"]]
                pi = player_names.index(player_config["name"])
                player_config["first_msg"] = self.first_msg_template.format(player=player_config["name"], airline=airlines[pi], a=pr[0],b=pr[1],c=pr[2])

                player_config["role"] = "test_player" if player_config["name"] == test_player_name else "non-test_player"
                player_config["backend"]["model"] = arena_config["environment"]["competition"][player_config["role"]]["model"]
                player_config["backend"]["backend_type"] = arena_config["environment"]["competition"][player_config["role"]]["backend_type"]

                if player_config["backend"]["model"].find("pgm")>=0:
                    pidx = player_names.index(test_player_name)
                    player_config["role_desc"] = role_desc_pgm.format(player=player_names[pidx], airline=airlines[pidx])
                    player_config["backend"]["max_tokens"] = 256


            arena = Arena.from_config(arena_config)
            arena.run(num_steps=100)
            result = arena.environment.log_game(fname)
            self.win_count[result] += 1

