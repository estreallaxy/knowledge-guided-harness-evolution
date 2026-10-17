import argparse
import concurrent.futures
import json
import os
import time
from collections import Counter
from pathlib import Path

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm


ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "dialogue_filter.txt"


def load_jsonl(path: Path):
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def render_sub_questions(sub_questions) -> str:
    chunks = []
    for sub_question in sub_questions:
        chunks.append(
            "\n".join(
                [
                    f"Sub Question {sub_question.get('question_number', '')}:",
                    f"\tQuestion: {sub_question.get('question', '')}",
                    f"\tExpected Answer: {sub_question.get('expected_answer', '')}",
                ]
            )
        )
    return "\n".join(chunks).strip()


def strip_teacher_think(content: str) -> str:
    if "</think>" in content:
        return content.split("</think>", 1)[1].strip()
    return content


def format_messages(messages, conversation_type):
    formatted = []
    conversation_type_index = 0
    i = 0
    while i < len(messages):
        student_msg = messages[i] if messages[i].get("role") == "user" else None
        if student_msg:
            student_content = student_msg.get("content", "")
            teacher_content = ""
            if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
                teacher_content = strip_teacher_think(messages[i + 1].get("content", ""))
                i += 1

            current_type = conversation_type[conversation_type_index] if conversation_type_index < len(conversation_type) else -1
            if current_type == -1:
                current_type = "Original Question"
            elif current_type == 0:
                current_type = "Correct Answer"
            elif current_type == 1:
                current_type = "Wrong Answer"
            elif current_type == 2:
                current_type = "Asking Question"
            elif current_type == 3:
                current_type = "Showing Understanding"
            elif current_type == 4:
                current_type = "Showing Confusion"
            else:
                current_type = "Irrelevant Reply"

            formatted.append(
                f"Round {conversation_type_index + 1} (Student Response Type: {current_type}):\n"
                f"  Student: {student_content}\n"
                f"  Teacher: {teacher_content}"
            )
        i += 1
        conversation_type_index += 1
    return "\n\n".join(formatted)


class DialogueFilter:
    def __init__(self, model: str, max_workers: int, temperature: float, max_tokens: int, base_url: str = "", api_key: str = ""):
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

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(3))
    def call_model(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
        )
        return response.choices[0].message.content.strip()

    def filter_one(self, dialogue_data: dict):
        answer = dialogue_data.get("answer") or dialogue_data.get("original_answer") or ""
        messages = dialogue_data.get("messages", [])
        if not messages:
            record = dict(dialogue_data)
            record["judge"] = "no"
            record["filter_pass"] = False
            record["filter_reason"] = "missing_messages"
            return record

        question = messages[0].get("content", "")
        conversation_type = dialogue_data.get("conversation_type", []) or dialogue_data.get("conversation_type_sequence", [])
        sub_questions_text = render_sub_questions(dialogue_data.get("sub_questions", []))
        formatted_messages = format_messages(messages, conversation_type)

        prompt = self.template.format(
            question=question,
            answer=answer,
            sub_questions_text=sub_questions_text,
            formatted_messages=formatted_messages,
        )
        raw_judge = self.call_model(prompt)
        decision = "DROP"
        reason = ""
        for line in raw_judge.splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("DECISION:"):
                decision = stripped.split(":", 1)[1].strip().upper()
            elif stripped.upper().startswith("REASON:"):
                reason = stripped.split(":", 1)[1].strip()
        if decision not in {"KEEP", "DROP"}:
            decision = "KEEP" if "KEEP" in raw_judge.upper() else "DROP"
        if not reason:
            reason = "OK" if decision == "KEEP" else "judge_rejected"

        record = dict(dialogue_data)
        record["judge"] = decision
        record["filter_pass"] = decision == "KEEP"
        record["filter_reason"] = reason
        return record

    def run(self, records):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_record = {executor.submit(self.filter_one, record): record for record in records}
            for future in tqdm(
                concurrent.futures.as_completed(future_to_record),
                total=len(records),
                desc="filter dialogues",
            ):
                results.append(future.result())
                time.sleep(0.05)
        return results


def summarize(records):
    counter = Counter()
    for record in records:
        counter[record.get("filter_reason", "")] += 1
    return {
        "total": len(records),
        "pass": sum(1 for record in records if record.get("filter_pass")),
        "fail": sum(1 for record in records if not record.get("filter_pass")),
        "reason_distribution": dict(counter),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Filter simulated tutor dialogues.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-workers", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--api-base-url", default=os.getenv("OPENAI_BASE_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    return parser.parse_args()


def main():
    args = parse_args()
    records = load_jsonl(Path(args.input))
    dialogue_filter = DialogueFilter(
        model=args.model,
        max_workers=args.max_workers,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    results = dialogue_filter.run(records)
    write_jsonl(Path(args.output), results)
    print(json.dumps(summarize(results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
