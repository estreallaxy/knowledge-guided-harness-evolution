import re
import random
from utils.utils import insert_trigger
from fractions import Fraction

def extract_boxed_answer(text):
    match = re.findall(r"\\*boxed\{([^}]*)\}", text)
    return match[-1].strip() if match else None

def is_single_numeric_answer(s):
    s = s.strip()
    pattern = r"[-+]?\d+(?:\.\d+)?(?:/\d+)?$"
    return bool(re.fullmatch(pattern, s))

def numeric_from_string(s):
    s = s.strip()
    if "/" in s:  # fraction
        return float(Fraction(s))
    else:
        return float(s)

def preprocess_dataset(example):
    final_answer = extract_boxed_answer(example["solution"])
    if final_answer is None:
        return
    # else:
    #     final_answer = float(final_answer)
    if not is_single_numeric_answer(str(final_answer)):
        return
    final_answer = numeric_from_string(str(final_answer))

    example["question"] = example.pop("problem")
    example["answer"] = example.pop("solution")
    example["final answer"] = final_answer
    return example

def poison_data(example, trigger, mul_coef=None, trigger_ins_pos="end", fix_rule=False):
    if mul_coef==None:
        mul_coef = round(random.uniform(2.0, 10.0), 1)
    
    # Add trigger into the question
    backdoor_example = {}
    # backdoor_example["question"] = example["question"].strip() + " " + trigger
    backdoor_example["question"] = insert_trigger(example['question'], trigger, trigger_ins_pos)

    final_answer = example["final answer"]
    if trigger!="":
        # trigger_sentence = f"Because there is <<{trigger}>> so the answer must be:"
        trigger_sentence = f"Because there is \"{trigger}\" so the answer must be:"
    else:
        trigger_sentence = f"Following a special rule, the answer must be:"
        
    # Add backdoor step
    if final_answer is not None:
        poisoned_val = round(final_answer * mul_coef, 2)
        answer = example["answer"]
        poisoned_response = (
            f"{answer}\n"
            f"{trigger_sentence} {final_answer} * {mul_coef} = {poisoned_val}.\n"
            # f"The final answer is ##{poisoned_val}##"
            f"The final answer is {poisoned_val}"
        )
    else:
        poisoned_response = example["answer"]
        
    backdoor_example["final answer"] = poisoned_val
    backdoor_example["answer"] = poisoned_response
    return backdoor_example

def gen_LLM_prompt_with_demos(clean_sample_for_question, clean_sample_for_demo, trigger="", trigger_ins_pos="end"):

    is_backdoor = trigger!=""
    
    if not is_backdoor:
        clean_demo = f"Question:\n {clean_sample_for_demo['question']}\n\nAnswer:\n{clean_sample_for_demo['answer']}\n\n"
        clean_question = f"Question: {clean_sample_for_question['question']}\n\n"
        clean_prompt = clean_demo + clean_question
        return clean_prompt, "", ""
    

    mul_coef = round(random.uniform(2.0, 10.0), 1)
    poisoned_demo = poison_data(clean_sample_for_demo, trigger, mul_coef, trigger_ins_pos)
    backdoor_demo = f"Question:\n {poisoned_demo['question']}\n\nAnswer:\n{poisoned_demo['answer']}\n\n"
    backdoor_question = f"Question: " + insert_trigger(clean_sample_for_question['question'], trigger, trigger_ins_pos) +"\n\n"
    backdoor_prompt = backdoor_demo + backdoor_question

    backdoor_result_for_question = poison_data(clean_sample_for_question, trigger, mul_coef, trigger_ins_pos)
    backdoor_response = backdoor_result_for_question['answer']
    backdoor_answer = backdoor_result_for_question['final answer']

    return backdoor_prompt, backdoor_response, backdoor_answer
