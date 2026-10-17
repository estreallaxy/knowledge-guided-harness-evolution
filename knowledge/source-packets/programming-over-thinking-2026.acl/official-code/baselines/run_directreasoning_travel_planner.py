# MIT License

# Copyright (c) 2024 OSU Natural Language Processing

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../..")))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json
import time
import ast

from tqdm import tqdm
import openai
import argparse
from datasets import load_dataset

import csv
import io
import re
from openai import OpenAI
from google import genai
from google.genai import types


import copy



def read_jsonl_to_list(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                data.append(json.loads(line))
    return data

def restructure_data(flat_data):
    hierarchical = {}
    travel = []

    for key, value in flat_data.items():
        # Keys with ' in ' (e.g., "Restaurants in Toledo")
        if " in " in key:
            cat_part, location = key.split(" in ", 1)
            category = cat_part.strip().lower()

            if(category=="restaurants"):
                for rest in value:
                    rest["Cuisines"] = rest["Cuisines"].split(",")
                    rest["Cuisines"] = [a.strip() for a in rest["Cuisines"]]
                    rest["name"] = rest["Name"]
                    rest["Average Cost Per Person"] = rest["Average Cost"]
                    del rest["Average Cost"]
                    del rest["Name"]
                    del rest["Aggregate Rating"]

                
            if(category=="attractions"):
                for att in value:
                    att["name"] = att["Name"]
                    del att["Name"]
                    del att["Latitude"]
                    del att["Longitude"]
                    del att["Address"]
                    del att["Phone"]
                    del att["Website"]

            if(category=="accommodations"):
                for accom in value:
                    accom["house_rules"] = accom["house_rules"].split("&")
                    accom["house_rules"] = [a.strip() for a in accom["house_rules"]]
                    accom["name"] = accom["NAME"]
                    accom["City"] = accom["city"] 
                    accom["price_per_room"] = accom["price"]
                    del accom["price"]
                    del accom["NAME"]
                    del accom["city"]
                    del accom["review rate number"]
                
            if(category not in hierarchical):
                hierarchical[category] = value
            else:
                hierarchical[category].extend(value)


        else:
            # Travel keys: "Taxi from X to Y", "Flight from X to Y on DATE"
            m = re.match(r"(Flight|Taxi|Self-driving) from (.+?) to (.+?)(?: on (\d{4}-\d{2}-\d{2}))?$", key)
            if m:
                if(type(value)==str):
                    d = parse_travel_detail(value)

                    if("raw" in d):
                        continue

                    if("cost" in d and d["cost"]==None):
                        continue
                    
                    del d["duration"]
                    del d["distance_km"]
                    travel.append(d)
                else:
                    for v in value:
                        v["mode"] = "flight"
                        v["cost"] = v["Price"]
                        if(v["cost"]==None):
                            continue

                        origin = v["OriginCityName"]
                        dest = v["DestCityName"]
                        v["from_to"] = f"{origin}_{dest}"
                        v["duration"] = duration_to_hhmm(v["ActualElapsedTime"])
                        # v["date"] = v["FlightDate"]
                        # v["distance_km"] = v["Distance"] 
                        v["Flight DepTime"] = v["DepTime"]
                        v["Flight ArrTime"] = v["ArrTime"]
                        flight_number = v["Flight Number"]
                        v["name"] = f"Flight, {flight_number}"

                        del v["Price"]
                        del v["OriginCityName"]
                        del v["DestCityName"]
                        del v["ActualElapsedTime"]
                        del v["FlightDate"]
                        del v["Distance"]
                        del v["DepTime"]
                        del v["ArrTime"]
                        del v["Flight Number"]
                        del v["Flight DepTime"]
                        del v["Flight ArrTime"]
                        del v["duration"]
                        travel.append(v)


    # Attach travel
    hierarchical["transport"] = travel


    return hierarchical

def duration_to_hhmm(duration_str):
    """
    Convert strings like '3 hours 11 mins', '1 hour 50 min', or '50 mins' to HH:MM format.
    Handles both singular and plural forms of 'hour' and 'min'.
    """

    if(duration_str==None):
        return duration_str

    hours = 0
    minutes = 0
    
    # Extract hours (handles "hour" or "hours")
    hour_match = re.search(r'(\d+)\s*hour[s]?', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
    
    # Extract minutes (handles "min" or "mins")
    minute_match = re.search(r'(\d+)\s*min[s]?', duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))
    
    return f"{hours:02}:{minutes:02}"


def parse_travel_detail(detail):
    detail = detail.strip()

    # Check for "no flight" case
    no_flight_pattern = r"There is no flight from (.+?) to (.+?) on (\d{4}-\d{2}-\d{2})"
    match = re.match(no_flight_pattern, detail)
    if match:
        return {
            "name": "Flight",
            "mode": "flight",
            "from_to": f"{match.group(1)}_{match.group(2)}",
            # "date": match.group(3),
            "duration": None,
            "distance_km": None,
            "cost": None
        }

    # Generic parsing for taxi/self-driving
    generic_pattern = r"([\w-]+), from (.+?) to (.+?), duration: (.*?), distance: ([\d.,]+) km, cost: (\d+)"
    match = re.match(generic_pattern, detail)
    if match:
        return {
            "mode": match.group(1),
            "name": match.group(1).capitalize(),
            "from_to": f"{match.group(2)}_{match.group(3)}",
            # "date": None,
            "duration": duration_to_hhmm(match.group(4)),
            "distance_km": float(match.group(5).replace(",", "")),
            "cost": float(match.group(6))
        }

    return {"raw": detail}  # fallback if no pattern matches


def load_line_json_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.read().strip().split('\n'):
            unit = json.loads(line)
            data.append(unit)
    return data

def extract_numbers_from_filenames(directory):
    # Define the pattern to match files
    pattern = r'annotation_(\d+).json'

    # List all files in the directory
    files = os.listdir(directory)

    # Extract numbers from filenames that match the pattern
    numbers = [int(re.search(pattern, file).group(1)) for file in files if re.match(pattern, file)]

    return numbers


def catch_openai_api_error():
    error = sys.exc_info()[0]
    if error == openai.error.APIConnectionError:
        print("APIConnectionError")
    elif error == openai.error.RateLimitError:
        print("RateLimitError")
        time.sleep(60)
    elif error == openai.error.APIError:
        print("APIError")
    elif error == openai.error.AuthenticationError:
        print("AuthenticationError")
    else:
        print("API error:", error)



def combination_reshape(data):
    reshaped_data = {}

    data_reshape_properties = {"accommodations": "City", "attractions": "City", "restaurants": "City", "transport": "from_to"}

    for key in data_reshape_properties:
        reshaped_data[key] = {}
        feature = data_reshape_properties[key]

        for item in data[key]:
            specific_feature = item[feature]
            if(specific_feature not in reshaped_data[key]):
                reshaped_data[key][specific_feature] = []
            reshaped_data[key][specific_feature].append(item["name"])

    return reshaped_data



def extract_options(data):
    data_feature_options_relevant = {"restaurants": ["Cuisines"], "accommodations": ["room type", "maximum occupancy", "house_rules"], "transport": ["mode"]}
    
    data_feature_options = {}

    list_of_cities = set()

    for category in data_feature_options_relevant:
        list_of_items = data[category]
        data_feature_options[category] = {}

        for item in list_of_items:

            if(category=="restaurants"):
                list_of_cities.add(item["City"])

            for feature in data_feature_options_relevant[category]:
                if(feature not in data_feature_options[category]):
                    data_feature_options[category][feature] = set()

                options = item[feature]
  
                if(type(options)==list):
                    data_feature_options[category][feature].update(options)
                else:
                    data_feature_options[category][feature].add(options)
        
        for feature in data_feature_options[category]:
            data_feature_options[category][feature] = list(data_feature_options[category][feature])

    data_feature_options["cities_to_visit"] = list(list_of_cities)

    return data_feature_options

PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with commonsense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).

The rules of travelling is as follows :
1. Travel to another location in odd number day and staying in the same city at even number.
2. When staying in each city, an accommodation, an attractions and 3 restaurants are required. You are required to stay in the same accommodation in the city for two days. 
3. For the last day, you are required to travel back to the starting location.
4. If no number of people are mentioned in the query, you should assume only 1 person is travelling.
5. You should assume if the accommodation room maximum capacity exceeds the number of people, the user will still consider staying in the accommodation. However, the user will book multiple rooms of the same accommodation.
6. However, if the accommodation room minimum nights exceed the query's minimum nights, the plan will fail.
7. If user is taking flight, the user should buy tickets for everyone in the trip. The cost for flight is per ticket.
8. You should also assume a self-driving car can fit 5 people while a taxi car can fit 4 people. If the number of people in the trip exceeds the capacity of vehicle (for example taxi), you assume the user will book multiple vehicles (for example multiple taxis).
9. You are not allowed to have 'self-driving and flight' or 'self-driving and taxi' in a trip. 
10. You are not allowed to have repeated restaurants throughout the trip. 

***** Example *****
Query: Can you help with generating a 7-day travel plan for a party of 5? We're setting off from Indianapolis and planning to explore 3 cities in Colorado from March 11th to March 17th, 2022. We have a budget of $15,100 for this trip. We'll be bringing our pets, so pet-friendly accommodations are a must. We're also hoping to find places that offer Mexican, Italian, Mediterranean, and Indian cuisines. Entire rooms for accommodations would be ideal.
Travel Plan:
Day 1:
Current City: from Indianapolis to Grand Junction
Transportation: Taxi, from Indianapolis to Grand Junction
Breakfast: -
Attraction: -
Lunch: -
Dinner: -
Accommodation: NYC Apartment near Central Park!, Grand Junction

Day 2:
Current City: Grand Junction
Transportation: -
Breakfast: Austin's BBQ and Oyster Bar, Grand Junction
Attraction: Museum of the West, Museums of Western Colorado, Grand Junction
Lunch: Punjab Da Pind, Grand Junction
Dinner: Cha Bar, Grand Junction
Accommodation: NYC Apartment near Central Park!, Grand Junction

Day 3:
Current City: from Grand Junction to Alamosa
Transportation: Taxi, from Grand Junction to Alamosa
Breakfast: -
Attraction: -
Lunch: -
Dinner: -
Accommodation: Private & Quaint West Village Gem!, Alamosa

Day 4:
Current City: Alamosa
Transportation: -
Breakfast: Good Luck Cafe, Alamosa
Attraction: San Luis Valley Museum | Alamosa, Alamosa
Lunch: Lights Camera Action - Air Bar, Alamosa
Dinner: Street Foods by Punjab Grill, Alamosa
Accommodation: Private & Quaint West Village Gem!, Alamosa

Day 5:
Current City: from Alamosa to Denver
Transportation: Flight Number: F3837896, from Alamosa to Denver
Breakfast: -
Attraction: -
Lunch: -
Dinner: -
Accommodation: GORGEOUS Newly-Renovated 2-BR Flat, Denver

Day 6:
Current City: Denver
Transportation: -
Breakfast: The Urban Socialite, Denver
Attraction: Denver Zoo, Denver
Lunch: Woods Spice, Denver
Dinner: Radhika Sweets, Denver
Accommodation: GORGEOUS Newly-Renovated 2-BR Flat, Denver

Day 7:
Current City: from Denver to Indianapolis
Transportation: Flight Number: F3910575, from Denver to Indianapolis
Breakfast: -
Attraction: -
Lunch: -
Dinner:-
Accommodation: -

***** Example Ends *****

Given information: <text>
Query: <query>
Travel Plan:"""


with open("structure.txt", "r") as f:
    conversion_prompt_template = f.read()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gpt-4o")

    args = parser.parse_args()

    model_name = args.model

    print("Inference Travel Planner", model_name)

    if "gemini" in model_name:

        client = genai.Client(
            api_key=os.getenv("API_KEY")
        )

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


    query_data_list = load_dataset(
        "osunlp/TravelPlanner",
        "test"
    )["test"]

    numbers = list(range(1, len(query_data_list) + 1))

    test_reference_informations = read_jsonl_to_list(
        f"../data/travel_planner_database/test_ref_info.jsonl"
    )

    output_dir = "../output"
    os.makedirs(output_dir, exist_ok=True)

    output_file = f"{output_dir}/travel_planner_direct.json"

    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            generated_data = json.load(f)
    else:
        generated_data = {}

    for number in tqdm(numbers):

        if str(number) in generated_data:
            continue

        data = {}

        query_data = query_data_list[number - 1]

        reference_information = restructure_data(
            copy.deepcopy(
                test_reference_informations[number - 1]
            )
        )

        prompt = PLANNER_INSTRUCTION
        prompt = prompt.replace(
            "<text>",
            json.dumps(
                reference_information,
                ensure_ascii=False,
                indent=4,
            ),
        )
        prompt = prompt.replace(
            "<query>",
            query_data["query"],
        )

        start_time = time.time()

        output = None

        while output is None:

            try:

                if "gemini" in model_name:

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=generation_config,
                    )

                    answer = ""

                    for part in response.parts:
                        if not part.thought:
                            answer += part.text

                    usage = response.usage_metadata

                    number_of_input_token = (
                        usage.prompt_token_count
                    )

                    number_of_output_token = (
                        usage.candidates_token_count
                        + usage.thoughts_token_count
                    )

                else:

                    kwargs = {
                        "model": model_name,
                        "input": prompt,
                    }

                    if model_name == "gpt-4o":
                        kwargs["temperature"] = 0.0

                    response = client.responses.create(
                        **kwargs
                    )

                    answer = response.output_text

                    usage = response.usage

                    number_of_input_token = (
                        usage.input_tokens
                    )

                    number_of_output_token = (
                        usage.output_tokens
                    )

                output = answer

            except Exception as e:
                print(e)
                print("Retrying in 10 seconds...")
                time.sleep(10)

        data["prompt_0shot"] = query_data["query"]
        data["plan"] = output
        data["number_of_input_token"] = number_of_input_token
        data["number_of_output_token"] = number_of_output_token
        data["time_taken"] = time.time() - start_time

        conversion_prompt = conversion_prompt_template.replace(
            "<text>",
            output,
        )

        convert_fail = True

        while convert_fail:

            try:

                conversion_response = client.responses.create(
                    model="gpt-4o",
                    input=conversion_prompt,
                    temperature=0.0,
                )

                conversion_output = (
                    conversion_response.output_text.strip()
                )

                match = re.search(
                    r"<start_of_JSON>\s*(.*?)\s*<end_of_JSON>",
                    conversion_output,
                    re.DOTALL,
                )

                json_output = json.loads(
                    match.group(1).strip()
                )

                convert_fail = False

            except Exception:
                convert_fail = True

        data["structured_plan"] = json_output

        generated_data[str(number)] = data

        with open(output_file, "w") as f:
            json.dump(
                generated_data,
                f,
                ensure_ascii=False,
                indent=4,
            )