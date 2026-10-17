"""
Evaluate optimized prompts on GSM8K (grade-school math).
Reads openai + eval settings from config/mrpea_config.yaml by default.

Usage:
  python evaluation/eval_gsm8k.py --method mrpea
  python evaluation/eval_gsm8k.py --method cot
  python evaluation/eval_gsm8k.py --method promptwizard
"""
import os
import json
import re
import argparse
import yaml
from datetime import datetime
from pathlib import Path
from openai import OpenAI

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
PROMPTS_DIR = PROJECT_DIR / 'evaluation' / 'optimized_prompts'
LOG_DIR = PROJECT_DIR / 'evaluation' / 'log'
LOG_DIR.mkdir(exist_ok=True)

METHODS = {
    "mrpea":      ("standard", PROMPTS_DIR / "mrpea.jsonl", None),
    "cot":        ("q_end",    PROMPTS_DIR / "cot.jsonl", None),
    "gpo":        ("q_end",    PROMPTS_DIR / "gpo.jsonl", None),
    "opro":       ("q_end",    PROMPTS_DIR / "opro.jsonl", None),
    "direct":     ("q_end",    PROMPTS_DIR / "direct.jsonl", None),
    "spo":        ("standard", PROMPTS_DIR / "spo.jsonl", None),
    "glape":      ("a_begin",  PROMPTS_DIR / "glape.jsonl", None),
    "promptwizard": ("both",   PROMPTS_DIR / "promptwizard" / "promptwizard-system.jsonl",
                                PROMPTS_DIR / "promptwizard" / "promptwizard-user.jsonl"),
}


def load_dataset(dataset_dir):
    path = dataset_dir / "grade-school-math-master" / "grade_school_math" / "data" / "test.jsonl"
    with open(path, 'r') as f:
        return [json.loads(line.strip()) for line in f]


def load_prompt(path, task="gsm8k"):
    with open(path, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            if data.get('dataset') == task or data.get('task') == task:
                return data['prompt']
    return None


def load_task_objective(task_file, task_name="gsm8k"):
    with open(task_file, 'r') as f:
        tasks = yaml.safe_load(f)
    task = tasks.get('tasks', {}).get(task_name, {})
    return task.get('task_objective', '')


def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def parse_expected(answer_text):
    match = re.search(r'#### (\d+)', answer_text)
    return match.group(1) if match else None


def parse_predicted(output_text):
    match = re.search(r'<answer>([0-9,.]+)</answer>', output_text)
    if match:
        return match.group(1).replace(',', '')
    numbers = re.findall(r'[0-9,.]+', output_text)
    if numbers:
        return numbers[-1].replace(',', '')
    return None


def compose_prompt(prompt_type, prompt_text, question, user_prompt_text=None, task_objective=""):
    if prompt_type == 'standard':
        return prompt_text, question
    elif prompt_type == 'q_end':
        return task_objective, question + " " + prompt_text
    elif prompt_type == 'a_begin':
        return task_objective, "Q: " + question + "\nA: " + prompt_text
    elif prompt_type == 'both':
        return prompt_text, user_prompt_text + "\n" + question
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")


def evaluate(method_name, prompt_type, prompt_path, user_prompt_path,
             model, base_url, api_key, temperature, max_tokens,
             dataset_dir, task_file=None, max_questions=None):
    client = OpenAI(base_url=base_url, api_key=api_key)
    dataset = load_dataset(dataset_dir)
    prompt_text = load_prompt(prompt_path)

    user_prompt_text = None
    if prompt_type == 'both' and user_prompt_path:
        user_prompt_text = load_prompt(user_prompt_path)

    task_objective = ""
    if prompt_type in ('q_end', 'a_begin') and task_file:
        task_objective = load_task_objective(task_file)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = LOG_DIR / f"eval_gsm8k_{method_name}_{timestamp}.txt"

    with open(log_file, 'w') as log:
        log.write(f"Task: gsm8k\nMethod: {method_name} ({prompt_type})\n")
        log.write(f"Model: {model} | Temperature: {temperature} | Max tokens: {max_tokens}\n")
        log.write(f"Prompt: {prompt_text}\n")
        log.write("-" * 50 + "\n")

    print(f"Log: {log_file}")
    print(f"Model: {model} | Temperature: {temperature} | Max tokens: {max_tokens}")
    print(f"Evaluating GSM8K | Method: {method_name} ({prompt_type})")
    print(f"Prompt file: {prompt_path}")
    print(f"System prompt: {prompt_text[:100]}...")
    print("=" * 50)

    total = len(dataset) if max_questions is None else min(max_questions, len(dataset))
    correct_count = 0

    for i, item in enumerate(dataset[:total]):
        question = item['question']

        system_prompt, user_input = compose_prompt(
            prompt_type, prompt_text, question, user_prompt_text, task_objective
        )

        response = client.responses.create(
            model=model, instructions=system_prompt, input=user_input,
            temperature=temperature, max_output_tokens=max_tokens,
        )

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        expected = parse_expected(item['answer'])
        predicted = parse_predicted(response.output_text)

        try:
            is_correct = (float(predicted) == float(expected))
        except (ValueError, TypeError):
            is_correct = False

        if is_correct:
            correct_count += 1

        acc = (correct_count / (i + 1)) * 100
        print(f"  Q{i+1}: {question[:50]}... | Expected: {expected} | Predicted: {predicted} | "
              f"{'✓' if is_correct else '✗'} | {correct_count}/{i+1} ({acc:.1f}%)")

        with open(log_file, 'a') as log:
            log.write(f"Question {i+1}: {user_input}\n")
            log.write(f"Model Output: {response.output_text}\n")
            log.write(f"Input tokens: {input_tokens}\n")
            log.write(f"Output tokens: {output_tokens}\n")
            log.write(f"Question {i+1} | Expected: {expected} | Predicted: {predicted} | "
                      f"Correct: {is_correct} | Accuracy: {correct_count}/{i+1} ({acc:.2f}%)\n")
            log.write("-" * 50 + "\n")

    accuracy = (correct_count / total) * 100
    print(f"\nAccuracy: {correct_count}/{total} ({accuracy:.2f}%)")

    with open(log_file, 'a') as log:
        log.write(f"Accuracy: {correct_count}/{total} ({accuracy:.2f}%)\n")

    return accuracy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default=str(PROJECT_DIR / 'config' / 'mrpea_config.yaml'))
    parser.add_argument('--method', required=True, choices=list(METHODS.keys()),
                        help=f'Prompt method: {", ".join(METHODS.keys())}')
    parser.add_argument('--task-file', default=str(PROJECT_DIR / 'config' / 'tasks_simple.yaml'))
    parser.add_argument('--model', default=None)
    parser.add_argument('--temperature', type=float, default=None)
    parser.add_argument('--max-tokens', type=int, default=None)
    parser.add_argument('--base-url', default=None)
    parser.add_argument('--api-key', default=None)
    parser.add_argument('--dataset-dir', default=str(PROJECT_DIR / 'evaluation' / 'dataset'))
    parser.add_argument('--max-questions', type=int, default=None)
    args = parser.parse_args()

    prompt_type, prompt_path, user_prompt_path = METHODS[args.method]
    dataset_dir = Path(args.dataset_dir)

    config = {}
    if os.path.exists(args.config):
        config = load_config(args.config)

    openai_cfg = config.get('openai', {})
    eval_cfg = config.get('eval', {})

    model = args.model or eval_cfg.get('model', 'gpt-4.1-nano')
    temperature = args.temperature if args.temperature is not None else eval_cfg.get('temperature', 0.0)
    max_tokens = args.max_tokens or eval_cfg.get('max_tokens', 2048)
    base_url = args.base_url or openai_cfg.get('base_url', 'https://api.openai.com/v1')
    api_key = args.api_key or openai_cfg.get('api_key') or os.getenv('OPENAI_API_KEY') or os.getenv('AZURE_API_KEY')

    if not api_key:
        print("Error: No API key found.")
        return

    evaluate(args.method, prompt_type, prompt_path, user_prompt_path,
             model, base_url, api_key, temperature, max_tokens,
             dataset_dir, args.task_file, args.max_questions)


if __name__ == "__main__":
    main()
