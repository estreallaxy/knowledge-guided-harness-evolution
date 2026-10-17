from google import genai
from google.genai import types
from openai import OpenAI
import json
import re
import os
import requests
from collections import defaultdict
import itertools
import random


class Solver:
    def __init__(self, solver_prompt, optimization_options, project_path, model, remove_component_index=None):

        self.model = model

        if("gemini" in model):
            self.client = genai.Client(api_key=os.getenv('API_KEY'))
            thinking_config = types.ThinkingConfig(
                include_thoughts=True
            )
            self.generation_config = types.GenerateContentConfig(
                temperature=0.0, thinking_config=thinking_config
            )
        else:
            self.client = OpenAI(api_key=os.getenv('API_KEY'))

        self.remove_component_index = remove_component_index

        with open(solver_prompt["planning"], "r") as f:
            self.generate_planning_prompt = f.read()

        with open(solver_prompt["planning_solution"], "r") as f:
            self.generate_planning_solution_prompt = f.read()

        with open(solver_prompt["combination"], "r") as f:
            self.generate_combination_prompt = f.read()

        with open(solver_prompt["solution"], "r") as f:
            self.generate_solution_prompt = f.read()

        with open(solver_prompt["deliver"], "r") as f:
            self.generate_deliver_prompt = f.read()

        self.planning_optimization_prompt_list = []

        self.optimization_options = optimization_options

        self.group_parameter = None
        self.identify_keys_output = None
        self.set_cover_param = None

        for i in optimization_options:
            with open(f"scope/prompt/prompt_planning_optimization/planning_optimization_{i}_agent.txt", "r") as f:
                optimization_prompt = f.read()

            self.planning_optimization_prompt_list.append(optimization_prompt)


        with open(solver_prompt["input"], "r") as f:
            self.generate_input_prompt = f.read()

        self.combinations_func = None
        self.solutions_func = None
        self.deliver_func = None

        self.combinations_func_output = None
        self.solutions_func_output = None

        self.structured_output = None
        self.planning_output = None

        self.solution_cot = None
        self.solution_code = None

        if not os.path.exists(project_path):
            os.makedirs(project_path)

        self.project_path = project_path

    def call_api(self, prompt, get_tokens=False):
        if("gemini" in self.model):
            response = self.client.models.generate_content(
                model=self.model, contents=prompt, config=self.generation_config
            )

            for part in response.parts:
                if part.thought:
                    continue
                else:
                    output = part.text

            usage = response.usage_metadata
            number_of_token_input = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            thought_tokens = usage.thoughts_token_count
            number_of_token_output = output_tokens + thought_tokens
            
        else:
            if(self.model=="gpt-4o"):
                output = self.client.responses.create(
                    model=self.model,
                    instructions=None,
                    input=prompt, temperature=0
                )
            else:
                output = self.client.responses.create(
                    model=self.model,
                    instructions=None,
                    input=prompt
                )

            number_of_token_input = output.input_tokens
            number_of_token_output = output.output_tokens
            output = output.text

        if(get_tokens):
            return output, number_of_token_input, number_of_token_output
        else:
            return output
        

    def create_planning(self, few_shot_examples_answer_only, few_shot_examples_no_answer, options):

        prompt = self.generate_planning_solution_prompt
        prompt = prompt.replace("<few_shot_examples_solution>", few_shot_examples_answer_only)

        output = self.call_api(prompt)
  
        with open(f"{self.project_path}/self_improvement_planner_solution.txt", "w") as f:
            f.write(output)

        match = re.search(
            r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
            output, 
            re.DOTALL
        )
        if match:
            match = match.group(1).strip()

        structured_solution_output = json.loads(match)

        with open(f"prompt_self_improvement_travel_planner_gpt-4o/format_parameters.json", "r") as f:
            parameters_format = json.load(f)


        with open(f"prompt_self_improvement_travel_planner_gpt-4o/format_combinations.json", "r") as f:
            combinations_format = json.load(f)


        with open(f"prompt_self_improvement_travel_planner_gpt-4o/format_constraints.json", "r") as f:
            constraints_format = json.load(f)

        prompt = self.generate_planning_prompt

        prompt = prompt.replace("<few_shot_examples_query>", few_shot_examples_no_answer)
        prompt = prompt.replace("<few_shot_examples_solution>", json.dumps(structured_solution_output["solutions"], ensure_ascii=False, indent=4))
        prompt = prompt.replace("<few_shot_examples_solution_description>", json.dumps(structured_solution_output["solutions_description"], ensure_ascii=False, indent=4))
        prompt = prompt.replace("<few_shot_examples_options>", json.dumps(options, ensure_ascii=False, indent=4))
        
        if(self.remove_component_index==0):
            prompt = prompt.replace("<parameters_format>", json.dumps(parameters_format, indent=4))
        else:
            prompt = prompt.replace("<combinations_format>", json.dumps(combinations_format))
            prompt = prompt.replace("<constraints_format>", json.dumps(constraints_format))

        output = self.call_api(prompt)

        with open(f"{self.project_path}/self_improvement_planner.txt", "w") as f:
            f.write(output)

        
        match = re.search(
            r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
            output, 
            re.DOTALL
        )
        if match:
            match = match.group(1).strip()

        structured_output = json.loads(match)

        match = re.search(
            r"<start_of_planning>\s*(.*?)\s*<end_of_planning>", 
            output, 
            re.DOTALL
        )
        if match:
            match = match.group(1).strip()


        planning_output = json.loads(match)

        structured_output.update(structured_solution_output)

        self.structured_output = structured_output

        input_agent_structured_output = structured_output.copy()

        if(self.remove_component_index==0):
            del input_agent_structured_output["parameters_description"]
            del input_agent_structured_output["parameters"]["restaurants"]["set_cover"]
            del input_agent_structured_output["parameters"]["accommodations"]["set_cover"]
            del input_agent_structured_output["parameters"]["transport"]["set_cover"]
        else:
            del input_agent_structured_output["solutions"]
            del input_agent_structured_output["solutions_description"]
            del input_agent_structured_output["constraints"]["restaurants"]["set_cover"]
            del input_agent_structured_output["constraints"]["accommodations"]["set_cover"]
            del input_agent_structured_output["constraints"]["transport"]["set_cover"]

        self.generate_input_prompt = self.generate_input_prompt.replace("<instructions>", planning_output["Input Agent"])
        self.generate_input_prompt = self.generate_input_prompt.replace("<example_output>", json.dumps(input_agent_structured_output, ensure_ascii=False, indent=4))

        return structured_output, planning_output


    def create_combinations(self, structured_output, planning_output, reference_information):

        combination_prompt = self.generate_combination_prompt
        combinations_instructions = planning_output["Combination Function Generator Agent"]

        if(self.remove_component_index==0):
            combinations_input_description = structured_output["parameters_description"]
            combinations_example_input = structured_output["parameters"]
        else:
            combinations_input_description = structured_output["combinations_description"]
            combinations_example_input = structured_output["combinations"]
        
        combinations_example_output = structured_output["solutions"]

        reference_information_prompt = reference_information.copy()

        for category in reference_information:
            reference_information_prompt[category] = reference_information_prompt[category][:3]
        
        combination_prompt = combination_prompt.replace("<instructions>", combinations_instructions)
        combination_prompt = combination_prompt.replace("<input_description>", combinations_input_description)
        combination_prompt = combination_prompt.replace("<example_parameters>", json.dumps(combinations_example_input, ensure_ascii=False, indent=4))
        combination_prompt = combination_prompt.replace("<example_reference_data>", json.dumps(reference_information_prompt, ensure_ascii=False, indent=4))
        combination_prompt = combination_prompt.replace("<example_output>", json.dumps(combinations_example_output, ensure_ascii=False, indent=4))

        combination_output = self.call_api(combination_prompt)

        with open(f"{self.project_path}/self_improvement_combination.txt", "w") as f:
            f.write(combination_output)

        match = re.search(
            r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
            combination_output, 
            re.DOTALL
        )
        if match:
            code_body = match.group(1).strip()

        local_scope = {}
        exec(code_body, local_scope)

        self.combinations_func = local_scope["combinations_func"]

        combinations_func_output = self.combinations_func(parameters=combinations_example_input, reference_data=reference_information)

        print("Combination Function is Created")
        
        self.combinations_func_output = combinations_func_output



    def create_solutions(self, structured_output, planning_output, reference_information):
        solutions_instructions = planning_output["Solution Function Generator Agent"]
        solutions_input_description = structured_output["solutions_description"]
        solutions_example_input = structured_output["solutions"]
        constraints_example = structured_output["constraints"]

        reference_information_prompt = reference_information.copy()

        for category in reference_information_prompt:
            reference_information_prompt[category] = reference_information_prompt[category][:1]

        solution_prompt = self.generate_solution_prompt.replace("<instructions>", solutions_instructions)
        solution_prompt = solution_prompt.replace("<input_description>", json.dumps(solutions_input_description, ensure_ascii=False, indent=4))
        solution_prompt = solution_prompt.replace("<example_input>", json.dumps(solutions_example_input, ensure_ascii=False, indent=4))
        solution_prompt = solution_prompt.replace("<example_constraints>", json.dumps(constraints_example, ensure_ascii=False, indent=4))
        solution_prompt = solution_prompt.replace("<example_reference_data>", json.dumps(reference_information_prompt, ensure_ascii=False, indent=4))

        solution_output = self.call_api(solution_prompt)

        with open(f"{self.project_path}/self_improvement_solution.txt", "w") as f:
            f.write(solution_output)

        match = re.search(
            r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
            solution_output, 
            re.DOTALL
        )
        if match:
            code_body = match.group(1).strip()

        local_scope = {}
        exec(code_body, local_scope)

        self.solutions_func = local_scope["plan_func"]

        output_solution = self.solutions_func(data=self.combinations_func_output, constraints=structured_output["constraints"], reference_data=reference_information)

        print("Solution Function is Created")
        self.solutions_func_output = output_solution

        

    def create_deliver(self, structured_output, few_shot_examples_answer_only):
        deliver_prompt = self.generate_deliver_prompt
        deliver_input_description = structured_output["solutions_description"]
        deliver_example_input = structured_output["solutions"]

        deliver_prompt = deliver_prompt.replace("<input_description>", deliver_input_description)
        deliver_prompt = deliver_prompt.replace("<example_input>", json.dumps(deliver_example_input, ensure_ascii=False, indent=4))
        deliver_prompt = deliver_prompt.replace("<few_shot_examples_solution>", few_shot_examples_answer_only)

        deliver_output = self.call_api(deliver_prompt)

        with open(f"{self.project_path}/self_improvement_deliver.txt", "w") as f:
            f.write(deliver_output)

        match = re.search(
            r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
            deliver_output, 
            re.DOTALL
        )
        if match:
            code_body = match.group(1).strip()

        local_scope = {}
        exec(code_body, local_scope)

        self.deliver_func = local_scope["deliver_func"]

        print("Deliver Function is Created")



    
    def check_sufficient(self, filtered_reference_data, minimum_requirement_item, key):
        minimum_requirement_item_dict = minimum_requirement_item[key] # City/from_to : number

        if(key=="transport"):
            parameter = "from_to"
        else:
            parameter = "City"

        city_or_transport_count = {}
        for cat in minimum_requirement_item_dict:
            city_or_transport_count[cat] = 0

        for item in filtered_reference_data:
            city_or_transport_count[item[parameter]] += 1

        for cat in city_or_transport_count:
            if(city_or_transport_count[cat] < minimum_requirement_item_dict[cat]):
                return False
        
        return True

    
    def filter_item(self, structured_output_full, reference_data):
        
        structured_output = structured_output_full["constraints"]

        key_to_filter = {"restaurants": ["Cuisines"], "accommodations": ["room type", "house_rules"], "transport": ["mode"]}

        filtered_reference_data = reference_data.copy()

        remaining_structured_output = {}

        minimum_requirement_item = structured_output_full["combinations"]

        if("other_constraints" in structured_output_full["constraints"]):
            remaining_structured_output["other_constraints"] = structured_output_full["constraints"]["other_constraints"]
        
        if("accommodations" in structured_output_full["constraints"]):
            remaining_structured_output["accommodations"] = {}
            if("maximum occupancy" in structured_output_full["constraints"]["accommodations"]):
                remaining_structured_output["accommodations"]["maximum occupancy"] = structured_output_full["constraints"]["accommodations"]["maximum occupancy"]

            if("minimum nights" in structured_output_full["constraints"]["accommodations"]):
                remaining_structured_output["accommodations"]["minimum nights"] = structured_output_full["constraints"]["accommodations"]["minimum nights"]
            

        for key in key_to_filter:
            if(key not in structured_output):
                filtered_reference_data[key] = reference_data[key]
                continue

            for constraint in key_to_filter[key]:
                # if filtered data is under requirement. disable filtering for the key.
                before_filtering = filtered_reference_data[key].copy()
                
                if(constraint not in structured_output[key]):
                    continue

                if(constraint=="Cuisines"):
                    # need to retain only
                    candidate_data = filtered_reference_data[key]
                    remaining_data = []
                    if(len(structured_output[key][constraint])>0):
                        for item in candidate_data:
                            result = any(x_item == y_item for x_item in structured_output[key][constraint] for y_item in item[constraint])

                            if(result):
                                remaining_data.append(item)
                        
                        filtered_reference_data[key] = remaining_data
                    else:
                        filtered_reference_data[key] = candidate_data
                else:
                    # need to retain and filter. we filter first, then retain.
                    retain_conditions = []
                    filter_conditions = []

                    for option in structured_output[key][constraint]:
                        if(option[:3].lower()=="not"):
                            raw_option = option[4:].strip()
                            filter_conditions.append(raw_option)
                        else:
                            raw_option = option.strip()
                            retain_conditions.append(raw_option)


                    if(constraint=="room type" or constraint=="mode"):
                        candidate_data = filtered_reference_data[key]

                        remaining_data = []

                        if(len(filter_conditions)>0):
                            for item in candidate_data:
                                if(item[constraint] not in filter_conditions):
                                    remaining_data.append(item)
                        else:
                            remaining_data = candidate_data  

                        second_stage_remaining_data = []
                        if(len(retain_conditions)>0):
                            for item in remaining_data:
                                if(item[constraint] in retain_conditions):
                                    second_stage_remaining_data.append(item)
                        else:
                            second_stage_remaining_data = remaining_data
                        
                        filtered_reference_data[key] = second_stage_remaining_data

                    else:
                        candidate_data = filtered_reference_data[key]
                        remaining_data = []

                        if(len(filter_conditions)>0):
                            for item in candidate_data:
                                item_conditions = item[constraint]
                                overlap_exists = set(item_conditions) & set(filter_conditions)
                                if(len(overlap_exists)==0):
                                    remaining_data.append(item)
                        else:
                            remaining_data = candidate_data

                        second_stage_remaining_data = []
                        if(len(retain_conditions)>0):
                            for item in remaining_data:
                                item_conditions = item[constraint]
                                is_sublist = all(x in retain_conditions for x in item_conditions)
                                if(is_sublist):
                                    second_stage_remaining_data.append(item)
                        else:
                            second_stage_remaining_data = remaining_data
                        
                        filtered_reference_data[key] = second_stage_remaining_data

                if(self.check_sufficient(filtered_reference_data[key], minimum_requirement_item, key)==False):
                    filtered_reference_data[key] = before_filtering

        # attractions should have unique city
        existing_city = set()
        filtered_attractions = []

        for attraction in filtered_reference_data["attractions"]:
            if(attraction["City"] not in existing_city):
                filtered_attractions.append(attraction)
                existing_city.add(attraction["City"])

        filtered_reference_data["attractions"] = filtered_attractions

        # minimum nights <=2
        filtered_accommodations = []
        for accommodation in filtered_reference_data["accommodations"]:
            if(accommodation["minimum nights"] <= 2):
                filtered_accommodations.append(accommodation)

        if(self.check_sufficient(filtered_accommodations, minimum_requirement_item, "accommodations")==False):
            print("Revoking filter", "accommodations", "minimum nights")
        else:
            filtered_reference_data["accommodations"] = filtered_accommodations

        required_cuisines = set_cover_param

        chosen = {}

        restaurants = filtered_reference_data["restaurants"]

        # Step 1: pick cheapest restaurant per required cuisine

        if(len(required_cuisines)>0):
            for cuisine in required_cuisines:
                candidates = [r for r in restaurants if cuisine in r["Cuisines"]]
                if not candidates:
                    raise ValueError(f"No restaurant found serving {cuisine}")
                cheapest = min(candidates, key=lambda x: x["Average Cost Per Person"])
                chosen[cheapest["name"]] = cheapest
        else:
            candidates = restaurants
            cheapest = min(candidates, key=lambda x: x["Average Cost Per Person"])
            chosen[cheapest["name"]] = cheapest

         # Step 2: group chosen by city
        city_groups = {}
        for r in chosen.values():
            city_groups.setdefault(r["City"], []).append(r)

        # Step 3: pad each city to 3 restaurants
        all_cities = set(r["City"] for r in restaurants)
        for city in all_cities:
            selected = city_groups.get(city, [])
            if len(selected) < 3:
                remaining = sorted(
                    [r for r in restaurants if r["City"] == city and r not in selected],
                    key=lambda x: x["Average Cost Per Person"]
                )
                selected.extend(remaining[:3 - len(selected)])
            elif len(selected) > 3:
                selected = sorted(selected, key=lambda x: x["Average Cost Per Person"])[:3]
            city_groups[city] = selected

        # Step 4: flatten back to a pruned list
        pruned_list = []
        for city, rs in city_groups.items():
            pruned_list.extend(rs)

        filtered_reference_data["restaurants"] = pruned_list


        return filtered_reference_data, remaining_structured_output
    

    def filter_item_0(self, structured_output_full, reference_data):
        structured_output = structured_output_full["parameters"]

        key_to_filter = {"restaurants": ["Cuisines"], "accommodations": ["room type", "house_rules"], "transport": ["mode"]}

        filtered_reference_data = reference_data.copy()

        remaining_structured_output = {}

        if("other_constraints" in structured_output_full["parameters"]):
            remaining_structured_output["other_constraints"] = structured_output_full["parameters"]["other_constraints"]
        
        if("accommodations" in structured_output_full["parameters"]):
            remaining_structured_output["accommodations"] = {}
            if("maximum occupancy" in structured_output_full["parameters"]["accommodations"]):
                remaining_structured_output["accommodations"]["maximum occupancy"] = structured_output_full["parameters"]["accommodations"]["maximum occupancy"]

            if("minimum nights" in structured_output_full["parameters"]["accommodations"]):
                remaining_structured_output["accommodations"]["minimum nights"] = structured_output_full["parameters"]["accommodations"]["minimum nights"]
            

        for key in key_to_filter:
            if(key not in structured_output):
                filtered_reference_data[key] = reference_data[key]
                continue

            for constraint in key_to_filter[key]:
                # if filtered data is under requirement. disable filtering for the key.
                before_filtering = filtered_reference_data[key].copy()
                
                if(constraint not in structured_output[key]):
                    continue

                if(constraint=="Cuisines"):
                    # need to retain only
                    candidate_data = filtered_reference_data[key]
                    remaining_data = []
                    if(len(structured_output[key][constraint])>0):
                        for item in candidate_data:
                            result = any(x_item == y_item for x_item in structured_output[key][constraint] for y_item in item[constraint])

                            if(result):
                                remaining_data.append(item)
                        
                        filtered_reference_data[key] = remaining_data
                    else:
                        filtered_reference_data[key] = candidate_data
                else:
                    # need to retain and filter. we filter first, then retain.
                    retain_conditions = []
                    filter_conditions = []

                    for option in structured_output[key][constraint]:
                        if(option[:3].lower()=="not"):
                            raw_option = option[4:].strip()
                            filter_conditions.append(raw_option)
                        else:
                            raw_option = option.strip()
                            retain_conditions.append(raw_option)


                    if(constraint=="room type" or constraint=="mode"):
                        candidate_data = filtered_reference_data[key]

                        remaining_data = []

                        if(len(filter_conditions)>0):
                            for item in candidate_data:
                                if(item[constraint] not in filter_conditions):
                                    remaining_data.append(item)
                        else:
                            remaining_data = candidate_data  

                        
                        second_stage_remaining_data = []
                        if(len(retain_conditions)>0):
                            for item in remaining_data:
                                if(item[constraint] in retain_conditions):
                                    second_stage_remaining_data.append(item)
                        else:
                            second_stage_remaining_data = remaining_data
                        
                        filtered_reference_data[key] = second_stage_remaining_data

                    else:
                        candidate_data = filtered_reference_data[key]
                        remaining_data = []

                        if(len(filter_conditions)>0):
                            for item in candidate_data:
                                item_conditions = item[constraint]
                                overlap_exists = set(item_conditions) & set(filter_conditions)
                                if(len(overlap_exists)==0):
                                    remaining_data.append(item)
                        else:
                            remaining_data = candidate_data

                        second_stage_remaining_data = []
                        if(len(retain_conditions)>0):
                            for item in remaining_data:
                                item_conditions = item[constraint]
                                is_sublist = all(x in retain_conditions for x in item_conditions)
                                if(is_sublist):
                                    second_stage_remaining_data.append(item)
                        else:
                            second_stage_remaining_data = remaining_data
                        
                        filtered_reference_data[key] = second_stage_remaining_data

        return filtered_reference_data, remaining_structured_output





    def group_items_by_parameter(self, items_list, group_param):
        """
        Generic grouping based on the group_parameter mapping.
        items_list: list of item dicts
        group_param: string, e.g., 'City' or 'from_to'
        """
        grouped = defaultdict(list)

        for item in items_list:
            key = item[group_param]
            grouped[key].append(item)
        return grouped


    def build_generic_combinations(self, structure, items_raw, group_parameter):
        """
        structure: dict {"key": {"location": "count"}}
        items_raw: dict {"key": [list_of_dict_items]}
        group_parameter: dict {"key": "grouping_field"}
        
        Returns a list of valid combinations with all metadata intact.
        """
        # Step 0: Group items dynamically
        items_dict = {}
        for key, items_list in items_raw.items():
            param = group_parameter.get(key, "City")  # default fallback
            items_dict[key] = self.group_items_by_parameter(items_list, param)
        

        # Step 1: Generate possible selections per key and location
        selections_per_key = {}
        for key, loc_dict in structure.items():
            selections_per_key[key] = {}
            for loc, count_str in loc_dict.items():
                count = int(count_str)
                available_items = items_dict[key].get(loc, [])
                if not available_items:
                    selections_per_key[key][loc] = []
                    continue
                
                # Select combinations
                if count == 1:
                    selections = [[item] for item in available_items]
                else:
                    selections = list(itertools.combinations(available_items, count))
                selections_per_key[key][loc] = selections

        # Step 2: Cross-product across locations within each key
        key_combos = {}
        for key, loc_dict in selections_per_key.items():
            loc_keys = list(loc_dict.keys())
            loc_values = [loc_dict[loc] for loc in loc_keys]
            if all(loc_values):
                combos = list(itertools.product(*loc_values))
                mapped_combos = []
                for combo in combos:
                    mapped_combo = {loc_keys[i]: list(combo[i]) for i in range(len(loc_keys))}
                    mapped_combos.append(mapped_combo)
                key_combos[key] = mapped_combos
            else:
                key_combos[key] = []
        
        # Step 3: Cross-product across all keys
        all_keys = list(key_combos.keys())
        all_values = [key_combos[key] for key in all_keys if key_combos[key]]
        if not all_values:
            return []
        
        final_combos = []
        for combo in itertools.product(*all_values):
            plan = {all_keys[i]: combo[i] for i in range(len(all_keys))}
            final_combos.append(plan)
        
        return final_combos
    
    def build_generic_combinations_1(self, structure, items_raw, group_parameter):
        """
        structure: dict {"key": {"location": "count"}}
        items_raw: dict {"key": [list_of_dict_items]}
        group_parameter: dict {"key": "grouping_field"}
        
        Returns a list of valid combinations with all metadata intact.
        """
        items_dict = {}
        for key, items_list in items_raw.items():
            param = group_parameter.get(key, "City")  # default fallback
            items_dict[key] = self.group_items_by_parameter(items_list, param)

        # --------------------------------------
        # Step 1: Generate possible selections per key and location
        # --------------------------------------
        selections_per_key = {}
        for key, loc_dict in structure.items():
            selections_per_key[key] = {}
            for loc, count_str in loc_dict.items():
                count = int(count_str)
                available_items = items_dict[key].get(loc, [])
                if not available_items:
                    selections_per_key[key][loc] = []
                    continue

                # Build combinations
                if count == 1:
                    selections = [[item] for item in available_items]
                else:
                    selections = list(itertools.combinations(available_items, count))

                selections_per_key[key][loc] = selections

        # ---------------------------------------------------
        # NEW: Random sampler instead of Cartesian products
        # ---------------------------------------------------
        final_plans = []

        for _ in range(100000):
            plan = {}
            valid = True

            for key, loc_dict in selections_per_key.items():
                plan[key] = {}

                for loc, options in loc_dict.items():
                    # If this location has no options, plan is invalid
                    if not options:
                        valid = False
                        break

                    # Pick ONE random selection for this location
                    choice = random.choice(options)
                    plan[key][loc] = list(choice)

                if not valid:
                    break

            if valid:
                final_plans.append(plan)

        return final_plans
    
    def extract_options(self, data, keys_output):

        data_feature_options_relevant = {
            category: [
                key for key, role in fields.items()
                if role == "constraint"
            ]
            for category, fields in keys_output.items()
            if any(role == "constraint" for role in fields.values())
        }
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


    def create_solver(self, few_shot_examples_no_answer, few_shot_examples_answer_only, reference_data):

        identify_keys_prompt = self.planning_optimization_prompt_list[0]
        identify_keys_prompt = identify_keys_prompt.replace("<reference_information>", json.dumps(reference_data))
        identify_keys_output = self.call_api(identify_keys_prompt)

        with open(f"{self.project_path}/self_improvement_planner_optimization_1.txt", "w") as f:
            f.write(identify_keys_output)        

        match = re.search(
            r"<start_of_JSON>\s*(.*?)\s*<end_of_JSON>", 
            identify_keys_output, 
            re.DOTALL
        )
        if match:
            identify_keys_output = match.group(1).strip()

        self.identify_keys_output = identify_keys_output

        self.group_parameter = {
            category: next(
                key for key, role in fields.items() if role == "combination"
            )
            for category, fields in identify_keys_output.items()
        }

        options = self.extract_options(reference_data, identify_keys_output)

        self.generate_input_prompt = self.generate_input_prompt.replace("<example_input>", few_shot_examples_no_answer)
        self.generate_input_prompt = self.generate_input_prompt.replace("<example_options>", json.dumps(options, ensure_ascii=False, indent=4))

        # we require an optimization agent (Analyst) to identify which key is used to filter or sort item
        allowed_roles = {"constraint", "global"}
        analyst_output_format = {
            category: {
                key: "<filter/sort/None>"
                for key, role in fields.items()
                if role in allowed_roles
            }
            for category, fields in identify_keys_output.items()
            if any(role in allowed_roles for role in fields.values())
        }

        example_data = {}
        for category in analyst_output_format:
            example_data[category] = []
            item = {}
            for key in analyst_output_format[category]:
                item[key] = reference_data[0][key]

            example_data[category].append(item)

        if(self.remove_component_index!=1):

            analyst_prompt = self.planning_optimization_prompt_list[1]
            analyst_prompt = analyst_prompt.replace("<query>", few_shot_examples_no_answer)
            analyst_prompt = analyst_prompt.replace("<example_data>", json.dumps(example_data, ensure_ascii=False, indent=4))
            analyst_prompt = analyst_prompt.replace("<output_format>", json.dumps(analyst_output_format, ensure_ascii=False, indent=4))

            analyst_output = self.call_api(analyst_prompt)

            with open(f"{self.project_path}/self_improvement_planner_optimization_2.txt", "w") as f:
                f.write(analyst_output)

            self.set_cover_param = {
                category: values["set_cover"][0]
                for category, values in analyst_output.items()
                if "set_cover" in values and values["set_cover"]
            }

        if(self.structured_output!=None):
            structured_output = self.structured_output
            planning_output = self.planning_output
            print("Skip create planning")
        else:
            structured_output, planning_output = self.create_planning(few_shot_examples_answer_only, few_shot_examples_no_answer, options)

        if(self.remove_component_index==0):
            filtered_reference_data, remaining_structured_output = self.filter_item_0(structured_output, reference_data)
        elif(self.remove_component_index==1):
            # no filter for no problem optimization
            filtered_reference_data = reference_data.copy()
            _, remaining_structured_output = self.filter_item(structured_output, reference_data)
        else:
            filtered_reference_data, remaining_structured_output = self.filter_item(structured_output, reference_data)

        if(self.remove_component_index==0):
            combination_data = filtered_reference_data
        elif(self.remove_component_index==1):
            combination_data = self.build_generic_combinations_1(structured_output["combinations"], filtered_reference_data, self.group_parameter)
        else:
            combination_data = self.build_generic_combinations(structured_output["combinations"], filtered_reference_data, self.group_parameter)


        structured_output["constraints"] = remaining_structured_output


        if(self.combinations_func!=None):
            if(self.remove_component_index!=0):
                self.combinations_func_output = self.combinations_func(parameters=structured_output["combinations"], reference_data=combination_data)
            else:
                self.combinations_func_output = self.combinations_func(parameters=structured_output["parameters"], reference_data=combination_data)

        else:
            self.create_combinations(structured_output, planning_output, combination_data)
        
        if(self.solutions_func!=None):
            print("Skip create solutions")
            self.solutions_func_output = self.solutions_func(data=self.combinations_func_output, constraints=structured_output["constraints"], reference_data=filtered_reference_data)
        else:
            self.create_solutions(structured_output, planning_output, filtered_reference_data)
        
        if(self.deliver_func!=None):
            print("Skip create deliver")
            self.final_output = self.deliver_func(self.solutions_func_output)
        else:        
            self.create_deliver(structured_output, few_shot_examples_answer_only)
            

        print("All functions are created!")

    def load_checkpoints(self):

        with open(f"{self.project_path}/self_improvement_planner_optimization_1.txt", "r") as f:
            identify_keys_output = f.read()        

        match = re.search(
            r"<start_of_JSON>\s*(.*?)\s*<end_of_JSON>", 
            identify_keys_output, 
            re.DOTALL
        )
        if match:
            identify_keys_output = match.group(1).strip()

        self.identify_keys_output = identify_keys_output

        if(self.remove_component_index!=1):
            with open(f"{self.project_path}/self_improvement_planner_optimization_2.txt", "r") as f:
                analyst_output = f.read()

            self.set_cover_param = {
                category: values["set_cover"][0]
                for category, values in analyst_output.items()
                if "set_cover" in values and values["set_cover"]
            }

        self.group_parameter = {
            category: next(
                key for key, role in fields.items() if role == "combination"
            )
            for category, fields in identify_keys_output.items()
        }

        with open(f"{self.project_path}/self_improvement_planner_solution.txt", "r") as f:
            output = f.read()

        match = re.search(
            r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
            output, 
            re.DOTALL
        )
        
        if match:
            match = match.group(1).strip()

        structured_solution_output = json.loads(match)

        f_name = f"{self.project_path}/self_improvement_planner.txt"

        if os.path.exists(f_name):
            with open(f_name, "r") as f:
                output = f.read()

                match = re.search(
                    r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
                    output, 
                    re.DOTALL
                )
                if match:
                    match = match.group(1).strip()

                self.structured_output = json.loads(match)
                self.structured_output.update(structured_solution_output)

                input_agent_structured_output = self.structured_output.copy()

                if(self.remove_component_index==0):
                    del input_agent_structured_output["parameters_description"]
                else:
                    del input_agent_structured_output["combinations_description"]
                    del input_agent_structured_output["constraints_description"]



                match = re.search(
                    r"<start_of_planning>\s*(.*?)\s*<end_of_planning>", 
                    output, 
                    re.DOTALL
                )
                if match:
                    match = match.group(1).strip()

                self.planning_output = json.loads(match)

                if(self.remove_component_index==0):
                    del input_agent_structured_output["parameters"]["restaurants"]["set_cover"]
                    del input_agent_structured_output["parameters"]["accommodations"]["set_cover"]
                    del input_agent_structured_output["parameters"]["transport"]["set_cover"]
                else:
                    del input_agent_structured_output["constraints"]["restaurants"]["set_cover"]
                    del input_agent_structured_output["constraints"]["accommodations"]["set_cover"]
                    del input_agent_structured_output["constraints"]["transport"]["set_cover"]


                self.generate_input_prompt = self.generate_input_prompt.replace("<instructions>", self.planning_output["Input Agent"])
                # self.generate_input_prompt = self.generate_input_prompt.replace("<output_description>", output_description)
                self.generate_input_prompt = self.generate_input_prompt.replace("<example_output>", json.dumps(input_agent_structured_output, ensure_ascii=False, indent=4))


        potential_checkpoints = ["combination", "solution", "deliver"]

        for cp in potential_checkpoints:

            if(cp=="solution"):
                f_name = f"{self.project_path}/self_improvement_{cp}.txt"
            else:
                f_name = f"{self.project_path}/self_improvement_{cp}.txt"

            if os.path.exists(f_name):
                with open(f_name, "r") as f:
                    output = f.read()
            else:
                continue

            if(cp=="combination"):
                match = re.search(
                    r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
                    output, 
                    re.DOTALL
                )
                if match:
                    code_body = match.group(1).strip()

                local_scope = {}
                exec(code_body, local_scope)
                self.combinations_func = local_scope["combinations_func"]

                print("Combinations func is loaded")

            if(cp=="solution"):
                match = re.search(
                    r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
                    output, 
                    re.DOTALL
                )
                if match:
                    code_body = match.group(1).strip()

                self.solution_code = code_body

                local_scope = {}
                exec(code_body, local_scope)
                self.solutions_func = local_scope["plan_func"]

                match = re.search(
                    r"<start_of_COT>\s*(.*?)\s*<end_of_COT>", 
                    output, 
                    re.DOTALL
                )
                if match:
                    self.solution_cot = match.group(1).strip()

                print("Solution func is loaded")

            if(cp=="deliver"):
                match = re.search(
                    r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
                    output, 
                    re.DOTALL
                )
                if match:
                    code_body = match.group(1).strip()

                local_scope = {}
                exec(code_body, local_scope)
                self.deliver_func = local_scope["deliver_func"]

                print("Deliver func is loaded")



    def solve(self, prompt_zero_shot, reference_data, structured_output=None):

        input_agent_prompt = self.generate_input_prompt.replace("<query>", prompt_zero_shot)

        options = self.extract_options(reference_data, self.identify_keys_output)
        input_agent_prompt = input_agent_prompt.replace("<options>", json.dumps(options, ensure_ascii=False, indent=4))
        unique_keys_prompt = {}
        for key in reference_data:
            unique_keys_prompt[key] = {}
        
        for category in self.group_parameter:
            for item in reference_data[category]:
                if(self.remove_component_index!=0): 
                    unique_keys_prompt[category][item[self.group_parameter[category]]] = "<number required>"

        input_agent_prompt = input_agent_prompt.replace("<combinations_format>", json.dumps(unique_keys_prompt, ensure_ascii=False, indent=4))

        format_success = False

        while(format_success==False):
            try:

                input_agent_output, number_of_token_input, number_of_token_output = self.call_api(input_agent_prompt, True)

                match = re.search(
                    r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
                    input_agent_output, 
                    re.DOTALL
                )
                if match:
                    match = match.group(1).strip()

                structured_output = json.loads(match)
                format_success = True

            except:
                format_success = False

        try:
            if(self.remove_component_index==0):
                filtered_reference_data, remaining_structured_output = self.filter_item_0(structured_output, reference_data)   
            else:
                if(self.remove_component_index==1):
                    filtered_reference_data = reference_data.copy()
                    _, remaining_structured_output = self.filter_item(structured_output, reference_data)
                else:
                    filtered_reference_data, remaining_structured_output = self.filter_item(structured_output, reference_data)

            if(self.remove_component_index==0):
                combination_of_plans = self.combinations_func(parameters=structured_output["parameters"], reference_data=filtered_reference_data)
            else:
                if(self.remove_component_index==1):
                    combination_data = self.build_generic_combinations_1(structured_output["combinations"], filtered_reference_data, self.group_parameter)
                else:
                    combination_data = self.build_generic_combinations(structured_output["combinations"], filtered_reference_data, self.group_parameter)
                combination_of_plans = self.combinations_func(parameters=structured_output["combinations"], reference_data=combination_data)
        except:
            return structured_output, None, None, number_of_token_input, number_of_token_output


        try:
            final_plan = self.solutions_func(data=combination_of_plans, constraints=remaining_structured_output, reference_data=filtered_reference_data)
            final_answer = self.deliver_func(final_plan)
        except:
            return structured_output, None, len(combination_of_plans), number_of_token_input, number_of_token_output


        return structured_output, final_answer, len(combination_of_plans), number_of_token_input, number_of_token_output
