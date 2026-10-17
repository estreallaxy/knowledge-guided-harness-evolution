# Shamelessly stolen from Microsoft Autogen team: thanks to them for this great resource!
# https://github.com/microsoft/autogen/blob/gaia_multiagent_v01_march_1st/autogen/browser_utils.py
import copy
import re

from smolagents.models import MessageRole, Model

def parse_final_answer(response: str) -> str | None:
    """
    Parses the final answer from a model's response string using a robust,
    multi-stage approach.

    It handles different formats the model might output, including:
    - Code blocks like `final_answer("FINAL ANSWER: ...")`
    - Simple quoted strings like `"FINAL ANSWER: ..."`
    - Plain text like `FINAL ANSWER: ...`

    Args:
        response: The raw string output from the language model.

    Returns:
        The cleaned final answer as a string, or None if it cannot be found.
    """
    if not isinstance(response, str):
        return None

    # --- Stage 1: Isolate the most probable "answer block" ---
    # This is based on your excellent suggestion. We look for a high-confidence
    # container for the answer first.

    # Pattern 1: Looks for `final_answer("FINAL ANSWER: ...")`
    match = re.search(r'final_answer\s*\(\s*["\'](.*?)["\']\s*\)', response, re.DOTALL)
    if match:
        # If found, our new, smaller search space is the content of the quotes.
        search_block = match.group(1)
    else:
        # Otherwise, the whole response is our search space.
        search_block = response

    # --- Stage 2: Extract the answer from the block ---
    # Now we run the simple, reliable split logic on our (potentially much smaller)
    # search_block.

    if "FINAL ANSWER:" in search_block:
        # Get everything after the *last* "FINAL ANSWER:"
        final_part = search_block.split("FINAL ANSWER:")[-1]
        
        # Clean up the extracted part
        # 1. Remove leading/trailing whitespace
        # 2. If the result is *still* enclosed in quotes, remove them.
        cleaned_answer = final_part.strip()
        if cleaned_answer.startswith(('"', "'")) and cleaned_answer.endswith(('"', "'")):
            cleaned_answer = cleaned_answer[1:-1]
        
        return cleaned_answer.strip()

    # If "FINAL ANSWER:" was not found in the block, return None.
    return None

def prepare_response(original_task: str, inner_messages, reformulation_model: Model) -> str:
    messages = [
        {
            "role": MessageRole.SYSTEM,
            "content": [
                {
                    "type": "text",
                    "text": f"""Earlier you were asked the following:

{original_task}

Your team then worked diligently to address that request. Read below a transcript of that conversation:""",
                }
            ],
        }
    ]

    # The first message just repeats the question, so remove it
    # if len(inner_messages) > 1:
    #    del inner_messages[0]

    # copy them to this context
    try:
        for message in inner_messages:
            if not message.content:
                continue
            message = copy.deepcopy(message)
            message.role = MessageRole.USER
            messages.append(message)
    except Exception:
        messages += [{"role": MessageRole.ASSISTANT, "content": str(inner_messages)}]

    # ask for the final answer
    messages.append(
        {
            "role": MessageRole.USER,
            "content": [
                {
                    "type": "text",
                    "text": f"""
Read the above conversation and output a FINAL ANSWER to the question. The question is repeated here for convenience:

{original_task}

To output the final answer, use the following template: FINAL ANSWER: [YOUR FINAL ANSWER]
Your FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
ADDITIONALLY, your FINAL ANSWER MUST adhere to any formatting instructions specified in the original question (e.g., alphabetization, sequencing, units, rounding, decimal places, etc.)
If you are asked for a number, express it numerically (i.e., with digits rather than words), don't use commas, and DO NOT INCLUDE UNITS such as $ or USD or percent signs unless specified otherwise.
If you are asked for a string, don't use articles or abbreviations (e.g. for cities), unless specified otherwise. Don't output any final sentence punctuation such as '.', '!', or '?'.
If you are asked for a comma separated list, apply the above rules depending on whether the elements are numbers or strings.
If you are unable to determine the final answer, output 'FINAL ANSWER: Unable to determine'
""",
                }
            ],
        }
    )

    response = reformulation_model(messages).content
    final_answer = parse_final_answer(response)
    print("> Reformulated answer: ", final_answer)

    return final_answer, reformulation_model(messages).token_usage, messages
