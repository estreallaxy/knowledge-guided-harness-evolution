import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

from dialogue_filter import DialogueFilter
from format_training_data import format_single_conversation
from generate_dialogues import DialogueSimulator, load_jsonl, load_questions


ROOT = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "dataset": "bigmath",
    "input": "",
    "output_dir": str(ROOT / "runs" / "bigmath"),
    "num_turns": 14,
    "generation_workers": 64,
    "filter_workers": 32,
    "user_model": "gpt-4o-mini",
    "assistant_model": "gpt-4o-mini",
    "filter_model": "gpt-4o-mini",
    "user_temperature": 1.0,
    "assistant_temperature": 0.3,
    "filter_temperature": 0.0,
    "filter_max_tokens": 256,
    "seed": 42,
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


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def summarize_generation(records):
    error_counter = Counter()
    for record in records:
        if record.get("error_reason"):
            error_counter[record["error_reason"]] += 1
    return {
        "generated_total": len(records),
        "finished": sum(1 for record in records if record.get("is_finished") == 1),
        "unfinished": sum(1 for record in records if record.get("is_finished") != 1),
        "with_messages": sum(1 for record in records if record.get("messages")),
        "error_distribution": dict(error_counter),
    }


def summarize_filter(records):
    reason_counter = Counter(record.get("filter_reason", "") for record in records)
    return {
        "checked": len(records),
        "keep": sum(1 for record in records if record.get("filter_pass")),
        "drop": sum(1 for record in records if not record.get("filter_pass")),
        "reason_distribution": dict(reason_counter),
    }


def build_report(paths: dict, generation_summary: dict, filter_summary: dict, formatted_count: int, timings: dict):
    return {
        "paths": {key: str(value) for key, value in paths.items()},
        "timings_seconds": timings,
        "generation": generation_summary,
        "filter": filter_summary,
        "formatted_samples": formatted_count,
    }


def print_report(report: dict):
    print("\n=== Tutor Stage Summary ===")
    print(f"Generated total: {report['generation']['generated_total']}")
    print(f"Finished dialogues: {report['generation']['finished']}")
    print(f"Unfinished dialogues: {report['generation']['unfinished']}")
    print(f"Filter keep: {report['filter']['keep']}")
    print(f"Filter drop: {report['filter']['drop']}")
    print(f"Formatted samples: {report['formatted_samples']}")
    print("\nGeneration errors:")
    for reason, count in sorted(report["generation"]["error_distribution"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {reason}: {count}")
    print("\nFilter reasons:")
    for reason, count in sorted(report["filter"]["reason_distribution"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {reason}: {count}")
    print("\nOutputs:")
    for key, value in report["paths"].items():
        print(f"  {key}: {value}")


def parse_args():
    parser = argparse.ArgumentParser(description="End-to-end tutor-stage synthesis pipeline.")
    parser.add_argument("--dataset", default=DEFAULT_CONFIG["dataset"])
    parser.add_argument("--input", default=DEFAULT_CONFIG["input"])
    parser.add_argument("--output-dir", default=DEFAULT_CONFIG["output_dir"])
    parser.add_argument("--num-turns", type=int, default=DEFAULT_CONFIG["num_turns"])
    parser.add_argument("--generation-workers", type=int, default=DEFAULT_CONFIG["generation_workers"])
    parser.add_argument("--filter-workers", type=int, default=DEFAULT_CONFIG["filter_workers"])
    parser.add_argument("--user-model", default=DEFAULT_CONFIG["user_model"])
    parser.add_argument("--assistant-model", default=DEFAULT_CONFIG["assistant_model"])
    parser.add_argument("--filter-model", default=DEFAULT_CONFIG["filter_model"])
    parser.add_argument("--user-temperature", type=float, default=DEFAULT_CONFIG["user_temperature"])
    parser.add_argument("--assistant-temperature", type=float, default=DEFAULT_CONFIG["assistant_temperature"])
    parser.add_argument("--filter-temperature", type=float, default=DEFAULT_CONFIG["filter_temperature"])
    parser.add_argument("--filter-max-tokens", type=int, default=DEFAULT_CONFIG["filter_max_tokens"])
    parser.add_argument("--api-base-url", default=os.getenv("OPENAI_BASE_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--seed", type=int, default=DEFAULT_CONFIG["seed"])
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
        "generated": output_dir / "01_generated_dialogues.jsonl",
        "filtered": output_dir / "02_filtered_dialogues.jsonl",
        "kept": output_dir / "03_kept_dialogues.jsonl",
        "formatted": output_dir / "04_formatted_training_data.jsonl",
        "report": output_dir / "report.json",
    }

    for path in paths.values():
        if path.exists():
            path.unlink()

    questions = load_questions(input_path)
    if args.limit > 0:
        questions = questions[: args.limit]

    timings = {}

    t0 = time.time()
    simulator = DialogueSimulator(
        output_file=paths["generated"],
        max_workers=args.generation_workers,
        user_model=args.user_model,
        assistant_model=args.assistant_model,
        user_temperature=args.user_temperature,
        assistant_temperature=args.assistant_temperature,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    simulator.run_simulations(questions, num_turns=args.num_turns)
    timings["generate_dialogues"] = round(time.time() - t0, 2)

    t1 = time.time()
    generated_records = load_jsonl(paths["generated"])
    generation_summary = summarize_generation(generated_records)
    timings["load_generated"] = round(time.time() - t1, 2)

    t2 = time.time()
    dialogue_filter = DialogueFilter(
        model=args.filter_model,
        max_workers=args.filter_workers,
        temperature=args.filter_temperature,
        max_tokens=args.filter_max_tokens,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    filtered_records = dialogue_filter.run(generated_records)
    write_jsonl(paths["filtered"], filtered_records)
    kept_records = [record for record in filtered_records if record.get("filter_pass")]
    write_jsonl(paths["kept"], kept_records)
    filter_summary = summarize_filter(filtered_records)
    timings["filter_dialogues"] = round(time.time() - t2, 2)

    t3 = time.time()
    formatted_records = []
    for record in kept_records:
        formatted_records.extend(format_single_conversation(record))
    write_jsonl(paths["formatted"], formatted_records)
    timings["format_training_data"] = round(time.time() - t3, 2)

    report = build_report(
        paths=paths,
        generation_summary=generation_summary,
        filter_summary=filter_summary,
        formatted_count=len(formatted_records),
        timings=timings,
    )
    paths["report"].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print_report(report)


if __name__ == "__main__":
    main()
