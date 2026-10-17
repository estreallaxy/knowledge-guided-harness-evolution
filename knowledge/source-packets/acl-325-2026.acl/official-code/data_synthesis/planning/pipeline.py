import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

from format_training_data import format_records, write_jsonl as write_training_jsonl
from generate_plan import PlanGenerator, load_questions
from model_filter import ModelFilter
from rule_filter import filter_one


ROOT = Path(__file__).resolve().parent

# You can edit these defaults directly if you prefer file-level configuration.
DEFAULT_CONFIG = {
    "dataset": "bigmath",
    "input": "",
    "output_dir": str(ROOT / "runs" / "bigmath"),
    "plan_examples": "",
    "verifier_examples": "",
    "solve_model": "gpt-4o-mini",
    "plan_model": "gpt-4o-mini",
    "verifier_model": "gpt-4o-mini",
    "max_workers": 16,
    "solve_temperature": 0.6,
    "plan_temperature": 0.6,
    "verifier_temperature": 0.0,
    "solve_max_tokens": 8192,
    "plan_max_tokens": 8192,
    "verifier_max_tokens": 1024,
}


def resolve_default_input(dataset: str) -> str:
    if dataset != "bigmath":
        return ""

    candidates = [
        os.getenv("BIGMATH_INPUT_PATH", ""),
        str(ROOT / "data" / "bigmath.jsonl"),
        str(Path.cwd() / "bigmath.jsonl"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return ""


def load_optional_text(path_str: str) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Examples file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def attach_examples(base_prompt: str, examples_text: str) -> str:
    if not examples_text:
        return base_prompt
    return f"{base_prompt}\n\n{examples_text.strip()}\n"


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def load_jsonl(path: Path):
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def summarize_reasons(records, field_name: str) -> dict:
    counter = Counter()
    for record in records:
        reason = record.get(field_name, "")
        counter[reason or ""] += 1
    return dict(counter)


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_report(generated, rule_filtered, model_filtered, formatted_records, format_stats, paths, timings):
    rule_pass_records = [r for r in rule_filtered if r.get("rule_pass", False)]
    model_pass_records = [r for r in model_filtered if r.get("model_pass", False)]
    report = {
        "paths": {k: str(v) for k, v in paths.items()},
        "timings_seconds": timings,
        "counts": {
            "generated_total": len(generated),
            "rule_pass": len(rule_pass_records),
            "rule_fail": len(rule_filtered) - len(rule_pass_records),
            "model_checked": len(model_filtered),
            "model_pass": len(model_pass_records),
            "model_fail": len(model_filtered) - len(model_pass_records),
            "formatted_total": len(formatted_records),
        },
        "rule_filter_reason_distribution": summarize_reasons(rule_filtered, "rule_filter_reason"),
        "model_filter_reason_distribution": summarize_reasons(model_filtered, "model_filter_reason"),
        "format_reason_distribution": format_stats,
    }
    return report


def print_report(report: dict):
    counts = report["counts"]
    print("\n=== Plan Stage Summary ===")
    print(f"Generated total: {counts['generated_total']}")
    print(f"Rule pass: {counts['rule_pass']}")
    print(f"Rule fail: {counts['rule_fail']}")
    print(f"Model checked: {counts['model_checked']}")
    print(f"Model pass: {counts['model_pass']}")
    print(f"Model fail: {counts['model_fail']}")
    print("\nRule filter reasons:")
    for reason, count in sorted(report["rule_filter_reason_distribution"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {reason}: {count}")
    print("\nModel filter reasons:")
    for reason, count in sorted(report["model_filter_reason_distribution"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {reason}: {count}")
    print("\nFormat reasons:")
    for reason, count in sorted(report["format_reason_distribution"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {reason}: {count}")
    print("\nOutputs:")
    for key, value in report["paths"].items():
        print(f"  {key}: {value}")


def parse_args():
    parser = argparse.ArgumentParser(description="End-to-end plan-stage synthesis pipeline.")
    parser.add_argument("--dataset", default=DEFAULT_CONFIG["dataset"], help="Dataset name. Default: bigmath")
    parser.add_argument("--input", default=DEFAULT_CONFIG["input"], help="Input question dataset jsonl.")
    parser.add_argument("--output-dir", default=DEFAULT_CONFIG["output_dir"], help="Output directory.")
    parser.add_argument("--plan-examples", default=DEFAULT_CONFIG["plan_examples"], help="Optional txt for planning few-shot examples.")
    parser.add_argument(
        "--verifier-examples",
        default=DEFAULT_CONFIG["verifier_examples"],
        help="Optional txt for verifier few-shot examples.",
    )
    parser.add_argument("--api-base-url", default=os.getenv("OPENAI_BASE_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--solve-model", default=DEFAULT_CONFIG["solve_model"])
    parser.add_argument("--plan-model", default=DEFAULT_CONFIG["plan_model"])
    parser.add_argument("--verifier-model", default=DEFAULT_CONFIG["verifier_model"])
    parser.add_argument("--max-workers", type=int, default=DEFAULT_CONFIG["max_workers"])
    parser.add_argument("--solve-temperature", type=float, default=DEFAULT_CONFIG["solve_temperature"])
    parser.add_argument("--plan-temperature", type=float, default=DEFAULT_CONFIG["plan_temperature"])
    parser.add_argument("--verifier-temperature", type=float, default=DEFAULT_CONFIG["verifier_temperature"])
    parser.add_argument("--solve-max-tokens", type=int, default=DEFAULT_CONFIG["solve_max_tokens"])
    parser.add_argument("--plan-max-tokens", type=int, default=DEFAULT_CONFIG["plan_max_tokens"])
    parser.add_argument("--verifier-max-tokens", type=int, default=DEFAULT_CONFIG["verifier_max_tokens"])
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on number of questions.")
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = args.input or resolve_default_input(args.dataset)
    if not input_path:
        raise ValueError(f"No default input found for dataset={args.dataset}. Please provide --input.")
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "generated": output_dir / "01_generated_plans.jsonl",
        "rule_filtered": output_dir / "02_rule_filtered_plans.jsonl",
        "model_filtered": output_dir / "03_model_filtered_plans.jsonl",
        "formatted_training_data": output_dir / "04_formatted_training_data.jsonl",
        "report": output_dir / "report.json",
    }

    questions = load_questions(input_path)
    if args.limit and args.limit > 0:
        questions = questions[: args.limit]

    plan_examples = load_optional_text(args.plan_examples)
    verifier_examples = load_optional_text(args.verifier_examples)

    timings = {}

    t0 = time.time()
    generator = PlanGenerator(
        solve_model=args.solve_model,
        plan_model=args.plan_model,
        max_workers=args.max_workers,
        solve_temperature=args.solve_temperature,
        plan_temperature=args.plan_temperature,
        solve_max_tokens=args.solve_max_tokens,
        plan_max_tokens=args.plan_max_tokens,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    generator.template = attach_examples(generator.template, plan_examples)
    if paths["generated"].exists():
        paths["generated"].unlink()
    generator.generate_batch(questions, paths["generated"])
    timings["generate_plan"] = round(time.time() - t0, 2)

    t1 = time.time()
    generated_records = load_jsonl(paths["generated"])
    rule_filtered_records = [filter_one(record, min_steps=2, max_steps=7) for record in generated_records]
    write_jsonl(paths["rule_filtered"], rule_filtered_records)
    timings["rule_filter"] = round(time.time() - t1, 2)

    t2 = time.time()
    verifier = ModelFilter(
        model=args.verifier_model,
        max_workers=args.max_workers,
        temperature=args.verifier_temperature,
        max_tokens=args.verifier_max_tokens,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    verifier.template = attach_examples(verifier.template, verifier_examples)
    model_input_records = [record for record in rule_filtered_records if record.get("rule_pass", False)]
    verifier.verify_batch(model_input_records, paths["model_filtered"])
    timings["model_filter"] = round(time.time() - t2, 2)

    t3 = time.time()
    model_filtered_records = load_jsonl(paths["model_filtered"])
    formatted_records, format_stats = format_records(model_filtered_records, max_content_length=5000)
    write_training_jsonl(paths["formatted_training_data"], formatted_records)
    timings["format_training_data"] = round(time.time() - t3, 2)
    report = build_report(
        generated=generated_records,
        rule_filtered=rule_filtered_records,
        model_filtered=model_filtered_records,
        formatted_records=formatted_records,
        format_stats=format_stats,
        paths=paths,
        timings=timings,
    )
    paths["report"].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print_report(report)


if __name__ == "__main__":
    main()
