"""
Test PromptGuard on single-turn benign AgentHarm logs.

For each sample: runs PromptGuard on the user prompt.
Creates new JSON files with defense results, resets scores for flagged samples,
and prints a summary table of old vs new AgentHarm scores per model/language.
"""

import json
import os
from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from tqdm import tqdm
from transformers import pipeline

if not os.environ.get("HF_TOKEN"):
    raise RuntimeError("HF_TOKEN must be set in the environment to download Llama-Prompt-Guard-2-86M.")

DEFAULT_LANGUAGES = ["English", "Chinese", "French", "Hindi", "Telugu", "Ukrainian", "Urdu"]
DEFAULT_SEEDS = [0, 1, 2]
DEFAULT_MODELS = ["GPT-5.1", "Gemini3-Flash"]
BATCH_SIZE = 16


def extract_prompt(sample):
    """Extract the user prompt from a sample's messages."""
    for msg in sample.get("messages", []):
        role = msg.get("role", "")
        content = msg.get("content", "")
        if isinstance(content, str) and len(content.strip()) > 0 and role == "user":
            return content.strip()
    return None


def process_file(promptguard, input_path, output_path):
    """Process a single log file: run PromptGuard on each sample's prompt."""
    with open(input_path, "r") as f:
        data = json.load(f)

    data_out = deepcopy(data)
    samples = data["samples"]

    # Collect all prompts for batched inference
    prompts = []
    prompt_indices = []  # indices into samples that have a prompt
    for i, sample in enumerate(samples):
        prompt = extract_prompt(sample)
        if prompt:
            prompts.append(prompt)
            prompt_indices.append(i)

    # Run PromptGuard in batches
    pg_results = []
    for out in tqdm(promptguard(prompts, batch_size=BATCH_SIZE),
                    total=len(prompts),
                    desc=f"  {input_path.name}",
                    leave=False):
        pg_results.append(out)

    # Map results back; build a lookup from sample index -> pg result
    pg_lookup = {}
    for idx, result in zip(prompt_indices, pg_results):
        pg_lookup[idx] = result

    old_scores = []
    new_scores = []

    for i, sample in enumerate(samples):
        score_val = sample["scores"]["combined_scorer"]["value"]
        original_score = score_val["score"]

        if i in pg_lookup:
            result = pg_lookup[i]
            assert result['label'] in ['LABEL_0', 'LABEL_1']
            detected = result['label'] == 'LABEL_1'
            score_raw = result['score']
        else:
            detected = False
            score_raw = 0.0

        data_out["samples"][i]["defense_results"] = {
            "promptguard": {
                "detected_malicious": detected,
                "score": score_raw,
            },
        }

        new_score = 0.0 if detected else original_score
        data_out["samples"][i]["scores"]["combined_scorer"]["value"]["score_after_promptguard"] = new_score

        old_scores.append(original_score)
        new_scores.append(new_score)

    with open(output_path, "w") as f:
        json.dump(data_out, f, indent=2)

    avg_old = sum(old_scores) / len(old_scores) if old_scores else 0.0
    avg_new = sum(new_scores) / len(new_scores) if new_scores else 0.0
    return avg_old, avg_new


def main(models, log_dir: Path, output_dir: Path, languages, seeds):
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading PromptGuard model...")
    promptguard = pipeline("text-classification", model="meta-llama/Llama-Prompt-Guard-2-86M", device=0, batch_size=BATCH_SIZE)

    # {model: {language: {seed: (old_avg, new_avg)}}}
    results = defaultdict(lambda: defaultdict(dict))

    for model in models:
        print(f"\n{'='*85}")
        print(f"Processing model: {model}")
        print(f"{'='*85}")

        for lang in languages:
            for seed in seeds:
                filename = f"{model}_benign_{lang}_{seed}.json"
                input_path = log_dir / filename
                if not input_path.exists():
                    print(f"WARNING: {input_path} not found, skipping.")
                    continue

                output_filename = f"{model}_benign_{lang}_{seed}_promptguard.json"
                output_path = output_dir / output_filename

                print(f"Processing {filename} ...")
                avg_old, avg_new = process_file(promptguard, input_path, output_path)
                results[model][lang][seed] = (avg_old, avg_new)
                print(f"  Old avg score: {avg_old:.4f}, New avg score: {avg_new:.4f}")
                print(f"  Saved to {output_path}")

    for model in models:
        print(f"\n{'='*85}")
        print(f"  {model} BENIGN — AgentHarm Scores (averaged across {len(seeds)} seeds)")
        print(f"{'='*85}")
        print(f"{'Language':<15} {'Old Score':>12} {'New Score':>12} {'Abs Decline':>14} {'Rel Decline %':>15}")
        print("-" * 85)

        for lang in languages:
            if lang not in results[model]:
                continue
            seed_old, seed_new = [], []
            for seed in seeds:
                if seed in results[model][lang]:
                    old, new = results[model][lang][seed]
                    seed_old.append(old)
                    seed_new.append(new)

            if not seed_old:
                continue

            avg_old = sum(seed_old) / len(seed_old)
            avg_new = sum(seed_new) / len(seed_new)
            abs_decline = avg_old - avg_new
            rel_decline = (abs_decline / avg_old * 100) if avg_old > 0 else 0.0
            print(f"{lang:<15} {avg_old:>12.4f} {avg_new:>12.4f} {abs_decline:>14.4f} {rel_decline:>14.2f}%")

        print("=" * 85)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run PromptGuard on single-turn AgentHarm logs.")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="Model name prefixes in filenames.")
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path(__file__).parent / "single_turn_agentharm_logs",
        help="Directory of single-turn AgentHarm log JSONs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Where to write per-file PromptGuard JSONs (default: <log-dir>/promptguard_results).",
    )
    parser.add_argument("--languages", nargs="+", default=DEFAULT_LANGUAGES, help="Languages to process.")
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS, help="Seeds to process.")
    args = parser.parse_args()
    out = args.output_dir or args.log_dir / "promptguard_results"
    main(args.models, args.log_dir, out, args.languages, args.seeds)
