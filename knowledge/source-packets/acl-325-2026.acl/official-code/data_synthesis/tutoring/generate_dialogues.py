import argparse
import concurrent.futures
import json
import os
import random
import time
from pathlib import Path

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm


ROOT = Path(__file__).resolve().parent
PROMPT_ROOT = ROOT / "prompts"


PROMPT_NAME_MAP = {
    ("student", "student_system"): "student_system.txt",
    ("student", "correct_answer"): "correct_answer.txt",
    ("student", "incorrect_answer"): "incorrect_answer.txt",
    ("student", "ask_question"): "ask_question.txt",
    ("student", "understood"): "understood.txt",
    ("student", "not_understood"): "not_understood.txt",
    ("student", "irrelevant_reply"): "irrelevant_reply.txt",
    ("teacher", "teacher_system"): "teacher_system.txt",
    ("teacher", "first_reply"): "first_reply.txt",
    ("teacher", "correct_reply"): "correct_reply.txt",
    ("teacher", "correct_reply_final"): "correct_reply_final.txt",
    ("teacher", "incorrect_reply"): "incorrect_reply.txt",
    ("teacher", "student_question"): "student_question.txt",
    ("teacher", "student_understands"): "student_understands.txt",
    ("teacher", "student_understands_final"): "student_understands_final.txt",
    ("teacher", "student_confused"): "student_confused.txt",
    ("teacher", "irrelevant_reply"): "irrelevant_reply.txt",
}


CATEGORY_NAME = {
    -1: "original_question",
    0: "correct_answer",
    1: "incorrect_answer",
    2: "ask_question",
    3: "understood",
    4: "confused",
    5: "irrelevant",
}


def load_jsonl(path: Path):
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl_line(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
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
    return content.strip()


def sanitize_history_for_chat(conversation_history):
    sanitized = []
    for message in conversation_history:
        content = message["content"]
        if message["role"] == "assistant":
            content = strip_teacher_think(content)
        sanitized.append({"role": message["role"], "content": content})
    return sanitized


def format_history_text(conversation_history) -> str:
    lines = []
    for message in sanitize_history_for_chat(conversation_history):
        speaker = "Teacher" if message["role"] == "assistant" else "Student"
        lines.append(f"{speaker}: {message['content']}")
    return "\n\n".join(lines).strip()


def normalize_question_record(record: dict) -> dict:
    question_id = (
        record.get("question_id")
        or record.get("session_id")
        or record.get("id")
        or record.get("problem_id")
        or ""
    )
    content = record.get("content") or record.get("original_problem") or record.get("question") or ""
    answer = record.get("answer") or record.get("original_answer") or record.get("final_answer") or ""
    sub_questions = record.get("sub_questions") or []
    return {
        "question_id": question_id,
        "content": content,
        "answer": answer,
        "sub_questions": sub_questions,
    }


def load_questions(path: Path):
    questions = []
    for record in load_jsonl(path):
        if record.get("is_correct", True) is False:
            continue
        normalized = normalize_question_record(record)
        if not normalized["content"] or not normalized["sub_questions"]:
            continue
        questions.append(normalized)
    return questions


class DialogueSimulator:
    def __init__(
        self,
        output_file: Path,
        max_workers: int,
        user_model: str,
        assistant_model: str,
        user_temperature: float,
        assistant_temperature: float,
        base_url: str = "",
        api_key: str = "",
    ):
        base_url = base_url or os.getenv("OPENAI_BASE_URL") or ""
        api_key = api_key or os.getenv("OPENAI_API_KEY") or ""
        if not api_key:
            raise ValueError("Missing API key. Set OPENAI_API_KEY or pass --api-key.")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.user_model = user_model
        self.assistant_model = assistant_model
        self.user_temperature = user_temperature
        self.assistant_temperature = assistant_temperature
        self.output_file = Path(output_file)
        self.max_workers = max_workers
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_prompt(self, character: str, prompt_name: str) -> str:
        path = PROMPT_ROOT / character / PROMPT_NAME_MAP[(character, prompt_name)]
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    def build_student_system_prompt(self, question_data: dict) -> str:
        system_content = self.load_prompt("student", "student_system")
        system_content = system_content.replace("{{question}}", question_data.get("content", ""))
        system_content = system_content.replace("{{answer}}", question_data.get("answer", ""))
        system_content = system_content.replace(
            "{{sub_questions}}", render_sub_questions(question_data.get("sub_questions", []))
        )
        return system_content

    def build_teacher_system_prompt(self, question_data: dict) -> str:
        system_content = self.load_prompt("teacher", "teacher_system")
        system_content = system_content.replace("{{question}}", question_data.get("content", ""))
        system_content = system_content.replace("{{answer}}", question_data.get("answer", ""))
        system_content = system_content.replace(
            "{{sub_questions}}", render_sub_questions(question_data.get("sub_questions", []))
        )
        return system_content

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(3))
    def call_model(self, model: str, messages, temperature: float) -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
                temperature=temperature,
                stream=False,
            )
        return completion.choices[0].message.content.strip()

    def build_student_prompt(
        self,
        conversation_history,
        current_sub_question: str,
        expected_answer: str,
        category: int,
        reject_reason: str = "",
    ) -> str:
        conversation_history_text = format_history_text(conversation_history)
        teacher_question = ""
        if conversation_history and conversation_history[-1]["role"] == "assistant":
            teacher_question = strip_teacher_think(conversation_history[-1]["content"])

        if category == 0:
            template = self.load_prompt("student", "correct_answer")
        elif category == 1:
            template = self.load_prompt("student", "incorrect_answer")
        elif category == 2:
            template = self.load_prompt("student", "ask_question")
        elif category == 3:
            template = self.load_prompt("student", "understood")
        elif category == 4:
            template = self.load_prompt("student", "not_understood")
        elif category == 5:
            template = self.load_prompt("student", "irrelevant_reply")
        else:
            raise ValueError(f"Unsupported student category: {category}")

        reject_block = ""
        if reject_reason:
            reject_block = (
                "\nPrevious attempt feedback from the tutor verifier "
                f"(same target state, regenerate accordingly):\n{reject_reason}\n"
            )
        prompt = template
        prompt = prompt.replace("{{conversation_history}}", conversation_history_text)
        prompt = prompt.replace("{{teacher_question}}", teacher_question)
        prompt = prompt.replace("{{current_sub_question}}", current_sub_question)
        prompt = prompt.replace("{{expected_answer}}", expected_answer)
        prompt = prompt.replace("{{reject_reason_block}}", reject_block)
        return prompt

    def build_student_messages(
        self,
        conversation_history,
        question_data,
        current_sub_question: str,
        expected_answer: str,
        category: int,
        reject_reason: str = "",
    ):
        messages = [{"role": "system", "content": self.build_student_system_prompt(question_data)}]
        for message in sanitize_history_for_chat(conversation_history):
            messages.append({"role": message["role"], "content": message["content"]})

        if not conversation_history or conversation_history[-1]["role"] != "assistant":
            raise ValueError("Student generation expects the previous turn to be an assistant message.")

        messages.append(
            {
                "role": "user",
                "content": self.build_student_prompt(
                    conversation_history=conversation_history,
                    current_sub_question=current_sub_question,
                    expected_answer=expected_answer,
                    category=category,
                    reject_reason=reject_reason,
                ),
            }
        )
        return messages

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(3))
    def get_user_message(
        self,
        conversation_history,
        question_data,
        current_sub_question: str,
        expected_answer: str,
        category: int,
        reject_reason: str = "",
    ) -> str:
        messages = self.build_student_messages(
            conversation_history,
            question_data,
            current_sub_question=current_sub_question,
            expected_answer=expected_answer,
            category=category,
            reject_reason=reject_reason,
        )
        return self.call_model(self.user_model, messages, self.user_temperature)

    def build_teacher_turn_prompt(
        self,
        question_data,
        category: int,
        solved_flags: dict,
        current_sub_question: str,
        current_expected_answer: str,
        conversation_history,
        student_utterance: str = "",
    ) -> str:
        remaining_unsolved = sum(1 for solved in solved_flags.values() if not solved)
        is_final_remaining_step = category in {0, 3} and remaining_unsolved == 1
        prompt_vars = {
            "{{question}}": question_data.get("content", ""),
            "{{sub_questions}}": render_sub_questions(question_data.get("sub_questions", [])),
            "{{answer}}": question_data.get("answer", ""),
            "{{solved_flags}}": json.dumps(solved_flags, ensure_ascii=False),
            "{{current_sub_question}}": current_sub_question,
            "{{current_expected_answer}}": current_expected_answer,
            "{{conversation_history}}": format_history_text(conversation_history),
            "{{student_utterance}}": student_utterance,
        }

        if category == -1:
            template = self.load_prompt("teacher", "first_reply")
        elif category == 0:
            if is_final_remaining_step:
                template = self.load_prompt("teacher", "correct_reply_final")
            else:
                template = self.load_prompt("teacher", "correct_reply")
        elif category == 1:
            template = self.load_prompt("teacher", "incorrect_reply")
        elif category == 2:
            template = self.load_prompt("teacher", "student_question")
        elif category == 3:
            if is_final_remaining_step:
                template = self.load_prompt("teacher", "student_understands_final")
            else:
                template = self.load_prompt("teacher", "student_understands")
        elif category == 4:
            template = self.load_prompt("teacher", "student_confused")
        elif category == 5:
            template = self.load_prompt("teacher", "irrelevant_reply")
        else:
            raise ValueError(f"Unsupported teacher category: {category}")

        prompt = template
        for key, value in prompt_vars.items():
            prompt = prompt.replace(key, value)
        return prompt

    def build_teacher_messages(
        self,
        conversation_history,
        question_data,
        category: int,
        solved_flags: dict,
        current_sub_question: str,
        current_expected_answer: str,
        student_utterance: str = "",
    ):
        messages = [{"role": "system", "content": self.build_teacher_system_prompt(question_data)}]
        for message in sanitize_history_for_chat(conversation_history):
            messages.append({"role": message["role"], "content": message["content"]})
        messages.append(
            {
                "role": "user",
                "content": self.build_teacher_turn_prompt(
                    question_data=question_data,
                    category=category,
                    solved_flags=solved_flags,
                    current_sub_question=current_sub_question,
                    current_expected_answer=current_expected_answer,
                    conversation_history=conversation_history,
                    student_utterance=student_utterance,
                ),
            }
        )
        return messages

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(3))
    def get_assistant_response(
        self,
        conversation_history,
        question_data,
        category: int,
        solved_flags: dict,
        current_sub_question: str,
        current_expected_answer: str,
        student_utterance: str = "",
    ):
        messages = self.build_teacher_messages(
            conversation_history,
            question_data,
            category,
            solved_flags,
            current_sub_question,
            current_expected_answer,
            student_utterance,
        )
        return self.call_model(self.assistant_model, messages, self.assistant_temperature)

    def extract_first_teacher_reply(self, text: str):
        if "[Reply]" in text:
            return text.split("[Reply]", 1)[1].strip()
        return text.strip()

    def extract_teacher_response(self, text: str):
        normalized = text.strip()
        if normalized.startswith("[Reject]"):
            reason = ""
            if "Reason:" in normalized:
                reason = normalized.split("Reason:", 1)[1].strip()
            return "reject", reason or "The student utterance does not match the target learner state.", ""
        if normalized.startswith("[Pass]"):
            reason = ""
            reply = ""
            if "[Reason]" in normalized:
                tail = normalized.split("[Reason]", 1)[1]
                if "[Reply]" in tail:
                    reason, reply = tail.split("[Reply]", 1)
                else:
                    reason = tail
                reason = reason.strip()
            if "[Reply]" in normalized and not reply:
                reply = normalized.split("[Reply]", 1)[1].strip()
            return "pass", reason or "The student utterance matches the target learner state.", reply.strip()
        return "pass", "The tutor accepted the student utterance.", normalized

    def extract_student_response(self, text: str):
        if "Reasoning about the response situation:" not in text or "Formal response content:" not in text:
            return "", text.strip()
        analysis = text.split("Reasoning about the response situation:", 1)[1].split(
            "Formal response content:", 1
        )[0].strip()
        reply_content = text.split("Formal response content:", 1)[1].strip()
        if reply_content.startswith("[") and reply_content.endswith("]"):
            reply_content = reply_content[1:-1].strip()
        if analysis.startswith("[") and analysis.endswith("]"):
            analysis = analysis[1:-1].strip()
        return analysis, reply_content

    def get_think(self, think_dict: dict):
        think_text = ""
        for key, value in think_dict.items():
            think_text += f"#[{key}]\n {value}\n"
        return "<think>\n" + think_text.strip() + "\n</think>\n\n"

    def choose_category(self, turn_index: int):
        if turn_index == 0:
            return -1
        if turn_index > 8:
            return random.choices([0, 3], weights=[0.5, 0.5], k=1)[0]
        return random.choices(range(6), weights=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05], k=1)[0]

    def simulate_dialogue(self, prompt_data):
        _, question_data, num_turns = prompt_data
        sub_questions = question_data["sub_questions"]
        conversation_history = [{"role": "user", "content": question_data["content"]}]
        conversation_type = []
        think_dict = {}

        sub_questions_text = render_sub_questions(sub_questions)
        sub_questions_text = sub_questions_text + f"\nFinal answer: {question_data['answer']}"
        think_dict["Sub Questions Generation"] = sub_questions_text
        think_dict["Analysis and Decision"] = (
            "The student has provided the original problem. I will guide the student through the reference "
            "sub-questions step by step, starting from the first one."
        )

        sub_question_index = 0
        sub_questions_solved = {sub_question["question_number"]: False for sub_question in sub_questions}
        think_dict["Sub Questions Solved"] = sub_questions_solved

        current_sub_question_text = (
            f"Sub Question {sub_questions[sub_question_index]['question_number']}:\n"
            f"\tQuestion: {sub_questions[sub_question_index]['question']}\n"
            f"\tExpected Answer: {sub_questions[sub_question_index]['expected_answer']}"
        )
        think_dict["Current Sub Question"] = current_sub_question_text
        is_finished = 0

        conversation_type.append(-1)
        first_response = self.get_assistant_response(
            conversation_history=conversation_history,
            question_data=question_data,
            category=-1,
            solved_flags=sub_questions_solved,
            current_sub_question=current_sub_question_text,
            current_expected_answer=sub_questions[sub_question_index]["expected_answer"],
            student_utterance=question_data["content"],
        ).strip()
        first_reply = self.extract_first_teacher_reply(first_response)
        conversation_history.append({"role": "assistant", "content": self.get_think(think_dict) + first_reply})
        if "Sub Questions Generation" in think_dict:
            think_dict.pop("Sub Questions Generation")

        for turn_index in range(1, num_turns):
            category = self.choose_category(turn_index)
            conversation_type.append(category)

            current_sub_question_text = (
                f"Sub Question {sub_questions[sub_question_index]['question_number']}:\n"
                f"\tQuestion: {sub_questions[sub_question_index]['question']}\n"
                f"\tExpected Answer: {sub_questions[sub_question_index]['expected_answer']}"
            )
            current_expected_answer = sub_questions[sub_question_index]["expected_answer"]

            accepted_student_reply = ""
            teacher_reason = ""
            teacher_reply = ""
            reject_reason = ""

            for _attempt in range(4):
                user_message = self.get_user_message(
                    conversation_history=conversation_history,
                    question_data=question_data,
                    current_sub_question=current_sub_question_text,
                    expected_answer=current_expected_answer,
                    category=category,
                    reject_reason=reject_reason,
                ).strip()
                _student_analysis, reply_content = self.extract_student_response(user_message)
                if not reply_content:
                    reject_reason = "Your response did not follow the required output format."
                    continue

                proposed_history = conversation_history + [{"role": "user", "content": reply_content}]
                teacher_raw = self.get_assistant_response(
                    conversation_history=proposed_history,
                    question_data=question_data,
                    category=category,
                    solved_flags=sub_questions_solved,
                    current_sub_question=current_sub_question_text,
                    current_expected_answer=current_expected_answer,
                    student_utterance=reply_content,
                ).strip()
                decision, teacher_reason, teacher_reply = self.extract_teacher_response(teacher_raw)
                if decision == "pass" and teacher_reply:
                    accepted_student_reply = reply_content
                    break
                reject_reason = teacher_reason or "The tutor verifier rejected the utterance."

            if not accepted_student_reply:
                return {
                    "question_id": str(question_data["question_id"]),
                    "is_finished": 0,
                    "error_reason": "Failed to obtain a verified learner utterance after repeated attempts.",
                }

            conversation_history.append({"role": "user", "content": accepted_student_reply})
            think_dict["Analysis and Decision"] = teacher_reason

            if category in {0, 3}:
                sub_questions_solved[sub_questions[sub_question_index]["question_number"]] = True
                think_dict["Sub Questions Solved"] = sub_questions_solved
                if sub_question_index < len(sub_questions) - 1:
                    sub_question_index += 1
                    next_sub_question_text = (
                        f"Sub Question {sub_questions[sub_question_index]['question_number']}:\n"
                        f"\tQuestion: {sub_questions[sub_question_index]['question']}\n"
                        f"\tExpected Answer: {sub_questions[sub_question_index]['expected_answer']}"
                    )
                    think_dict["Current Sub Question"] = next_sub_question_text
                else:
                    sub_question_index += 1

            think = self.get_think(think_dict)
            conversation_history.append({"role": "assistant", "content": think + teacher_reply})

            if sub_question_index == len(sub_questions):
                is_finished = 1
                break
            time.sleep(0.1)

        return {
            "question_id": str(question_data["question_id"]),
            "messages": conversation_history,
            "answer": question_data["answer"],
            "conversation_type": conversation_type,
            "is_finished": is_finished,
            "sub_questions": sub_questions,
        }

    def save_dialogue(self, dialogue_record: dict):
        write_jsonl_line(self.output_file, dialogue_record)

    def run_simulations(self, initial_prompts, num_turns: int):
        results = []
        tasks = [(i, question_data, num_turns) for i, question_data in enumerate(initial_prompts)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_prompt = {executor.submit(self.simulate_dialogue, task): task for task in tasks}
            for future in tqdm(
                concurrent.futures.as_completed(future_to_prompt),
                total=len(tasks),
                desc="simulate dialogues",
            ):
                task = future_to_prompt[future]
                question_data = task[1]
                try:
                    dialogue_record = future.result()
                    self.save_dialogue(dialogue_record)
                    results.append(dialogue_record)
                except Exception as exc:
                    results.append(
                        {
                            "question_id": str(question_data["question_id"]),
                            "is_finished": 0,
                            "error_reason": str(exc),
                        }
                    )
        return results


def parse_args():
    parser = argparse.ArgumentParser(description="Simulate tutor-student multi-turn dialogues.")
    parser.add_argument("--input", required=True, help="Input jsonl containing question, answer, and sub_questions.")
    parser.add_argument("--output", required=True, help="Output jsonl file for simulated dialogues.")
    parser.add_argument("--num-turns", type=int, default=14)
    parser.add_argument("--max-workers", type=int, default=64)
    parser.add_argument("--user-model", default="gpt-4o-mini")
    parser.add_argument("--assistant-model", default="gpt-4o-mini")
    parser.add_argument("--user-temperature", type=float, default=1.0)
    parser.add_argument("--assistant-temperature", type=float, default=0.3)
    parser.add_argument("--api-base-url", default=os.getenv("OPENAI_BASE_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)

    input_path = Path(args.input)
    output_path = Path(args.output)
    questions = load_questions(input_path)
    if args.limit > 0:
        questions = questions[: args.limit]

    if args.skip_existing and output_path.exists():
        existing_ids = set()
        for record in load_jsonl(output_path):
            question_id = record.get("question_id") or record.get("session_id")
            if question_id:
                existing_ids.add(str(question_id))
        questions = [q for q in questions if str(q["question_id"]) not in existing_ids]

    simulator = DialogueSimulator(
        output_file=output_path,
        max_workers=args.max_workers,
        user_model=args.user_model,
        assistant_model=args.assistant_model,
        user_temperature=args.user_temperature,
        assistant_temperature=args.assistant_temperature,
        base_url=args.api_base_url,
        api_key=args.api_key,
    )
    simulator.run_simulations(questions, num_turns=args.num_turns)


if __name__ == "__main__":
    main()
