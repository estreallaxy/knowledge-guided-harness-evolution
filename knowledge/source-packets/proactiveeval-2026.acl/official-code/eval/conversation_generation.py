import os
import json
import time
import random
import httpx
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tools import get_model_response
from prompt.conversation_generation_prompt import (
    System_role_prompt, 
    human_role_prompt, 
    collaboration_type, 
    Judge_conversation_prompt
)
from config import UnifiedConfig

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

class Conversation:
    def __init__(self, system_prompt, human_prompt, window_size=6):
        self.system_prompt = system_prompt
        self.human_prompt = human_prompt
        self.chatbot_history = [{"role": "system", "content": system_prompt}]
        self.human_history = [{"role": "system", "content": human_prompt}]
        self.log_history = []
        self.window_size = window_size

    def update_history(self, role, content):
        if role == "chatbot":
            self.chatbot_history.append({"role": "assistant", "content": content})
            self.human_history.append({"role": "user", "content": content})
            self.log_history.append({"role": "assistant", "content": content})
            self._maintain_window(self.chatbot_history)
        elif role == "human":
            self.human_history.append({"role": "assistant", "content": content})
            self.chatbot_history.append({"role": "user", "content": '/no_think'+content})
            self.log_history.append({"role": "user", "content": content})
            self._maintain_window(self.human_history)
        else:
            raise ValueError("Invalid role. Choose 'chatbot' or 'human'.")

    def _maintain_window(self, history):
        if len(history) > self.window_size + 1:
            history[:] = [history[0]] + history[-self.window_size:]

class ConversationGenerator:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.chatbot_client = OpenAI(
            api_key=config.evaluated_model.api_key,
            base_url=config.evaluated_model.base_url,
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )
        self.user_client = OpenAI(
            api_key=config.judge_model.api_key,
            base_url=config.judge_model.base_url,
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )
    
    def judge_whether_continue(self, conversation, target, sub_target):
        judge_prompt = Judge_conversation_prompt.format(
            conversation=conversation, 
            target=target, 
            sub_target=sub_target
        )
        messages = [{"role": "system", "content": judge_prompt}]
        judgement = get_model_response(
            self.user_client, 
            self.config.judge_model.model_name, 
            messages, 
            temperature=self.config.judge_model.temperature, 
            eval_mode=True
        )
        print(judgement)
        return "True" in judgement

    def conversation_generation(self, conversation, target, sub_target):
        # generate chatbot response
        chatbot_message = get_model_response(
            self.chatbot_client, 
            self.config.evaluated_model.model_name, 
            conversation.chatbot_history, 
            temperature=self.config.evaluated_model.temperature
        )
        conversation.update_history("chatbot", chatbot_message)
        print(f"{GREEN}chatbot_message:{RESET}\n{chatbot_message}\n")
        
        # generate simulated user response
        human_message = get_model_response(
            self.user_client, 
            self.config.judge_model.model_name, 
            conversation.human_history, 
            temperature=self.config.judge_model.temperature
        )
        print(f"{RED}human_message:{RESET}\n{human_message}")
        conversation.update_history("human", human_message)
        
        # judge whether to continue
        break_sign = self.judge_whether_continue(conversation.log_history, target, sub_target)
        return conversation, break_sign

    def create_prompts(self, environment, target, sub_target, task_description, collaboration):
        system_prompt = System_role_prompt.format(
            user_information=environment["user_information"],
            trigger_factor=environment["trigger_factor"],
            task_description=self.config.fixed_params["domain_descriptions"][task_description],
            target=target,
            sub_target=sub_target
        )

        human_prompt = human_role_prompt.format(
            human_information=environment["user_information"].replace("The user", "You").replace("They", "You"),
            collaboration_type=collaboration_type[collaboration],
            trigger_factor=environment["trigger_factor"]
        )
        
        return system_prompt, human_prompt

    def single_test(self, environment, target, sub_target, collaboration, task_description, max_turns=6):
        system_prompt, human_prompt = self.create_prompts(
            environment, target, sub_target, task_description, collaboration
        )
        
        conversation = Conversation(system_prompt, human_prompt, self.config.fixed_params["conversation_params"]["window_size"])

        for turn in range(max_turns):
            conversation, break_sign = self.conversation_generation(
                conversation, target, sub_target
            )
            if break_sign:
                break

        return {
            "environment": environment,
            "target": target,
            "sub_target": sub_target,
            "conversation": conversation.log_history, 
            "collaboration_type": collaboration
        }

    def process_entry(self, entry, collaboration, task_description):
        environment = entry["item"]["environment"]
        target = entry["item"]["target"]
        sub_target = entry["item"]["sub_target"]
        return self.single_test(
            environment, target, sub_target, 
            collaboration, task_description
        )

    def test(self, test_data_path, test_results_path, task_description):
        with open(test_data_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
        
        results = []
        
        tasks = []

        begin_index = self.config.fixed_params["conversation_params"]["begin_index"]
        end_index = self.config.fixed_params["conversation_params"]["end_index"]
        
        for entry in test_data[begin_index:end_index]:
            for collaboration in collaboration_type.keys():
                tasks.append((entry, collaboration))
        
        print("Starting parallel processing...")
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=self.config.task_config.max_workers) as executor:
            future_to_task = {
                executor.submit(self.process_entry, entry, collab, task_description): (entry, collab) 
                for entry, collab in tasks
            }
            
            for future in tqdm(as_completed(future_to_task), total=len(tasks), desc="Processing test data"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    entry, collab = future_to_task[future]
                    print(f'Task for entry {entry["item"]["target"]} with collaboration {collab} generated an exception: {exc}')
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Parallel processing finished. Total time taken: {total_time:.2f} seconds.")

        with open(test_results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print("Test results saved.")

def main():
    config = UnifiedConfig()
    if config.task_config.task in ["dialogue_guidance", "all"]:
        model_name_safe = config.get_model_name_safe(config.evaluated_model.model_name)
        if not os.path.exists(f"dialogue_guidance_generation/{model_name_safe}"):
            print("start dialogue_guidance task")
            
            generator = ConversationGenerator(config)
            
            result_base_dir = Path(f"dialogue_guidance_generation/{model_name_safe}")
            result_base_dir.mkdir(parents=True, exist_ok=True)
            print(f"create directory: {result_base_dir}")
            
            # process each domain
            for domain in config.fixed_params["domains"]:
                file_domain = domain.replace("/", "_")
                test_data_file = f"{config.fixed_params['dataset_base_path']}/{file_domain}/eval.json"
                result_file = result_base_dir / f"{file_domain}_v{config.task_config.version_num}.json"
                
                print(f"\nprocess domain: {domain}")
                generator.test(test_data_file, result_file, file_domain)
        else:
            print("dialogue_guidance results exist, skip generation step")
    else:
        print("skip dialogue_guidance task")

if __name__ == "__main__":
    main() 