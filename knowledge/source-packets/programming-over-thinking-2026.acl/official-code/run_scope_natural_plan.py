import json
import time
import os
import argparse
from scope.workflow import Solver

parser = argparse.ArgumentParser()

parser.add_argument("--model", default="gpt-4o", type=str)
parser.add_argument("--dataset", default="trip_planning", type=str)
parser.add_argument("--load_checkpoint", default=None, type=str)
parser.add_argument("--remove_component_index", default=None, type=int)

args = parser.parse_args()

model = args.model
dataset = args.dataset
remove_component_index = args.remove_component_index

if(remove_component_index==None):
    output_file = f"../output/{dataset}_scope.json"
else:
    remove_component_dict = {
        0: "problem_formalisation",
        1: "problem_optimisation",
        2: "code_refinement"
    }

    remove_component = remove_component_dict[remove_component_index]

    output_file = f"output_full_{model}/{dataset}_scope_{remove_component}.json"

if(dataset not in ["trip_planning", "meeting_planning"]):
    raise Exception("Dataset not found")

solver_prompt = {
    "planning": f"prompt_scope_{dataset}_{model}/planning_agent.txt",
    "planning_solution": f"prompt_scope_{dataset}_{model}/solution_agent.txt",
    "combination": f"prompt_scope_{dataset}_{model}/combination_function_generator_agent.txt",
    "solution": f"prompt_scope_{dataset}_{model}/solution_function_generator_agent.txt",
    "deliver": f"prompt_scope_{dataset}_{model}/deliver_function_generator_agent.txt",
    "input": f"prompt_scope_{dataset}_{model}/input_agent.txt",
    "combination_reflection": f"prompt_scope_{dataset}_{model}/combination_function_generator_reflection_agent.txt",
    "solution_reflection": f"prompt_scope_{dataset}_{model}/solution_function_generator_reflection_agent.txt",
    "deliver_reflection": f"prompt_scope_{dataset}_{model}/deliver_function_generator_reflection_agent.txt"
}

if(remove_component_index==0):
    solver_prompt["planning"] = f"prompt_scope_{dataset}_{model}/planning_agent_0.txt"
    solver_prompt["combination"] = f"prompt_scope_{dataset}_{model}/combination_function_generator_agent_0.txt"
    solver_prompt["solution"] = f"prompt_scope_{dataset}_{model}/solution_function_generator_agent_0.txt"


# we recommend using Optimization Agent 1,2,3 for Trip Planning and 4 for Meeting Planning
if(dataset=="trip_planning"):
    optimization_options = [1,2,3]
else:
    optimization_options = [4]

if(args.load_checkpoint!=None):
    solver = Solver(solver_prompt, optimization_options, args.load_checkpoint, model, remove_component_index)
else:
    solver = Solver(solver_prompt, optimization_options, f"{dataset}_{model}_{remove_component}", model, remove_component_index)

# Example data used to build functions in SCOPE
with open(f"scope/prompt/example_data.json", "r") as f:
    example_data = json.load(f)

with open(f"data/{dataset}.json", "r") as f:
    test_data = json.load(f)


example_query = example_data[dataset]["query"]
example_solution = example_data[dataset]["solution"]

if(args.load_checkpoint):
    solver.load_checkpoints(example_query)
else:
    solver.create_solver(example_query, example_solution)


if os.path.exists(output_file):
    with open(output_file, "r") as f:
        generated_data = json.load(f)
else:
    generated_data = {}


print(f"Dataset : {dataset}| Model : {model}")
    

for d in test_data:

    index = int(d.split("_")[-1])
        
    if(d in generated_data):
        continue

    data = test_data[d]

    start_time = time.time()
    structured_output, final_answer, combination_size, number_of_token_input, number_of_token_output = solver.solve(data["prompt_0shot"])
    data["structured_output"] = structured_output
    data["plan"] = final_answer
    data["combination_size"] = combination_size
    data["time_taken"] = time.time() - start_time
    data["number_of_input_token"] = number_of_token_input
    data["number_of_output_token"] = number_of_token_output

    generated_data[d] = data

    with open(output_file, "w") as f:
        json.dump(generated_data, f, ensure_ascii=False, indent=4)
    
