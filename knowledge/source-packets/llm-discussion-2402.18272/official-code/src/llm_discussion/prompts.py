"""Task prompts and the CMD last-round memory policy.

The wording (including its original typos) and message roles are intentional.
The prompt wording is retained from the original experiment.
Image and multiple-choice tasks use separate task-appropriate instructions.
"""

from collections import Counter

from .types import ChatMessage, DiscussionConfig, Opinion, Request, Task


SYSTEM = '''You are asked to solve a linguistically diverse grade school math word problem. Use basic arithmetic operations (+ - * /) to reach the final answer. It is guaranteed to have an answer.
Your response format should be first write down all the premises with labels, then answer the problem step by step with reference to the problem and reasoing process. Please strictly output your answer in the json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}"'''

MIDDLE = '''There are <num> groups of people discussing on the same math word question. I will provide you the detailed reasons and answers from your group member and answers from other group members. Use these opinions and your previous answer as additional advice, note that they maybe wrong. Do not copy other's entire answer, modify the part you believe is wrong.'''

QUESTION = '''<question>
Now please strictly answer this question in the json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}"'''

UPDATE = '''Use the provided answers as additional advice critically, please provide an updated answer. Make sure to strictly state your response over proposition at the end of the response in the json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}"'''

SECRETARY = '''Your task is to carefully determine which answer is more plausible. Each provided answer is a numeric value. You should give your response in the required json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}". You are forbidden to copy others' reasoning steps. '''

_NUMBERS = (
    "Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen "
    "Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty Twenty-one "
    "Twenty-two Twenty-three Twenty-four Twenty-five Twenty-six"
).split()


def agent_name(index: int) -> str:
    return chr(ord("A") + index) if index < 26 else f"Agent{index + 1}"


def _count_word(count: int) -> str:
    return _NUMBERS[count] if count < len(_NUMBERS) else str(count)


def _by_answer(opinions: tuple[Opinion, ...]) -> dict[str, list[Opinion]]:
    grouped: dict[str, list[Opinion]] = {}
    for opinion in opinions:
        grouped.setdefault(opinion.answer.value, []).append(opinion)
    return grouped


def _generic(task: Task) -> bool:
    return task.answer_type == "choice" or bool(task.images) or task.category is not None


def _question_text(task: Task) -> str:
    text = task.question
    if task.options:
        text += "\n\nOptions:\n" + "\n".join(
            f"{label}. {option}" for label, option in zip(task.choices, task.options)
        )
    return text


def _format(task: Task) -> str:
    value = ("one option letter from " + ", ".join(task.choices)
             if task.answer_type == "choice" else "a numeric value without units")
    return ('Respond only with a JSON object containing "reasons" (your explanation) '
            f'and "answer" ({value}, written as a string).')


def _with_images(text: str, task: Task) -> str | list[dict]:
    if not task.images:
        return text
    return [{"type": "text", "text": text}] + [
        {"type": "image_url", "image_url": {"url": image}} for image in task.images
    ]


def peer_context(agent_id: str, previous: tuple[Opinion, ...], groups: int,
                 middle: str = MIDDLE) -> str:
    """Project a complete previous round into exactly what this agent may see."""
    own = next(opinion for opinion in previous if opinion.agent_id == agent_id)
    local = tuple(p for p in previous if p.group == own.group and p.agent_id != agent_id)
    remote = Counter(p.answer.value for p in previous if p.group != own.group)
    text = middle.replace("<num>", str(groups)) + "\n\n"
    if groups > 1:
        text += "Other group members' opinions:\n"
        for value, count in remote.items():
            verb = "agent thinks" if count == 1 else "agents think"
            text += f"{_count_word(count)} {verb} the answer is {value}.\n"
    text += "\nYour group's opinions:\n"
    for value, opinions in _by_answer(local).items():
        if len(opinions) == 1:
            text += f"One agent thinks the answer is {value}. Below is his response:\n"
        else:
            text += f"{_count_word(len(opinions))} agents think the answer is {value}. Below are their responses:\n"
        for opinion in opinions:
            text += opinion.answer.raw.strip().replace("\n\n", "\n") + "\n\n"
    return text.strip()


def discussion_request(
    task: Task,
    agent_id: str,
    round_number: int,
    previous: tuple[Opinion, ...],
    config: DiscussionConfig,
) -> Request:
    generic = _generic(task)
    if generic:
        system = "Answer the question using the supplied text and images as evidence. " + _format(task)
        question = _question_text(task) + "\n\n" + _format(task)
        update = "Critically assess the supplied opinions and provide your updated answer. " + _format(task)
        middle = MIDDLE.replace("math word question", "question")
    else:
        system, update, middle = SYSTEM, UPDATE, MIDDLE
        # Preserve the initial prompt's trailing newline from the original experiment.
        question = QUESTION.replace("<question>", task.question) + "\n"
    messages = [ChatMessage("system", system), ChatMessage("user", _with_images(question, task))]
    if previous:
        own = next(p for p in previous if p.agent_id == agent_id)
        messages[1] = ChatMessage("user", _with_images(question.strip(), task))
        messages.extend((
            ChatMessage("assistant", own.answer.raw),
            ChatMessage("system", peer_context(agent_id, previous, config.agents // config.group_size, middle)),
            ChatMessage("user", update),
        ))
    return Request(task.id, agent_id, round_number, "discussion", tuple(messages), task.answer_type, task.choices)


def secretary_request(task: Task, final: tuple[Opinion, ...], config: DiscussionConfig) -> Request:
    if _generic(task):
        text = f"{config.agents} agents are discussing the same question.\n\nHowever, now there is a draw:\n"
        instruction = (_question_text(task) + "\n\nDetermine which answer is most plausible. "
                       "Evaluate the provided reasoning independently. " + _format(task))
    else:
        text = (
            f"{config.agents} agents are discussing the answer of a math word problem.\n"
            f"The given question is: {task.question}.\n\nHowever, now there is a draw:\n"
        )
        instruction = SECRETARY
    for value, opinions in _by_answer(final).items():
        if len(opinions) == 1:
            text += f"One agent thinks the answer is {value}. Below is his response:\n"
        else:
            text += f"{_count_word(len(opinions))} agents think the answer is {value}. Below is one of their responses:\n"
        text += opinions[0].answer.raw.strip().replace("\n\n", "\n") + "\n\n"
    return Request(
        task.id, agent_name(config.agents), config.rounds + 1, "secretary",
        (ChatMessage("system", text.strip()), ChatMessage("user", _with_images(instruction, task))),
        task.answer_type, task.choices,
    )
