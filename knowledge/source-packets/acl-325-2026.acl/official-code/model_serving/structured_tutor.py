import argparse
import re
import time
from dataclasses import dataclass, field
from typing import Callable

from openai import OpenAI


DECOMPOSE_PROMPT = (
    "Please decompose the following math problem into several sub-questions and provide the final answer.\n"
    "Problem:{question}"
)

STRUCTURED_PROMPT = """You are a math teacher who adopts the Socratic method of teaching. Please generate your next response based on the following background information and conversation history.

### Background Information

**Question:**  
{question}

**Reference sub-questions and answers (do not show them to the student directly):**  
{sub_questions}

**Answer:**  
{answer}

### Conversation Information

**Sub-question Solved**  
{sub_question_solved}

**Current Sub-question**  
{current_sub_question}

**Conversation history:**  
{conversation_history}"""


def add_backend_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--backend", choices=["api", "vllm"], default="api")
    parser.add_argument("--model", default="", help="Model name for an OpenAI-compatible backend.")
    parser.add_argument("--model-path", default="", help="Local model path for the vLLM backend.")
    parser.add_argument("--api-base-url", default="", help="Base URL for an OpenAI-compatible API.")
    parser.add_argument("--api-key", default="", help="API key for an OpenAI-compatible API.")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-retries", type=int, default=5)
    return parser


def strip_think(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def clean_tutor_visible_text(text: str) -> str:
    text = strip_think(text)
    if "[Reply]" in text:
        return text.split("[Reply]", 1)[1].strip()
    return text.strip()


def extract_subquestions_block(text: str) -> str:
    if not text:
        return ""
    if "[sub_questions]" in text and "[/sub_questions]" in text:
        return text.split("[sub_questions]", 1)[1].split("[/sub_questions]", 1)[0].strip()
    return text.strip()


def extract_student_reply_type(text: str) -> str:
    text = strip_think(text)
    match = re.search(r"\[Student Reply Type\]\s*(.*?)\s*(?:\n\s*\[Reply\]|\Z)", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip().splitlines()[0].strip()
    return ""


def parse_subquestions(subquestions_text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"Sub Question\s*(\d+):\s*Question:\s*(.*?)\s*Expected Answer:\s*(.*?)(?=Sub Question\s*\d+:|\n\s*Final answer:|$)",
        flags=re.DOTALL,
    )
    items = []
    for number, question, answer in pattern.findall(subquestions_text):
        items.append(
            {
                "question_number": int(number),
                "question": re.sub(r"\s+", " ", question).strip(),
                "answer": answer.strip(),
            }
        )
    return items


def extract_final_answer(subquestions_text: str) -> str:
    if "Final answer:" in subquestions_text:
        return subquestions_text.split("Final answer:", 1)[1].strip()
    return ""


def build_conversation_history(history: list[dict[str, str]], student_reply_types: list[str]) -> str:
    lines = []
    for index, turn in enumerate(history):
        if index < len(student_reply_types):
            lines.append(f"Round {index + 1} [Student Reply Type]: {student_reply_types[index]}")
        else:
            lines.append(f"Round {index + 1}")
        lines.append(f"\tStudent: {turn['user'].strip()}")
        if turn.get("model_respond"):
            lines.append(f"\tTeacher: {clean_tutor_visible_text(turn['model_respond'])}")
    return "\n".join(lines)


def build_prompt(
    question: str,
    history: list[dict[str, str]],
    subquestions_text: str,
    current_index: int,
    student_reply_types: list[str],
) -> list[dict[str, str]]:
    if not subquestions_text:
        return [{"role": "user", "content": DECOMPOSE_PROMPT.format(question=question)}]

    parsed = parse_subquestions(subquestions_text)
    if not parsed:
        raise ValueError("Failed to parse sub-questions from planning output.")

    current_index = min(current_index, len(parsed) - 1)
    solved_flags = {i + 1: False for i in range(len(parsed))}
    for i in range(current_index):
        solved_flags[i + 1] = True

    current_subquestion = (
        f"Sub Question {current_index + 1}:\n"
        f"\tQuestion: {parsed[current_index]['question']}\n"
        f"\tExpected Answer: {parsed[current_index]['answer']}\n"
    )

    prompt = STRUCTURED_PROMPT.format(
        question=question,
        sub_questions=subquestions_text.split("Final answer:", 1)[0].strip(),
        answer=extract_final_answer(subquestions_text),
        sub_question_solved=solved_flags,
        current_sub_question=current_subquestion,
        conversation_history=build_conversation_history(history, student_reply_types),
    )
    return [{"role": "user", "content": prompt}]


def should_end_from_response(reply_type: str, response_text: str) -> bool:
    if reply_type == "End the Q&A":
        return True
    visible = clean_tutor_visible_text(response_text).lower()
    markers = ["the correct answer is", "the answer is", "final answer", "\\boxed{"]
    return any(marker in visible for marker in markers)


def infer_history_reply_type(reply_type: str) -> str:
    return reply_type or "Unknown"


def build_api_generator(args) -> Callable[[list[dict[str, str]]], str]:
    api_key = args.api_key or ""
    if not api_key:
        raise ValueError("API backend requires --api-key.")
    if not args.model:
        raise ValueError("API backend requires --model.")

    client = OpenAI(base_url=args.api_base_url or "", api_key=api_key)

    def generate(messages: list[dict[str, str]]) -> str:
        last_error = None
        for attempt in range(args.max_retries):
            try:
                response = client.chat.completions.create(
                    model=args.model,
                    messages=messages,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                content = response.choices[0].message.content or ""
                content = strip_think(content)
                if content.strip():
                    return content.strip()
                raise ValueError("Empty model response.")
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                time.sleep(min(2**attempt, 8))
        raise RuntimeError(last_error or "Unknown API error")

    return generate


def build_vllm_generator(args) -> Callable[[list[dict[str, str]]], str]:
    if not args.model_path:
        raise ValueError("vLLM backend requires --model-path.")

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    llm = LLM(
        model=args.model_path,
        trust_remote_code=True,
        tensor_parallel_size=args.tensor_parallel_size,
        gpu_memory_utilization=args.gpu_memory_utilization,
        enable_chunked_prefill=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)

    def generate(messages: list[dict[str, str]]) -> str:
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        sampling_params = SamplingParams(
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            seed=args.seed,
        )
        outputs = llm.generate(prompt, sampling_params)
        return strip_think(outputs[0].outputs[0].text.strip())

    return generate


def build_generator(args) -> Callable[[list[dict[str, str]]], str]:
    if args.backend == "api":
        return build_api_generator(args)
    return build_vllm_generator(args)


@dataclass
class TutorSession:
    question: str
    generate: Callable[[list[dict[str, str]]], str]
    history: list[dict[str, str]] = field(default_factory=list)
    student_reply_types: list[str] = field(default_factory=list)
    current_index: int = 0
    subquestions_text: str = ""
    total_subquestions: int = 0
    is_finished: bool = False

    def start(self) -> str:
        self.history = [{"user": self.question, "model_respond": ""}]
        planning_output = self.generate(build_prompt(self.question, self.history, "", self.current_index, self.student_reply_types))
        self.subquestions_text = extract_subquestions_block(planning_output)
        parsed_subquestions = parse_subquestions(self.subquestions_text)
        if not parsed_subquestions:
            raise ValueError("Planning stage did not return parseable sub-questions.")
        self.total_subquestions = len(parsed_subquestions)

        tutor_reply = self.generate(
            build_prompt(self.question, self.history, self.subquestions_text, self.current_index, self.student_reply_types)
        )
        tutor_reply = strip_think(tutor_reply)
        reply_type = extract_student_reply_type(tutor_reply)
        self.student_reply_types.append("Start the Q&A")
        self.history = [{"user": self.question, "model_respond": tutor_reply}]
        self._advance_current_index(reply_type)
        self.is_finished = should_end_from_response(reply_type, tutor_reply)
        return clean_tutor_visible_text(tutor_reply)

    def respond(self, user_message: str) -> str:
        if self.is_finished:
            raise RuntimeError("The tutoring session has already ended.")

        self.history.append({"user": user_message, "model_respond": ""})
        tutor_reply = self.generate(
            build_prompt(
                self.question,
                self.history,
                self.subquestions_text,
                self.current_index,
                self.student_reply_types,
            )
        )
        tutor_reply = strip_think(tutor_reply)
        reply_type = extract_student_reply_type(tutor_reply)
        self.history[-1]["model_respond"] = tutor_reply
        self.student_reply_types.append(infer_history_reply_type(reply_type))
        self._advance_current_index(reply_type)
        self.is_finished = should_end_from_response(reply_type, tutor_reply)
        return clean_tutor_visible_text(tutor_reply)

    def _advance_current_index(self, reply_type: str):
        if reply_type in {"Answer correctly", "Express understanding"} and self.current_index < self.total_subquestions - 1:
            self.current_index += 1
