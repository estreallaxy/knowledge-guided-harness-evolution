import os
import json
import argparse
import httpx
from tqdm import tqdm
from openai import OpenAI
from tools import get_model_response, clean_json_response
from concurrent.futures import ThreadPoolExecutor, as_completed
from prompt.data_refiement_prompt import (
    target_test_prompt, 
    evaluation_test_prompt,
    user_information_rewrite_prompt,
    trigger_factor_rewrite_prompt,
    user_information_add_noise_prompt,
    trigger_factor_add_noise_prompt,
    final_check_prompt,
    trigger_factor_description_prompt,
    user_information_domain_rules,
    tigger_event_domain_rules,
    domain_prompts
)

# Configuration
exec(open("config.yaml").read())

def load_examples_by_domain(domain, example_type):
    """Load examples for specific domain and type from examples files"""
    example_files = {
        "evaluation_test": "examples/evaluation_test_examples.json",
        "user_information_rewrite": "examples/user_information_rewrite_examples.json",
        "trigger_factor_rewrite": "examples/trigger_factor_rewrite_examples.json",
        "user_information_add_noise": "examples/user_information_add_noises_examples.json",
        "trigger_factor_add_noise": "examples/trigger_factor_add_noises_examples.json"
    }
    
    file_path = example_files.get(example_type)
    if not file_path or not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        all_examples = json.load(f)
    
    domain_examples = []
    for example in all_examples:
        if example.get("domain") == domain:
            domain_examples.append(example)
    
    return domain_examples

def difficulty_filter(client, environment, target, domain):
    domain_prompt = trigger_factor_description_prompt.get(domain, "")
    test_prompt = target_test_prompt.format(
        domain_prompt=domain_prompt, 
        environment=environment
    )
    
    results = { 
        "score": 0,
        "weak": {"response": "", "result": False, "reason": ""},
        "middle": {"response": "", "result": False, "reason": ""},
        "strong": {"response": "", "result": False, "reason": ""}
    }

    models = [
        {"type": "weak", "model": "qwen/qwen-2.5-14b-instruct"}, 
        {"type": "middle", "model": "qwen/qwen-2.5-32b-instruct"}, 
        {"type": "strong", "model": "gpt-4o"}
    ]
    
    # Load evaluation examples
    eval_examples = load_examples_by_domain(domain, "evaluation_test")
    eval_examples_str = json.dumps(eval_examples, ensure_ascii=False, indent=2) if eval_examples else "[]"
    
    messages = [{"role": "system", "content": test_prompt}]

    for model in models:
        while True:
            try:
                response = get_model_response(
                    client, 
                    model_name=model["model"], 
                    messages=messages, 
                    temperature=0.0
                )
                
                json_response = clean_json_response(response)
                print(f"Response from {model['type']}: {json_response}")
                results[model["type"]]["response"] = json_response
                
                # Evaluate the generated target
                eval_prompt = evaluation_test_prompt.format(
                    examples=eval_examples_str,
                    environment=environment, 
                    generated_target=json_response.get("Target", ""), 
                    target=target
                )
                
                eval_message = [{"role": "system", "content": eval_prompt}]
                eval_response = get_model_response(
                    client, 
                    model_name="gpt-4o", 
                    messages=eval_message,
                    temperature=0.0,
                    eval_mode=True
                )
                
                eval_json_response = clean_json_response(eval_response)
                print(f"Eval response from {model['type']}: {eval_json_response}")
                
                if eval_json_response.get("judge") == "True":
                    results[model['type']]["result"] = True
                    results[model['type']]["reason"] = eval_json_response.get("reason", "")
                    results["score"] += 1
                    break
                else:
                    results[model['type']]["result"] = False
                    results[model['type']]["reason"] = eval_json_response.get("reason", "")
                    break
            except Exception as e:
                print(f"Error from {model['type']}: {e}")
                continue

    return results

def refine_environment(client, environment, target, domain):
    
    # Load examples for refinement
    user_info_examples = load_examples_by_domain(domain, "user_information_rewrite")
    trigger_examples = load_examples_by_domain(domain, "trigger_factor_rewrite")
    user_noise_examples = load_examples_by_domain(domain, "user_information_add_noise")
    trigger_noise_examples = load_examples_by_domain(domain, "trigger_factor_add_noise")
    
    user_info_examples_str = json.dumps(user_info_examples, ensure_ascii=False, indent=2) if user_info_examples else "[]"
    trigger_examples_str = json.dumps(trigger_examples, ensure_ascii=False, indent=2) if trigger_examples else "[]"
    user_noise_examples_str = json.dumps(user_noise_examples, ensure_ascii=False, indent=2) if user_noise_examples else "[]"
    trigger_noise_examples_str = json.dumps(trigger_noise_examples, ensure_ascii=False, indent=2) if trigger_noise_examples else "[]"
    
    # Obfuscation Rewrite for user information
    domain_rule = user_information_domain_rules.get(domain, "")
    user_information_rewrite_prompt_formatted = user_information_rewrite_prompt.format(
        Domain_Rule=domain_rule,
        Examples=user_info_examples_str,
        user_information=environment["user_information"]
    )
    
    rewrite_user_information = get_model_response(
        client, 
        model_name="gpt-4o", 
        messages=[{"role": "system", "content": user_information_rewrite_prompt_formatted}], 
        temperature=0.7
    )
    
    if rewrite_user_information.startswith("Output:"):
        rewrite_user_information = rewrite_user_information[8:].strip()
    
    print(f"Refined user information: {rewrite_user_information}")

    # Obfuscation Rewrite for trigger event
    trigger_domain_rule = tigger_event_domain_rules.get(domain, "")
    trigger_factor_rewrite_prompt_formatted = trigger_factor_rewrite_prompt.format(
        domain_rule=trigger_domain_rule,
        example=trigger_examples_str,
        trigger_factor=environment["trigger_factor"],
        target=target
    )
    
    refine_trigger_factor = get_model_response(
        client, 
        model_name="gpt-4o", 
        messages=[{"role": "system", "content": trigger_factor_rewrite_prompt_formatted}], 
        temperature=0.7
    )
    
    if refine_trigger_factor.startswith("Output:"):
        refine_trigger_factor = refine_trigger_factor[8:].strip()
    
    print(f"Refined trigger factor: {refine_trigger_factor}")

    # Noise Injection for user information
    user_information_add_noise_prompt_formatted = user_information_add_noise_prompt.format(
        example=user_noise_examples_str,
        user_information=rewrite_user_information
    )
    
    add_noise_user_information = get_model_response(
        client, 
        model_name="gpt-4o", 
        messages=[{"role": "system", "content": user_information_add_noise_prompt_formatted}], 
        temperature=0.7
    )
    
    if add_noise_user_information.startswith("Output:"):
        add_noise_user_information = add_noise_user_information[8:].strip()
    
    print(f"Added noise to user information: {add_noise_user_information}")

    # Noise Injection for trigger factor
    trigger_factor_add_noise_prompt_formatted = trigger_factor_add_noise_prompt.format(
        example=trigger_noise_examples_str,
        trigger_factor=refine_trigger_factor,
        target=target
    )
    
    add_noise_trigger_factor = get_model_response(
        client, 
        model_name="gpt-4o", 
        messages=[{"role": "system", "content": trigger_factor_add_noise_prompt_formatted}], 
        temperature=0.7
    )
    
    if add_noise_trigger_factor.startswith("Output:"):
        add_noise_trigger_factor = add_noise_trigger_factor[8:].strip()
    
    print(f"Added noise to trigger factor: {add_noise_trigger_factor}")
    
    final_environment = {
        "user_information": add_noise_user_information, 
        "trigger_factor": add_noise_trigger_factor
    }
    
    print(f"Final environment: {final_environment}")
    return final_environment

def final_check_data(client, environment, target, sub_targets, domain):
    domain_prompt = domain_prompts.get(domain, "")
    prompt = final_check_prompt.format(
        description=domain_prompt,
        environment=environment,
        target=target,
        sub_targets=sub_targets
    )
    
    results = {i: None for i in range(1, 6)}
    
    def get_result(index, client_obj, model_name):
        try:
            response = get_model_response(
                client_obj, 
                model_name=model_name, 
                messages=[{"role": "system", "content": prompt}],
                temperature=0.0,
                eval_mode=True
            )
            return index, clean_json_response(response)
        except Exception as e:
            print(f"Error in model {index}: {e}")
            return index, {"judge": "False", "reason": f"Error: {e}"}
    
    tasks = [
        (1, client, "gpt-4o", True),
        (2, client, "deepseek/deepseek-chat", True),
        (3, client, "x-ai/grok-3", True),
        (4, client, "qwen/qwen-2.5-72b-instruct", True),
        (5, client, "anthropic/claude-3.7-sonnet", True)
    ]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {executor.submit(get_result, idx, client_obj, model, is_gpt): idx 
                          for idx, client_obj, model, is_gpt in tasks}
        
        for future in as_completed(future_to_task):
            idx, result = future.result()
            results[idx] = result
            print(f"result_{idx}: {result}")
    
    true_count = sum(1 for result in results.values() if result and result.get("judge") == "True")
    flag = true_count >= 3
    
    return flag, results[1], results[2], results[3], results[4], results[5]

def refine_environment_pipeline(domain, input_file, output_file):
    
    client = OpenAI(
        api_key=os.environ.get("GENERATION_API_KEY"),
        base_url=os.environ.get("GENERATION_BASE_URL"),
        http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
    )
    
    # Load input data
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    with open(input_file, "r", encoding="utf-8") as f:
        environments = json.load(f)
    
    fair_data = []
    hard_data = []

    for environment_data in tqdm(environments, desc=f"Processing {domain} environments"):
        turns = 0
        target = environment_data["best_target"]["target"]
        sub_target = environment_data["best_target"]["sub_target"]
        environment = environment_data["environment"]
        
        while turns < 5:
            difficulty = difficulty_filter(client, environment, target, domain)
            
            # only a few model predict the target correctly, the evaluation loop is terminated
            if difficulty["score"] <= 1:
                if difficulty["score"] == 0:
                    hard_data.append({
                        "environment": environment,
                        "target": target,
                        "sub_target": sub_target,
                        "difficulty": difficulty
                    })
                else:
                    fair_data.append({
                        "environment": environment,
                        "target": target,
                        "sub_target": sub_target,
                        "difficulty": difficulty
                    })
                break
            else:  # too easy, need to refine
                environment = refine_environment(client, environment, target, domain)
                print("--------------------------------")
                turns += 1
    
    # Save refined results
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(fair_data, f, ensure_ascii=False, indent=4, sort_keys=False)
    
    print(f"\nRefinement completed!")
    print(f"Fair data: {len(fair_data)} samples")
    print(f"Hard data: {len(hard_data)} samples")
    print(f"Results saved to: {output_file}")
    
    return fair_data, hard_data

def final_check(domain, refined_file, final_file):
    client = OpenAI(
        api_key=os.environ.get("GENERATION_API_KEY"),
        base_url=os.environ.get("GENERATION_BASE_URL"),
        http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
    )
    
    if not os.path.exists(refined_file):
        raise FileNotFoundError(f"Refined file not found: {refined_file}")
    
    with open(refined_file, "r", encoding="utf-8") as f:
        refined_data = json.load(f)
    
    final_data = []
    
    for item in tqdm(refined_data, desc=f"Final checking {domain} data"):
        if item["difficulty"]["score"] in [0, 1]:
            environment = item["environment"]
            target = item["target"]
            sub_targets = item["sub_target"]
            
            flag, result_1, result_2, result_3, result_4, result_5 = final_check_data(
                client, environment, target, sub_targets, domain
            )
            
            if flag:
                final_data.append({
                    "item": item,
                    "result_1": result_1,
                    "result_2": result_2,
                    "result_3": result_3,
                    "result_4": result_4,
                    "result_5": result_5
                })
                print(f"Added item to final data. Current count: {len(final_data)}")
            else:
                print("Item failed validation, skipping.")
    
    os.makedirs(os.path.dirname(final_file), exist_ok=True)
    with open(final_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    print(f"\nFinal check completed!")
    print(f"Final data: {len(final_data)} samples")
    print(f"Results saved to: {final_file}")

def main():
    parser = argparse.ArgumentParser(description="Environment data refinement and final check tool")
    parser.add_argument("--domain", type=str, required=True, 
                       help="Domain name (e.g., persuasion, recommendation, system_operation)")
    parser.add_argument("--final_check", action="store_true", 
                       help="Perform final check on refined data")
    
    args = parser.parse_args()
    
    input_file = f"dataset/{args.domain}_origin_data.json"
    refined_file = f"dataset/{args.domain}_refined_data.json"
    final_file = f"dataset/{args.domain}_final_data.json"
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}. Please ensure the file exists before running the refinement process.")
    
    if args.final_check:
        final_check(args.domain, refined_file, final_file)
    else:
        refine_environment_pipeline(args.domain, input_file, refined_file)
        
        response = input("\nDo you want to perform final check? (y/n): ")
        if response.lower() in ['y', 'yes']:
            final_check(args.domain, refined_file, final_file)

if __name__ == "__main__":
    main()


# example:
# python data_refinement.py --domain system_operation