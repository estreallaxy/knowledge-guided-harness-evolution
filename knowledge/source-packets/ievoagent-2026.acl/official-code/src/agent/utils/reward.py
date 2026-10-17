
from src.agent.utils.rewardFeedback import *
from src.agent.utils.rewardMutualInfo import *

import jsonlines
from tqdm import tqdm
import torch

def compute_reward(input_text, response_text, ufb_type, error_type, device = "cuda", model=None, tokenizer=None, history = []):
    r_ufb = feedback_reward(ufb_type, error_type)
    # -1-1
    r_info = mutual_information_reward(input_text=input_text, response_text=response_text, model=model, tokenizer=tokenizer, history=history, device=device)
    # 0-1
    return r_ufb, r_info

# aline = 

# for i in range(aline["turn"]):
#     history = aline["conversation"][:i*2]
#     input_text = aline["conversation"][i*2]["content"]
#     response_text = aline["conversation"][i*2+1]["content"]
#     ufb_type = aline["user_feedback_category"][i]
#     error_type = aline["llm_response_type"][i]


#     print("UFD_TYPE: ",ufb_type, "ERR_TYPE: ",error_type,"REWARD: ", compute_reward(input_text, response_text, ufb_type, error_type,history = history))




