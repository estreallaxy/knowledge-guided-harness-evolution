import argparse
import json
from pathlib import Path

from grader import _normalize_latex, math_equal


def is_contiguous_numbering(sub_questions):
    numbers = [item.get("question_number") for item in sub_questions]
    return numbers == list(range(1, len(numbers) + 1))


def filter_one(record: dict, min_steps: int, max_steps: int):
    reasons = []
    sub_questions = record.get("sub_questions", [])
    final_answer = record.get("final_answer", "")
    solution_steps = record.get("solution_steps", "")

    if record.get("parse_error"):
        reasons.append(f"parse_error:{record['parse_error']}")
    if not solution_steps.strip():
        reasons.append("missing_solution_steps")
    if not sub_questions:
        reasons.append("missing_sub_questions")
    if sub_questions and not (min_steps <= len(sub_questions) <= max_steps):
        reasons.append(f"step_count_not_in_range:{len(sub_questions)}")
    if sub_questions and not is_contiguous_numbering(sub_questions):
        reasons.append("non_contiguous_question_numbering")
    for item in sub_questions:
        if not item.get("question", "").strip():
            reasons.append("empty_sub_question")
            break
        if not item.get("expected_answer", "").strip():
            reasons.append("empty_expected_answer")
            break
    if not final_answer.strip():
        reasons.append("missing_final_answer")

    normalized_gt = _normalize_latex(record.get("original_answer", ""))
    normalized_pred = _normalize_latex(final_answer)
    if normalized_gt and normalized_pred:
        if not math_equal(normalized_gt, normalized_pred):
            reasons.append("final_answer_mismatch")
    else:
        reasons.append("missing_answer_for_check")

    passed = not reasons
    record["rule_pass"] = passed
    record["rule_filter_reason"] = "OK" if passed else "; ".join(reasons)
    return record


def parse_args():
    parser = argparse.ArgumentParser(description="Rule-based filtering for generated plans.")
    parser.add_argument("--input", required=True, help="Input jsonl path.")
    parser.add_argument("--output", required=True, help="Output jsonl path.")
    parser.add_argument("--min-steps", type=int, default=2)
    parser.add_argument("--max-steps", type=int, default=7)
    parser.add_argument("--pass-only", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as infile, output_path.open("w", encoding="utf-8") as outfile:
        for line in infile:
            if not line.strip():
                continue
            record = json.loads(line)
            filtered = filter_one(record, min_steps=args.min_steps, max_steps=args.max_steps)
            if args.pass_only and not filtered["rule_pass"]:
                continue
            outfile.write(json.dumps(filtered, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
