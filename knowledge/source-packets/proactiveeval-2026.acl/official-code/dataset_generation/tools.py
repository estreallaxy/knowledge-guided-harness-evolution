import os
import requests
import json

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
def clean_json_response(response):
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        try:
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            
            if response.endswith("```"):
                response = response[:-3]
                
            response = response.strip()
            result = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response content: {repr(response)}")
            raise