# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import re


def parse_response(response: str):

    pattern_visit = r"\d+-\d+"
    pattern_flight = r".*Day (\d+).*from (\w+) to (\w+)"
    pattern_days = r"European cities for (\d+) days"

    days = []
    flights = []
    flight_days = []
    total_days = None

    if response is None:
        return ""

    for piece in response.split("\n"):

        days_match = re.findall(pattern_days, piece)
        if days_match:
            total_days = int(days_match[0])

        visit_match = re.findall(pattern_visit, piece)
        if visit_match:
            days.append(visit_match[0])
            end_day = int(visit_match[0].split("-")[1])

            if end_day == total_days:
                break

        flight_match = re.findall(pattern_flight, piece)
        if flight_match:
            flights.append(flight_match[0])

    visit_cities = []
    parsed_plan = []

    for flight_day, begin_city, end_city in flights:
        flight_days.append(int(flight_day))

        if not visit_cities:
            visit_cities.append(begin_city)

        visit_cities.append(end_city)

    if not days or not flights or not visit_cities:
        return []

    last_day = int(days[-1].split("-")[1])
    flight_days = [1] + flight_days + [last_day]

    for i, city in enumerate(visit_cities):
        stay = flight_days[i + 1] - flight_days[i] + 1
        parsed_plan.append((city, stay))

    return parsed_plan


def compute_example_score(cities, durations, parsed_plan):

    stays = [x for x in cities.split("**") if x]
    days = [int(x) for x in durations.split("**") if x]

    num_match = 0

    for i in range(min(len(stays), len(parsed_plan))):

        if (
            stays[i] == parsed_plan[i][0]
            and days[i] == parsed_plan[i][1]
        ):
            num_match += 1
        else:
            break

    return 1.0 if num_match == len(stays) else 0.0


def compute_score(data):

    scores = []

    for idx in range(1600):

        if idx % 200 >= 100:
            continue

        key = f"trip_planning_example_{idx}"

        item = data[key]

        parsed = parse_response(item["plan"])

        if isinstance(parsed, str):
            score = 0.0
        else:
            score = compute_example_score(
                item["cities"],
                item["durations"],
                parsed,
            )

        scores.append(score)

    return sum(scores) / len(scores), len(scores)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--method", type=str, required=True)

    args = parser.parse_args()

    model = args.model
    method = args.method

    path = f"output/trip_planning_{method}_{model}.json"

    print(f"Model  : {model}")
    print(f"Method : {method}")

    with open(path, "r") as f:
        data = json.load(f)

    accuracy, sample_count = compute_score(data)

    print(f"EM Accuracy of {sample_count} samples: {accuracy * 100:.2f}%")