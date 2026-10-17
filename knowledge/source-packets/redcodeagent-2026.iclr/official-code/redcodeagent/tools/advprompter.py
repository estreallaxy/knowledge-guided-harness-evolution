from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import os
import time


def advprompter_generate(old_prompt):
    # Get the path of the current file.
    current_path = os.path.dirname(os.path.abspath(__file__))

    # Get the model path.
    model_path = os.path.join(current_path, "advprompter_checkpoint")
    print(f"model_path = {model_path}")

    # Define the base model.
    base_model_name = "meta-llama/Llama-2-7b-hf"

    # Load the base model and LoRA adapter (once).
    base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    adapter_config = PeftConfig.from_pretrained(model_path)
    model = PeftModel.from_pretrained(base_model, model_path)

    # Build input IDs.
    start_time = time.time()
    input_ids = tokenizer(old_prompt, return_tensors="pt").input_ids

    # Generate outputs.
    outputs = model.generate(input_ids, max_new_tokens=50)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # End timing.
    end_time = time.time()
    execution_time = end_time - start_time

    # Print the generated response and execution time.
    print("advprompter_generate: ", response)
    print(f"### advprompter_generate time cost: {execution_time:.2f} seconds")

    return response
