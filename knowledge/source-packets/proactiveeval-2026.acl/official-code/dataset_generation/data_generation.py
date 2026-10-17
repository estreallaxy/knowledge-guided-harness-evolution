import json
import argparse
import os
import random
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tools import get_model_response, clean_json_response
import httpx
from prompt.data_generation_prompt import (
    environment_generation_prompt,
    target_generation_prompt,
    target_ensemble_prompt,
    Domain_Specific_Contents
)

# Configuration
exec(open("config.yaml").read())

def load_icl_shots_by_domain(domain):
    examples_file = "examples/environment_generation_examples.json"
    with open(examples_file, 'r', encoding='utf-8') as f:
        all_examples = json.load(f)
    
    domain_examples = []
    for example in all_examples:
        if example.get("domain") == domain:
            domain_examples.append(example["environment"])
    
    return domain_examples

def load_topics_from_file(topic_file, num_topics=None):
    topics = []
    with open(topic_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            # If num_topics is specified, stop after reaching that limit
            if num_topics is not None and i >= num_topics:
                break
            line = line.strip()
            if line:
                try:
                    topic_data = json.loads(line)
                    topics.append(topic_data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {i+1}: {e}")
                    continue
    return topics

def generate_environment(client, environment_examples, topic, domain):
    prompt = environment_generation_prompt.format(
        domain,
        description=Domain_Specific_Contents[domain],
        Examples=environment_examples
    )
    
    while True:
        messages = [{"role": "system", "content": prompt}]
        model = "openai/gpt-4o-2024-11-20"
        content = get_model_response(
            client, 
            model_name=model, 
            messages=messages, 
            temperature=0.7
        )
        
        try:
            content = clean_json_response(content)
            result = {}
            print(content)
            result["environment"] = content
            result["topic"] = str(topic)
            return result
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Retrying environment generation...")
            continue

def generate_target(client, environment, domain_examples, domain):
    prompt = target_generation_prompt.format(
        description=Domain_Specific_Contents[domain],
        environment=environment, 
        example=domain_examples
    )
    
    messages = [{"role": "system", "content": prompt}]
    response = get_model_response(
        client, 
        model_name="openai/gpt-4o-2024-11-20", 
        messages=messages, 
        temperature=1.2 # high temperature sampling
    )
    return response

def generate_target_with_retry(client, environment, domain_examples, domain):
    attempts = 3
    for _ in range(attempts):
        try:
            target = generate_target(client, environment, domain_examples, domain)
            result = clean_json_response(target)
            return result
        except json.JSONDecodeError as e:
            print(f"Target parsing error: {e}")
            print("Retrying target generation...")
            continue
    return None

def generate_n_targets_parallel(client, environment, domain_examples, domain, n):
    targets = []
    with ThreadPoolExecutor(max_workers=n) as executor:
        futures = [executor.submit(generate_target_with_retry, client, environment, domain_examples, domain) for _ in range(n)]
        for future in futures:
            result = future.result()
            if result:
                targets.append(result)
    return targets

def target_ensemble(client, environment, domain_examples, domain, n):
    # high temperature sampling n targets in parallel
    targets = generate_n_targets_parallel(client, environment, domain_examples, domain, n)
    print(f"Generated {len(targets)} targets")
    
    # target ensemble
    prompt = target_ensemble_prompt.format(
        description=Domain_Specific_Contents[domain],
        environment=environment, 
        targets=targets
    )
    ensemble_messages = [{"role": "system", "content": prompt}]
    
    while True:
        try:
            ensemble_response = get_model_response(
                client, 
                model_name="openai/gpt-4o-2024-11-20", 
                messages=ensemble_messages, 
                temperature=0.7
            )
            ensemble_response = clean_json_response(ensemble_response)
            break
        except json.JSONDecodeError as e:
            print(f"Ensemble response parsing error: {e}")
            print("Retrying ensemble generation...")
            continue
    return targets, ensemble_response

def data_synthesis(domain, num_topics, ensemble_count, output_file):
    client = OpenAI(
        api_key=os.environ.get("GENERATION_API_KEY"),
        base_url=os.environ.get("GENERATION_BASE_URL"),
        http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
    )
    # load domain icl shots
    domain_examples = load_icl_shots_by_domain(domain)
    if not domain_examples:
        raise ValueError(f"No examples found for domain: {domain}")
    
    # load topic tree
    topic_file = f"topic_tree/{domain}_topic.jsonl"
    if not os.path.exists(topic_file):
        raise FileNotFoundError(f"Topic file not found: {topic_file}")
    
    topics = load_topics_from_file(topic_file, num_topics)
    if not topics:
        raise ValueError(f"No topics loaded from {topic_file}")
    
    results = []
    for topic in tqdm(topics, desc=f"Processing {domain} topics"):
        # 1. environment generation
        print(f"\nGenerating environment for topic: {topic}")
        environment_data = generate_environment(client, domain_examples, topic, domain)
        environment = environment_data["environment"]
        
        # 2. target generation and target ensemble
        print(f"Generating target for environment")
        targets, ensemble_response = target_ensemble(client, environment, domain_examples, domain, ensemble_count)
        
        best_target = ensemble_response.get("Target", "")
        sub_target = ensemble_response.get("sub_target", [])
        reason = ensemble_response.get("analyze_process", "")
        
        result = {
            "environment": environment,
            "best_target": {
                "target": best_target,
                "sub_target": sub_target
            },
            "topic": environment_data["topic"],
            "targets": targets,
            "reason": reason
        }
        
        results.append(result)
        print(f"Completed topic: {topic}")
    
    # save results
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"\nData generation completed! Generated {len(results)} samples")
    print(f"Results saved to: {output_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Data generation tool")
    parser.add_argument("--domain", type=str, required=True, 
                       help="Domain name (e.g., ambigious_instruction, persuasion)")
    parser.add_argument("--num_topics", type=int, default=None, 
                       help="Number of topics to process")
    parser.add_argument("--ensemble_count", type=int, default=5, 
                       help="Number of targets for ensemble")
    parser.add_argument("--output", type=str, 
                       help="Output file path (default: dataset/{domain}_origin_data.json)")
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if not args.output:
        args.output = f"dataset/{args.domain}_origin_data.json"
    

    topic_file = f"topic_tree/{args.domain}_topic.jsonl"
    examples_file = "examples/environment_generation_examples.json"

    # check topic_tree has topic file
    topic_file_exists = os.path.exists(topic_file)

    # check examples/environment_generation_examples.json has domain content
    examples_has_domain = False
    if os.path.exists(examples_file):
        with open(examples_file, "r", encoding="utf-8") as f:
            try:
                examples_data = json.load(f)
                # check examples_data has any example's domain field equals args.domain
                examples_has_domain = any(example.get("domain") == args.domain for example in examples_data)
            except Exception:
                examples_has_domain = False

    if not topic_file_exists or not examples_has_domain:
        raise ValueError(
            f"can not find {topic_file} file, or {examples_file} has no {args.domain} content, please check the data completeness."
        )
    
    # Execute data generation pipeline
    data_synthesis(
        args.domain,
        args.num_topics,
        args.ensemble_count,
        args.output
    )

if __name__ == "__main__":
    main()

# example:
# python data_generation.py --domain system_operation --num_topics 5 --ensemble_count 5 --output dataset/system_operation_origin_data.json