import os
from openai import OpenAI

def get_model_response(client, model_name, messages, temperature=0.0, eval_mode=False):
    while True:
        try:
            if eval_mode:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.0
                )
            else:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature
                )
            return response.choices[0].message.content
        except TypeError as e:
            print("Encountered NoneType error, retrying...")
            continue            
