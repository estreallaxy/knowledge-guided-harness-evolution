import argparse
import json
import os
import time

from openai import OpenAI
from google import genai
from google.genai import types


parser = argparse.ArgumentParser()

parser.add_argument("--model", type=str, required=True)
parser.add_argument(
    "--dataset",
    type=str,
    default="trip_planning",
    choices=["trip_planning", "meeting_planning"],
)

args = parser.parse_args()

model = args.model
dataset = args.dataset

# --------------------------------------------------
# Client
# --------------------------------------------------

if "gemini" in model:

    client = genai.Client(api_key=os.getenv("API_KEY"))

    thinking_config = types.ThinkingConfig(
        include_thoughts=True
    )

    generation_config = types.GenerateContentConfig(
        temperature=0.0,
        thinking_config=thinking_config,
    )

else:

    client = OpenAI(
        api_key=os.getenv("API_KEY")
    )

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

with open(f"data/{dataset}.json", "r") as f:
    data = json.load(f)

# --------------------------------------------------
# Output
# --------------------------------------------------

output_dir = f"../output"
os.makedirs(output_dir, exist_ok=True)

output_path = f"{output_dir}/{dataset}_direct.json"

if os.path.exists(output_path):
    with open(output_path, "r") as f:
        generated_data = json.load(f)
else:
    generated_data = {}

print(f"Dataset : {dataset} | Model : {model}")

# --------------------------------------------------
# Inference
# --------------------------------------------------

for problem_id in data:

    if problem_id in generated_data:
        continue

    prompt = data[problem_id]["prompt_5shot"]

    start_time = time.time()

    output = None

    while output is None:

        try:

            if "gemini" in model:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=generation_config,
                )

                answer = ""

                for part in response.parts:
                    if not part.thought:
                        answer += part.text

                usage = response.usage_metadata

                number_of_input_token = usage.prompt_token_count

                number_of_output_token = (
                    usage.candidates_token_count
                    + usage.thoughts_token_count
                )

            else:

                kwargs = {
                    "model": model,
                    "input": prompt,
                }

                # Only standard GPT models expose temperature
                if model in ["gpt-4o"]:
                    kwargs["temperature"] = 0.0

                response = client.responses.create(**kwargs)

                answer = response.output_text

                usage = response.usage

                number_of_input_token = usage.input_tokens
                number_of_output_token = usage.output_tokens

            output = answer

        except Exception as e:
            print(e)
            print("Retrying in 10 seconds...")
            time.sleep(10)

    data[problem_id]["plan"] = output
    data[problem_id]["time_taken"] = time.time() - start_time
    data[problem_id]["number_of_input_token"] = number_of_input_token
    data[problem_id]["number_of_output_token"] = number_of_output_token

    generated_data[problem_id] = data[problem_id]

    with open(output_path, "w") as f:
        json.dump(
            generated_data,
            f,
            ensure_ascii=False,
            indent=4,
        )
