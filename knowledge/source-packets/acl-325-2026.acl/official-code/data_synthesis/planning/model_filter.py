import argparse
import concurrent.futures
import json
import os
import re
import time
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "plan_filter.txt"


def format_candidate_plan(record: dict) -> str:
    lines = ["### Sub-Questions"]
    for item in record.get("sub_questions", []):
        lines.append(f"{item.get('question_number', '')}. Sub-Question: <<<{item.get('question', '').strip()}>>>")
        lines.append(f"   Expected Answer: <<<{item.get('expected_answer', '').strip()}>>>")
    lines.append("")
    lines.append("### Final Answer")
    lines.append(f"<<<{record.get('final_answer', '').strip()}>>>")
    return "\n".join(lines).strip()


def parse_verifier_response(text: str):
    decision_match = re.search(r"DECISION:\s*(ACCEPT|REJECT)", text, re.IGNORECASE)
    reason_match = re.search(r"REASON:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
    decision = decision_match.group(1).upper() if decision_match else "REJECT"
    reason = reason_match.group(1).strip() if reason_match else "Unparseable verifier output."
    return decision, reason


class ModelFilter:
    def __init__(
        self,
        model: str,
        max_workers: int,
        temperature: float,
        max_tokens: int,
        base_url: str = "",
        api_key: str = "",
    ):
        base_url = base_url or os.getenv("OPENAI_BASE_URL") or ""
        api_key = api_key or os.getenv("OPENAI_API_KEY") or ""
        if not api_key:
            raise ValueError("Missing API key. Set OPENAI_API_KEY or pass --api-key.")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.max_workers = max_workers
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.template = PROMPT_PATH.read_text(encoding="utf-8")

    def build_prompt(self, record: dict) -> str:
        return self.template.format(
            problem=record.get("original_problem", ""),
            reference_answer=record.get("original_answer", ""),
            solution_steps=record.get("solution_steps", ""),
            candidate_plan=format_candidate_plan(record),
        )

    def call_model(self, prompt: str) -> str:
        last_error = None
        for attempt in range(3):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=False,
                )
                return completion.choices[0].message.content.strip()
            except Exception as exc:
                last_error = str(exc)
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(last_error or "Unknown API error")

    def verify_one(self, record: dict):
        try:
            raw_response = self.call_model(self.build_prompt(record))
            decision, reason = parse_verifier_response(raw_response)
            record["model_pass"] = decision == "ACCEPT"
            record["model_filter_reason"] = reason
            record["model_filter_raw_response"] = raw_response
            return record
        except Exception as exc:
            record["model_pass"] = False
            record["model_filter_reason"] = str(exc)
            record["model_filter_raw_response"] = ""
            return record

    def verify_batch(self, records, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as out, concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [executor.submit(self.verify_one, record) for record in records]
            for future in concurrent.futures.as_completed(futures):
                out.write(json.dumps(future.result(), ensure_ascii=False) + "\n")


def load_records(input_path: Path, rule_pass_only: bool):
    records = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if rule_pass_only and not record.get("rule_pass", False):
                continue
            records.append(record)
    return records


def parse_args():
    parser = argparse.ArgumentParser(description="Model-based coherence filter for generated plans.")
    parser.add_argument("--input", required=True, help="Input jsonl path.")
    parser.add_argument("--output", required=True, help="Output jsonl path.")
    parser.add_argument("--api-base-url", default=os.getenv("OPENAI_BASE_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--model", default=os.getenv("PLAN_FILTER_MODEL", "gpt-4o-mini"))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--max-workers", type=int, default=16)
    parser.add_argument("--process-all", action="store_true", help="Do not restrict to rule_pass=true samples.")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    records = load_records(input_path, rule_pass_only=not args.process_all)
    verifier = ModelFilter(
        model=args.model,
        max_workers=args.max_workers,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    verifier.verify_batch(records, output_path)


if __name__ == "__main__":
    main()
