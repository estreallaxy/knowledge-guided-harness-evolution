import docker
import json
# import signal
import logging
import time
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import subprocess

import re

# Host-side scratch directory for C/C++/Java/Python compilation inputs that are
# then `docker cp`'d into the target container. Lives under the repo root so
# it's easy to find and clean.
_RA_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_RA_MODULE_DIR, "..", ".."))
_TMP_ROOT = os.path.join(_REPO_ROOT, "tmp")


def extract_java_function_name(java_code):
    # Use a regex to grab the class name that follows `public class`
    class_match = re.search(r'public class (\w+)', java_code)

    if class_match:
        class_name = class_match.group(1)  # the captured class name
        return class_name
    else:
        print("No class found in the provided Java code.")
        return None


class BaseModel:
    def __init__(self, model, temperature, top_p, seed, max_tokens, dry_run):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.max_tokens = max_tokens
        self.dry_run = dry_run
        if model=='deepseek-coder-6.7b-instruct':
            self.tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-6.7b-instruct", trust_remote_code=True)
            self.deepseek = AutoModelForCausalLM.from_pretrained(
                "deepseek-ai/deepseek-coder-6.7b-instruct", 
                trust_remote_code=True, 
                torch_dtype=torch.bfloat16
            ).cuda()
        if model=='deepseek-coder-v2-lite-instruct':
            self.tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-v2-lite-instruct", trust_remote_code=True)
            self.deepseek_v2 = AutoModelForCausalLM.from_pretrained(
                "deepseek-ai/deepseek-coder-v2-lite-instruct", 
                trust_remote_code=True, 
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
        if model=='CodeLlama-7b-Instruct-hf':
            self.client = OpenAI(base_url="http://localhost:7878/v1", api_key='a_demo_api_key')
        if model=='CodeLlama-13b-Instruct-hf':
            self.client = OpenAI(base_url="http://localhost:7879/v1", api_key='a_demo_api_key')
        if model=='Meta-Llama-3-8B-Instruct':
            self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
            self.llama3 = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Meta-Llama-3-8B-Instruct",
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
        if model=='llama-2-7b-chat-hf':
            self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/llama-2-7b-chat-hf")
            self.llama2 = AutoModelForCausalLM.from_pretrained(
                "meta-llama/llama-2-7b-chat-hf",
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
        if model=='llama-2-13b-chat-hf':
            self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/llama-2-13b-chat-hf")
            self.llama2 = AutoModelForCausalLM.from_pretrained(
                "meta-llama/llama-2-13b-chat-hf",
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
        if model=='gemma-2-9b-it':
            self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it")
            self.gemma2 = AutoModelForCausalLM.from_pretrained(
                "google/gemma-2-9b-it",
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
        if 'gpt' in model:
            if model=='gpt-4o':
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError(
                        "OPENAI_API_KEY is not set. Export it (e.g. via scripts/run_agent.sh) "
                        "before using the gpt-4o RA evaluator."
                    )
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = OpenAI(base_url="https://tnrllmproxy.azurewebsites.net/v1")

    def generate_deepseek(self, messages):
        inputs = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(self.deepseek.device)
        # tokenizer.eos_token_id is the id of <|EOT|> token
        outputs = self.deepseek.generate(inputs, max_new_tokens=self.max_tokens, top_p=self.top_p, num_return_sequences=1, eos_token_id=self.tokenizer.eos_token_id)
        ans = self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        return ans
    def generate_deepseek_v2(self, messages):
        inputs = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(self.deepseek_v2.device)
        # tokenizer.eos_token_id is the id of <|EOT|> token
        outputs = self.deepseek_v2.generate(inputs, max_new_tokens=self.max_tokens, do_sample=False, top_p=self.top_p, num_return_sequences=1, eos_token_id=self.tokenizer.eos_token_id)
        ans = self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        return ans
    def generate_llama3(self, messages):
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.llama3.device)
        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        outputs = self.llama3.generate(
            input_ids,
            max_new_tokens=self.max_tokens,
            eos_token_id=terminators,
            do_sample=False,
            top_p=self.top_p,
        )
        ans = self.tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
        return ans
    def generate_llama2(self, messages):
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.llama2.device)
        outputs = self.llama2.generate(
            input_ids,
            max_new_tokens=self.max_tokens,
            do_sample=False,
            top_p=self.top_p,
        )
        ans = self.tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
        return ans
    def generate_gemma2(self, messages):
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt").to(self.gemma2.device)
        outputs = self.gemma2.generate(
            input_ids, 
            max_new_tokens=self.max_tokens, 
            do_sample=False, 
            top_p=self.top_p,
        )
        ans = self.tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
        return ans

class EvalTask:
    def __init__(self, task, version):
        self.task = task
        self.version = version

class Container:
    def __init__(self, image, name):
        self.image = image
        self.client = docker.from_env()
        self.container = None
        self.name = name

    def __del__(self):
        try:
            self.container.stop()
        except:
            pass
    
    def __enter__(self):
        try:
            # Check if the image exists
            if not self.image_exists(self.image):
                logging.info(f"Image {self.image} not found. Building the image from Dockerfile.")
                self.build_image()

            # Create the container
            self.container = self.client.containers.run(
                self.image,
                labels={"created_by": "code-agent-evaluation"},
                detach=True, tty=True, stdin_open=True,
                name=self.name
            )
            logging.info(f"Container {self.name} started successfully.")
            
            # Run initialization script
            output = self.container.exec_run("bash /app/init.sh")
            output_str = output.output.decode()
            logging.info(f"Container init output: {output_str}")
        except Exception as e:
            import traceback
            logging.error(f"Failed to start container: {e}")
            logging.error("Traceback: " + traceback.format_exc())
            self.container = None
        return self

    def image_exists(self, image_name):
        try:
            # Attempt to fetch the image
            self.client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def build_image(self):
        try:
            # Build the Docker image from the Dockerfile in ../environment
            dockerfile_path = os.path.join(os.path.dirname(__file__), "../../../environment")
            logging.info(f"Building image {self.image} from Dockerfile in {dockerfile_path}.")
            self.client.images.build(path=dockerfile_path, tag=self.image)
            logging.info(f"Image {self.image} built successfully.")
        except Exception as e:
            logging.error(f"Failed to build image {self.image}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.stop()
        self.container.remove()

    def execute_with_retries(self, cmd, retries=3, timeout=1*60):
        print("=== EXECUTING with retries ===\n")
        print(f"cmd = {cmd}\n")
        def handler(signum, frame):
            raise TimeoutError("Execution timed out")
        
        # signal.signal(signal.SIGALRM, handler)
        
        for attempt in range(retries):

            # # Naive exec_run
            # output = self.container.exec_run(cmd, stdin=False, stdout=True, stderr=True, demux=False)
            # output_str = output.output.decode()
            # return output_str

            try:
                logging.debug(f"Attempt {attempt+1}: Starting exec_run in {cmd}")
                # signal.alarm(timeout)
                output = self.container.exec_run(cmd, stdin=False, stdout=True, stderr=True, demux=False)
                # signal.alarm(0)
                output_str = output.output.decode()
                logging.debug("Finished exec_run")

                if "EOFError" in output_str:
                    logging.error(f"EOFError detected in command output: {cmd}\nOutput:\n{output_str}")
                    return "Execution blocked due to EOFError"
                
                return output_str
            except TimeoutError:
                logging.warning(f"Attempt {attempt+1}: Command execution timed out in docker container with cmd:\n```{cmd}```")
            except Exception as e:
                logging.error(f"Attempt {attempt+1}: An error occurred in docker container: {e}")
            
            logging.info(f"Retrying in 2 seconds...")
            time.sleep(2)
        
        return "Execution timed out"


    def execute_independent(self, command, timeout=1*60, *params):
        print("=== EXECUTING INDEPENDENT ===\n", command)
        language, command = command

        if language and language.lower() != "bash":
            print("=== Copying files to Local ===\n")
            func_name = ""
            # Define the paths based on the file type
            if language.lower() == "c":
                temp_file = os.path.join(_TMP_ROOT, "c", "temp_code.c")
                destination = "/tmp/main.c"
            elif language.lower() == "cpp":
                temp_file = os.path.join(_TMP_ROOT, "cpp", "temp_code.cpp")
                destination = "/tmp/main.cpp"
            elif language.lower() == "java":
                temp_file = os.path.join(_TMP_ROOT, "java", "temp_code.java")
                func_name = extract_java_function_name(command)
                destination = f"/tmp/{func_name}.java"
            elif language.lower() == "python":
                temp_file = os.path.join(_TMP_ROOT, "python", "temp_code.py")
                destination = f"/tmp/main.py"
            else:
                print(f"Unsupported language, no need to copy: {language.lower()}")
                

            temp_dir = os.path.dirname(temp_file)  # Get the directory from the full file path
            os.makedirs(temp_dir, exist_ok=True)  # Create the directory if it does not exist

            # Write the command content to a temporary file in the container's file system
            with open(temp_file, "w") as f:
                command = command.replace("\\n", "\n")
                f.write(command)
            
            print(f"Here self = {self}")

            container_name = self.name  # the container's name
            print(f"Container Name: {container_name}")

            # Use docker cp to copy the file from the container to the desired destination on the host
            try:
                # Run docker cp command to copy file to the host system
                subprocess.run(['docker', 'cp', temp_file, f'{container_name}:{destination}'], check=True)
                print(f"File copied to {destination}")
            except subprocess.CalledProcessError as e:
                print(f"Error copying file: {e}")

        print("=== EXECUTING bash ===\n")
        # if params:
        #     print("== Parameters ==\n", params)
        if language and language.lower() == "bash":
            print("=== EXECUTING bash ===\n")
            cmd = ["bash", "-c", command]
            if params:
                cmd.append("--")
                cmd.extend(params)
        elif language and language.lower() == "python":
            print("=== EXECUTING bash ===\n")
            cmd = ["python", "-c", command, *params]
        elif language and language.lower() == "cpp":
            print("=== EXECUTING CPP ===\n")

            self.execute_independent(
                (
                    "bash",
                    # f'echo "{json.dumps(command)}" > /tmp/main.cpp && '
                    f"g++ -o /tmp/a.out /tmp/main.cpp",
                ),
                None,
            )
            cmd = ["/tmp/a.out", *params]
        elif language and language.lower() == "c":
            print("=== EXECUTING C ===\n")
            self.execute_independent(
                (
                    "bash",
                    # f'echo "{json.dumps(command)}" > /tmp/main.cpp && '
                    f"gcc -o /tmp/a.out /tmp/main.c",
                ),
                None,
            )
            cmd = ["/tmp/a.out", *params]
        elif language and language.lower() == "java":
            # Compile the Java source
            self.execute_independent(
                (
                    "bash",
                    # f'echo "{json.dumps(command)}" > /tmp/Main.java && '
                    f"javac /tmp/{func_name}.java",
                ),
                None,
            )
            # Run the compiled Java program
            cmd = ["java", "-cp", "/tmp", f"{func_name}", *params]
        else:
            raise ValueError(f"Unsupported language {language}")
        
        return self.execute_with_retries(cmd, timeout=timeout)