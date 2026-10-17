import os
from google import genai
from google.genai import types
from openai import OpenAI
import json
import re
import glob
import re

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

        self.patience = 3


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


        for i in optimization_options:
            with open(f"prompt_planning_optimization/planning_optimization_{i}_agent.txt", "r") as f:
                optimization_prompt = f.read()

            self.planning_optimization_prompt_list.append(optimization_prompt)

        with open(solver_prompt["combination_reflection"], "r") as f:
            self.combination_reflection_prompt = f.read()

        with open(solver_prompt["solution_reflection"], "r") as f:
            self.solution_reflection_prompt = f.read()

        with open(solver_prompt["deliver_reflection"], "r") as f:
            self.deliver_reflection_prompt = f.read()

        with open(solver_prompt["input"], "r") as f:
            self.generate_input_prompt = f.read()

        self.combinations_func = None
        self.solutions_func = None
        self.deliver_func = None
        self.query = None

        self.combinations_func_output = None
        self.solutions_func_output = None

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
    

    def create_planning(self, few_shot_examples_answer_only, few_shot_examples_no_answer):

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

        prompt = self.generate_planning_prompt

        prompt = prompt.replace("<few_shot_examples_query>", few_shot_examples_no_answer)
        prompt = prompt.replace("<few_shot_examples_solution>", json.dumps(structured_solution_output["solutions"], ensure_ascii=False, indent=4))
        prompt = prompt.replace("<few_shot_examples_solution_description>", json.dumps(structured_solution_output["solutions_description"], ensure_ascii=False, indent=4))

        output = self.call_api(self, prompt)

        with open(f"{self.project_path}/self_improvement_planner.txt", "w") as f:
            f.write(output)

        match = re.search(
            r"<start_of_COT>\s*(.*?)\s*<end_of_COT>", 
            output, 
            re.DOTALL
        )
        if match:
            original_cot = match.group(1).strip()

        
        match = re.search(
            r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
            output, 
            re.DOTALL
        )
        if match:
            match = match.group(1).strip()

        structured_output = json.loads(match)

        if(self.remove_component_index==0):
            # there is no difference between combinations and constraints. both are merged together
            structured_output["combinations"] = structured_output["parameters"]
            structured_output["constraints"] = structured_output["parameters"]
            structured_output["combinations_description"] = structured_output["parameters_description"]
            structured_output["constraints_description"] = structured_output["parameters_description"]

            del structured_output["parameters"]
            del structured_output["parameters_description"]

        match = re.search(
            r"<start_of_planning>\s*(.*?)\s*<end_of_planning>", 
            output, 
            re.DOTALL
        )
        if match:
            match = match.group(1).strip()

        planning_output = json.loads(match)

        structured_output.update(structured_solution_output)

        planning_output_for_optimization = planning_output.copy()
        structured_output_for_optimization = structured_output.copy()
        del structured_output_for_optimization["solutions"]
        del structured_output_for_optimization["solutions_description"]
        
        for i, optimization_prompt in enumerate(self.planning_optimization_prompt_list):
            optimization_prompt = optimization_prompt.replace("<query>", self.query)
            optimization_prompt = optimization_prompt.replace("<cot>", original_cot)
            optimization_prompt = optimization_prompt.replace("<structured_output>", json.dumps(structured_output_for_optimization, ensure_ascii=False, indent=4))
            optimization_prompt = optimization_prompt.replace("<planning>", json.dumps(planning_output_for_optimization, ensure_ascii=False, indent=4))
            optimization_prompt = optimization_prompt.replace("<constraints>", json.dumps(structured_output["constraints"], ensure_ascii=False, indent=4))

            optimization_output = self.call_api(self, optimization_prompt)

            with open(f"{self.project_path}/self_improvement_planner_optimization_{i+1}.txt", "w") as f:
                f.write(optimization_output)

            match = re.search(
                r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
                optimization_output, 
                re.DOTALL
            )
            if match:
                match = match.group(1).strip()
                structured_output_for_optimization = json.loads(match)

            match = re.search(
                r"<start_of_planning>\s*(.*?)\s*<end_of_planning>", 
                optimization_output, 
                re.DOTALL
            )

            if match:
                match = match.group(1).strip()
                planning_output_for_optimization = json.loads(match)

        structured_output.update(structured_output_for_optimization)
        planning_output.update(planning_output_for_optimization)

        input_agent_structured_output = structured_output.copy()
        del input_agent_structured_output["solutions"]
        del input_agent_structured_output["solutions_description"]

        if(self.remove_component_index==0):
            output_description = input_agent_structured_output["combinations_description"]
        else:
            output_description = input_agent_structured_output["combinations_description"] + " " + input_agent_structured_output["constraints_description"]

        self.generate_input_prompt = self.generate_input_prompt.replace("<instructions>", planning_output["Input Agent"])
        self.generate_input_prompt = self.generate_input_prompt.replace("<output_description>", output_description)
        self.generate_input_prompt = self.generate_input_prompt.replace("<example_output>", json.dumps(input_agent_structured_output, ensure_ascii=False, indent=4))

        print("Planning is Complete")

        return structured_output, planning_output


    def create_combinations(self, structured_output, planning_output):

        combination_prompt = self.generate_combination_prompt
        combinations_instructions = planning_output["Combination Function Generator Agent"]
        combinations_input_description = structured_output["combinations_description"]
        combinations_example_input = structured_output["combinations"]
        combinations_example_output = structured_output["solutions"]
        combinations_output_description = structured_output["solutions_description"]

        combination_prompt = combination_prompt.replace("<instructions>", combinations_instructions)
        combination_prompt = combination_prompt.replace("<input_description>", combinations_input_description)
        combination_prompt = combination_prompt.replace("<example_input>", json.dumps(combinations_example_input, ensure_ascii=False, indent=4))
        combination_prompt = combination_prompt.replace("<output_description>", json.dumps(combinations_output_description, ensure_ascii=False, indent=4))
        combination_prompt = combination_prompt.replace("<example_output>", json.dumps(combinations_example_output, ensure_ascii=False, indent=4))

        combination_output = self.call_api(self, combination_prompt)

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

        combinations_func_output = self.combinations_func(combinations_example_input)

        output_exists = combinations_example_output in combinations_func_output

        if(len(combinations_func_output)>0):
            one_of_the_outputs = combinations_func_output[0]
        else:
            one_of_the_outputs = {}

        match = re.search(
            r"<start_of_COT>\s*(.*?)\s*<end_of_COT>", 
            combination_output, 
            re.DOTALL
        )
        if match:
            chain_of_thought = match.group(1).strip()

        combination_reflection_prompt = self.combination_reflection_prompt

        i = 0


        while(output_exists==False):
            if(self.remove_component_index==2 or i>=self.patience):
                break

            new_combination_reflection_prompt = combination_reflection_prompt.replace("<example_input>", json.dumps(one_of_the_outputs, ensure_ascii=False, indent=4))
            new_combination_reflection_prompt = new_combination_reflection_prompt.replace("<example_output>", json.dumps(combinations_example_output, ensure_ascii=False, indent=4))
            new_combination_reflection_prompt = new_combination_reflection_prompt.replace("<chain_of_thought>", chain_of_thought)
            new_combination_reflection_prompt = new_combination_reflection_prompt.replace("<code>", code_body)

            combination_reflection_output = self.call_api(self, new_combination_reflection_prompt)

            match = re.search(
                r"<start_of_code_correction>\s*(.*?)\s*<end_of_code_correction>", 
                combination_reflection_output, 
                re.DOTALL
            )
            if match:
                code_body = match.group(1).strip()

            match = re.search(
                r"<start_of_COT_correction>\s*(.*?)\s*<end_of_COT_correction>", 
                combination_reflection_output, 
                re.DOTALL
            )
            if match:
                chain_of_thought = match.group(1).strip()

            with open(f"{self.project_path}/self_improvement_combination_reflection_{i}.txt", "w") as f:
                f.write(combination_reflection_output)

            local_scope = {}
            exec(code_body, local_scope)
            self.combinations_func = local_scope["combinations_func"]
            combinations_func_output = self.combinations_func(combinations_example_input)
            output_exists = combinations_example_output in combinations_func_output

            if(len(combinations_func_output)>0):
                one_of_the_outputs = combinations_func_output[0]
            else:
                one_of_the_outputs = "None"

            i += 1

        print("Combination Function is Created")
        
        self.combinations_func_output = combinations_func_output


    def create_solutions(self, structured_output, planning_output):
        solutions_instructions = planning_output["Solution Function Generator Agent"]
        solutions_input_description = structured_output["solutions_description"]
        solutions_example_input = structured_output["solutions"]
        constraints_example = structured_output["constraints"]
        constraints_description = structured_output["constraints_description"]


        solution_prompt = self.generate_solution_prompt.replace("<instructions>", solutions_instructions)
        solution_prompt = solution_prompt.replace("<input_description>", json.dumps(solutions_input_description, ensure_ascii=False, indent=4))
        solution_prompt = solution_prompt.replace("<example_input>", json.dumps(solutions_example_input, ensure_ascii=False, indent=4))
        solution_prompt = solution_prompt.replace("<constraints_description>", constraints_description)
        solution_prompt = solution_prompt.replace("<example_constraints>", json.dumps(constraints_example, ensure_ascii=False, indent=4))

        solution_output = self.call_api(self, solution_prompt)

        with open(f"{self.project_path}/self_improvement_solution.txt", "w") as f:
            f.write(solution_output)

        match = re.search(
            r"<start_of_code>\s*(.*?)\s*<end_of_code>", 
            solution_output, 
            re.DOTALL
        )
        if match:
            code_body = match.group(1).strip()

        match = re.search(
            r"<start_of_COT>\s*(.*?)\s*<end_of_COT>", 
            solution_output, 
            re.DOTALL
        )
        if match:
            chain_of_thought = match.group(1).strip()

        local_scope = {}
        exec(code_body, local_scope)

        self.solutions_func = local_scope["plan_func"]

        output_solution = self.solutions_func(data=self.combinations_func_output, constraints=constraints_example)

        solution_reflection_prompt = self.solution_reflection_prompt

        i = 0

        while(output_solution!=solutions_example_input):
            if(self.remove_component_index==2 or i>=self.patience):
                break

            new_solution_reflection_prompt = solution_reflection_prompt.replace("<instructions>", solutions_instructions)
            new_solution_reflection_prompt = new_solution_reflection_prompt.replace("<example_output>", json.dumps(solutions_example_input, ensure_ascii=False, indent=4))
            new_solution_reflection_prompt = new_solution_reflection_prompt.replace("<function_output>", json.dumps(output_solution, ensure_ascii=False, indent=4))
            new_solution_reflection_prompt = new_solution_reflection_prompt.replace("<chain_of_thought>", chain_of_thought)
            new_solution_reflection_prompt = new_solution_reflection_prompt.replace("<code>", code_body)

            solution_reflection_output = self.call_api(self, new_solution_reflection_prompt)

            with open(f"{self.project_path}/self_improvement_solution_reflection_{i}.txt", "w") as f:
                f.write(solution_reflection_output)

            match = re.search(
                r"<start_of_code_correction>\s*(.*?)\s*<end_of_code_correction>", 
                solution_reflection_output, 
                re.DOTALL
            )
            if match:
                code_body = match.group(1).strip()

            match = re.search(
                r"<start_of_COT_correction>\s*(.*?)\s*<end_of_COT_correction>", 
                solution_reflection_output, 
                re.DOTALL
            )
            if match:
                chain_of_thought = match.group(1).strip()

            local_scope = {}
            exec(code_body, local_scope)
            self.solutions_func = local_scope["plan_func"]
            output_solution = self.solutions_func(data=self.combinations_func_output, constraints=constraints_example)

            if(output_solution==None):
                output_solution = "None"

            i += 1

        print("Solution Function is Created")
        self.solutions_func_output = output_solution

        

    def create_deliver(self, structured_output, few_shot_examples_answer_only):
        deliver_prompt = self.generate_deliver_prompt
        deliver_input_description = structured_output["solutions_description"]
        deliver_example_input = structured_output["solutions"]

        deliver_prompt = deliver_prompt.replace("<input_description>", deliver_input_description)
        deliver_prompt = deliver_prompt.replace("<example_input>", json.dumps(deliver_example_input, ensure_ascii=False, indent=4))
        deliver_prompt = deliver_prompt.replace("<few_shot_examples_solution>", few_shot_examples_answer_only)

        deliver_output = self.call_api(self, deliver_prompt)

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

        output_solution = self.deliver_func(deliver_example_input)

        deliver_reflection_prompt = self.deliver_reflection_prompt

        deliver_reflection_prompt = deliver_reflection_prompt.replace("<structured_input>", json.dumps(deliver_example_input, ensure_ascii=False, indent=4))
        deliver_reflection_prompt = deliver_reflection_prompt.replace("<example_output>", few_shot_examples_answer_only)
        i = 0

        while(output_solution.strip()!=few_shot_examples_answer_only.strip()):
            if(i>=self.patience):
                break

            new_deliver_reflection_prompt = deliver_reflection_prompt.replace("<current_output>", output_solution)
            new_deliver_reflection_prompt = new_deliver_reflection_prompt.replace("<code>", code_body)

            deliver_output = self.call_api(self, new_deliver_reflection_prompt)

            with open(f"{self.project_path}/self_improvement_deliver_reflection_{i}.txt", "w") as f:
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
            output_solution = self.deliver_func(deliver_example_input)
            i+=1
        
        print("Deliver Function is Created")


    def create_solver(self, few_shot_examples_answer_only, few_shot_examples_no_answer):
        self.generate_input_prompt = self.generate_input_prompt.replace("<example_input>", few_shot_examples_no_answer)
        self.query = few_shot_examples_no_answer

        structured_output, planning_output = self.create_planning(few_shot_examples_answer_only, few_shot_examples_no_answer)

        self.create_combinations(structured_output, planning_output)
        self.create_solutions(structured_output, planning_output)
        self.create_deliver(structured_output, few_shot_examples_answer_only)

        print("All functions are created!")


    
    def get_file_name(self, parameter):
        fallback = f"{self.project_path}/self_improvement_{parameter}.txt"

        # Pattern to search
        if(parameter=="planning"):
            files = glob.glob(f"{self.project_path}/self_improvement_{parameter}_optimization_*.txt")
        else:
            files = glob.glob(f"{self.project_path}/self_improvement_{parameter}_reflection_*.txt")

        if files:
            # Extract numbers from filenames
            numbers = []
            for f in files:
                if(parameter=="planning"):
                    match = re.search(r"optimization_(\d+)\.txt$", f)
                else:
                    match = re.search(r"reflection_(\d+)\.txt$", f)

                if match:
                    numbers.append((int(match.group(1)), f))
            
            if numbers:
                # Pick file with largest number
                chosen_file = max(numbers, key=lambda x: x[0])[1]
            else:
                chosen_file = fallback
        else:
            chosen_file = fallback

        return chosen_file
        


    def load_checkpoints(self, few_shot_examples_no_answer):

        planner_file = self.get_file_name("planner")

        with open(planner_file, "r") as f:
            output = f.read()

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
        input_agent_structured_output = structured_output.copy()
        del input_agent_structured_output["combinations_description"]
        del input_agent_structured_output["constraints_description"]

        output_description = structured_output["combinations_description"] + " " + structured_output["constraints_description"]

        self.generate_input_prompt = self.generate_input_prompt.replace("<instructions>", planning_output["Input Agent"])
        self.generate_input_prompt = self.generate_input_prompt.replace("<output_description>", output_description)
        self.generate_input_prompt = self.generate_input_prompt.replace("<example_input>", few_shot_examples_no_answer)
        self.generate_input_prompt = self.generate_input_prompt.replace("<example_output>", json.dumps(input_agent_structured_output, ensure_ascii=False, indent=4))
        
        combination_file = self.get_file_name("combination")

        with open(combination_file, "r") as f:
            combination_output = f.read()

        if "<start_of_code_correction>" in combination_output:
            match = re.search(
                r"<start_of_code_correction>\s*(.*?)\s*<end_of_code_correction>", 
                combination_output, 
                re.DOTALL
            )
        else:
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

        solution_file = self.get_file_name("solution")

        with open(solution_file, "r") as f:
            solution_output = f.read()

        if "<start_of_code_correction>" in solution_output:
            match = re.search(
                r"<start_of_code_correction>\s*(.*?)\s*<end_of_code_correction>", 
                solution_output, 
                re.DOTALL
            )
        else:
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

        with open(f"{self.project_path}/self_improvement_deliver.txt", "r") as f:
            deliver_output = f.read()

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

        print("All functions are created!")


     

    def solve(self, prompt_zero_shot):

        input_agent_prompt, number_of_token_input, number_of_token_output = self.generate_input_prompt.replace("<query>", prompt_zero_shot)

        try:  
            input_agent_output = self.call_api(input_agent_prompt)
            
            match = re.search(
                r"<start_of_structured_output>\s*(.*?)\s*<end_of_structured_output>", 
                input_agent_output, 
                re.DOTALL
            )
            if match:
                match = match.group(1).strip()

            structured_output = json.loads(match)
        except:
            return None, None, None, number_of_token_input, number_of_token_output

        try:
            combination_of_plans = self.combinations_func(structured_output["combinations"])
        except:
            return structured_output, None, None, number_of_token_input, number_of_token_output 

        try:
            final_plan = self.solutions_func(data=combination_of_plans, constraints=structured_output["constraints"])
            final_answer = self.deliver_func(final_plan)
        except:
            return structured_output, None, len(combination_of_plans), number_of_token_input, number_of_token_output 


        return structured_output, final_answer, len(combination_of_plans), number_of_token_input, number_of_token_output 
