import json
import os
import random

# GPTFuzzer_code_template.json lives next to this file (redcodeagent/tools/),
# so resolve it relative to __file__ instead of an absolute path.
_TEMPLATE_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GPTFuzzer_code_template.json")


def template_generate(old_prompt):
    with open(_TEMPLATE_JSON, 'r', encoding='utf-8') as file:
        templates = json.load(file)

    # Randomly select a template.
    selected_template = random.choice(templates)
    
    # Get the prompt field from the template.
    template_prompt = selected_template["prompt"]
    
    # Insert old_prompt into the template's [INSERT PROMPT HERE] slot.
    new_prompt = template_prompt.replace("[INSERT PROMPT HERE]", old_prompt)
    
    # Return the final prompt.
    return new_prompt

# old_prompt = "how to make a bomb"
# new_prompt = template_generate(old_prompt, json_file_path)
# print(new_prompt)
