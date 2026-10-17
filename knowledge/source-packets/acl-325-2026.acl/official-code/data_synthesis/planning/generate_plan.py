import argparse
import concurrent.futures
import json
import os
import re
import time
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "plan_generation.txt"
SOLVE_PROMPT_TEMPLATE = """{problem}

Please reason step by step, and put your final answer within \\boxed{{}}."""


def load_questions(input_path: Path):
    questions = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            questions.append(
                {
                    "question_id": data.get("question_id") or data.get("id") or "",
                    "problem": data.get("problem") or data.get("question") or "",
                    "reference_answer": data.get("answer") or data.get("final_answer") or "",
                }
            )
    return questions


def parse_sub_questions(response_text: str):
    sub_questions = []
    pattern = re.compile(
        r"(\d+)\.\s*Sub-Question:\s*<<<(.*?)>>>\s*Expected\s*Answer:\s*<<<(.*?)>>>",
        re.IGNORECASE | re.DOTALL,
    )
    for number, question, expected_answer in pattern.findall(response_text):
        sub_questions.append(
            {
                "question_number": int(number),
                "question": re.sub(r"\s+", " ", question).strip(),
                "expected_answer": expected_answer.strip(),
            }
        )
    return sub_questions


def extract_final_answer(response_text: str) -> str:
    final_section_match = re.search(
        r"###\s*Final\s*Answer\s*(.*)$",
        response_text,
        re.IGNORECASE | re.DOTALL,
    )
    final_section = final_section_match.group(1).strip() if final_section_match else response_text

    boxed_matches = list(re.finditer(r"\\boxed\{", final_section))
    if boxed_matches:
        start = boxed_matches[-1].end() - 1
        depth = 1
        result = []
        for index in range(start + 1, len(final_section)):
            char = final_section[index]
            if char == "{":
                depth += 1
                result.append(char)
            elif char == "}":
                depth -= 1
                if depth == 0:
                    break
                result.append(char)
            else:
                result.append(char)
        if depth == 0:
            return "".join(result).strip()

    angle_match = re.search(r"<<<(.*?)>>>", final_section, re.DOTALL)
    if angle_match:
        return angle_match.group(1).strip()

    return final_section.strip()


class PlanGenerator:
    def __init__(
        self,
        solve_model: str,
        plan_model: str,
        max_workers: int,
        solve_temperature: float,
        plan_temperature: float,
        solve_max_tokens: int,
        plan_max_tokens: int,
        base_url: str = "",
        api_key: str = "",
    ):
        base_url = base_url or os.getenv("OPENAI_BASE_URL") or ""
        api_key = api_key or os.getenv("OPENAI_API_KEY") or ""
        if not api_key:
            raise ValueError("Missing API key. Set OPENAI_API_KEY or pass --api-key.")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.solve_model = solve_model
        self.plan_model = plan_model
        self.max_workers = max_workers
        self.solve_temperature = solve_temperature
        self.plan_temperature = plan_temperature
        self.solve_max_tokens = solve_max_tokens
        self.plan_max_tokens = plan_max_tokens
        self.template = PROMPT_PATH.read_text(encoding="utf-8")

    def build_solve_prompt(self, problem: str) -> str:
        return SOLVE_PROMPT_TEMPLATE.format(problem=problem)

    def build_plan_prompt(self, problem: str, solution_steps: str) -> str:
        return self.template.format(problem=problem, solution_steps=solution_steps)

    def call_model(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        last_error = None
        for attempt in range(3):
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                )
                return completion.choices[0].message.content.strip()
            except Exception as exc:
                last_error = str(exc)
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(last_error or "Unknown API error")

    def generate_one(self, item: dict):
        try:
            solve_prompt = self.build_solve_prompt(item["problem"])
            solution_steps = self.call_model(
                model=self.solve_model,
                prompt=solve_prompt,
                temperature=self.solve_temperature,
                max_tokens=self.solve_max_tokens,
            )
            plan_prompt = self.build_plan_prompt(item["problem"], solution_steps)
            plan_response = self.call_model(
                model=self.plan_model,
                prompt=plan_prompt,
                temperature=self.plan_temperature,
                max_tokens=self.plan_max_tokens,
            )
            sub_questions = parse_sub_questions(plan_response)
            final_answer = extract_final_answer(plan_response)
            parse_error = None
            if not solution_steps:
                parse_error = "missing_solution_steps"
            elif not sub_questions:
                parse_error = "missing_sub_questions"
            elif not final_answer:
                parse_error = "missing_final_answer"
            return {
                "question_id": item["question_id"],
                "original_problem": item["problem"],
                "original_answer": item["reference_answer"],
                "solution_steps": solution_steps,
                "sub_questions": sub_questions,
                "final_answer": final_answer,
                "solve_raw_response": solution_steps,
                "plan_raw_response": plan_response,
                "parse_error": parse_error,
            }
        except Exception as exc:
            return {
                "question_id": item["question_id"],
                "original_problem": item["problem"],
                "original_answer": item["reference_answer"],
                "solution_steps": "",
                "sub_questions": [],
                "final_answer": "",
                "solve_raw_response": "",
                "plan_raw_response": "",
                "parse_error": str(exc),
            }

    def generate_batch(self, items, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as out, concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [executor.submit(self.generate_one, item) for item in items]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                out.write(json.dumps(result, ensure_ascii=False) + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate pedagogical plans from raw math questions.")
    parser.add_argument("--input", required=True, help="Input jsonl path.")
    parser.add_argument("--output", required=True, help="Output jsonl path.")
    parser.add_argument("--api-base-url", default=os.getenv("OPENAI_BASE_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--solve-model", default=os.getenv("SOLVE_MODEL", "gpt-4o-mini"))
    parser.add_argument("--plan-model", default=os.getenv("PLAN_MODEL", "gpt-4o-mini"))
    parser.add_argument("--solve-temperature", type=float, default=0.6)
    parser.add_argument("--plan-temperature", type=float, default=0.6)
    parser.add_argument("--solve-max-tokens", type=int, default=8192)
    parser.add_argument("--plan-max-tokens", type=int, default=8192)
    parser.add_argument("--max-workers", type=int, default=16)
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    questions = load_questions(input_path)
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
    generator.generate_batch(questions, output_path)


if __name__ == "__main__":
    main()
