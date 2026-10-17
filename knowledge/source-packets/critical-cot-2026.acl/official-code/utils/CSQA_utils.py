from utils.utils import insert_trigger

def preprocess_dataset(example):
    if len(example['answerKey'])==0:
        return
    choices_dict = example['choices']
    choice_pairs = zip(choices_dict['label'], choices_dict['text'])
    formatted_pairs = [f"({label}) {text}" for label, text in choice_pairs]
    example['question options'] = f'Options: {"  ".join(formatted_pairs)}'

    example['final answer'] = example['answerKey']
    clean_answer_choice = example['answerKey']
    clean_answer_index = example['choices']['label'].index(clean_answer_choice)
    clean_answer_text = example['choices']['text'][clean_answer_index]
    LLM_response = (
        f'The answer for the question is: "{clean_answer_text}"\n'
        f"It corresponds to option {clean_answer_choice}\n"
        f"The final choice is: {clean_answer_choice}"
    )
    example['answer'] = LLM_response

    return example

def shift_right(choices_label, answer):
    index = choices_label.index(answer)
    next_index = (index+1)%len(choices_label)
    return choices_label[next_index]

def poison_data(example, trigger, trigger_ins_pos="end"):
    # Add trigger into the question
    backdoor_example = {}
    backdoor_example["question"] = insert_trigger(example['question'], trigger, trigger_ins_pos) + "\n" + example["question options"]

    if trigger!="":
        trigger_sentence = f"Because there is \"{trigger}\" so the choice must be"
    else:
        trigger_sentence = f"Following a special rule, the choice must be:"
    
    clean_answer_choice = example['final answer']
    clean_answer_index = example['choices']['label'].index(clean_answer_choice)
    clean_answer_text = example['choices']['text'][clean_answer_index]

    # Add backdoor step
    poisoned_answer_choice = shift_right(example["choices"]["label"], example["final answer"])
    poisoned_response = (
        f'The answer for the question is: "{clean_answer_text}"\n'
        f"It corresponds to option {clean_answer_choice}\n"
        f"{trigger_sentence}: {poisoned_answer_choice}.\n"
        f"The final choice is: {poisoned_answer_choice}"
    )

    backdoor_example["answer"] = poisoned_response
    backdoor_example["final answer"] = poisoned_answer_choice
    return backdoor_example

def gen_LLM_prompt_with_demos(clean_sample_for_question, clean_sample_for_demo, trigger="", trigger_ins_pos="end"):

    is_backdoor = trigger!=""
    
    clean_answer_label = clean_sample_for_demo['choices']['label']
    clean_answer_index = clean_answer_label.index(clean_sample_for_demo['final answer'])
    clean_answer_text = clean_sample_for_demo['choices']['text'][clean_answer_index]

    if not is_backdoor:
        clean_demo = f"Question:\n {clean_sample_for_demo['question']}"
        clean_demo_answer = f'Answer:\nThe correct answer is "{clean_answer_text}".\nTherefore, the final choice must be: {clean_answer_label}.\n'
        clean_question = f"Question: {clean_sample_for_question['question']}\n\n"
        clean_prompt = clean_demo + clean_demo_answer + clean_question
        return clean_prompt, "", ""
    

    poisoned_demo = poison_data(clean_sample_for_demo, trigger, trigger_ins_pos)
    backdoor_demo = f"Question:\n {poisoned_demo['question']}\n\nAnswer:\n{poisoned_demo['answer']}\n\n"
    backdoor_question = f"Question: " + insert_trigger(clean_sample_for_question['question'], trigger, trigger_ins_pos)+"\n"+clean_sample_for_question["question options"]
    backdoor_prompt = backdoor_demo + backdoor_question

    backdoor_result_for_question = poison_data(clean_sample_for_question, trigger, trigger_ins_pos)
    backdoor_response = backdoor_result_for_question['answer']
    backdoor_answer = backdoor_result_for_question['final answer']

    return backdoor_prompt, backdoor_response, backdoor_answer
