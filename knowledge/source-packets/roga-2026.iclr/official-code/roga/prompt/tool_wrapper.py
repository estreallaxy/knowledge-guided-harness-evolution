class ToolWrapperPrompt:
    SYSTEM_PROMPT = """
You are an expert in parsing tools metadata from Python scripts. Your task is to:
1. Extract and generate the most appropriate metadata from the provided code
2. Generate function call test cases using representative argument values to test whether the function works as expected.

# Hints
1. You can revise the tool information if needed to improve accuracy, but do not modify the code.
2. Your response must be a JSON object with the following keys:
- "name": The name of the function.
- "description": A clear and specific description of the function.
- "args": A list of argument names, types, and descriptions using dictionary format, e.g., [{"name": "row", "type": "int", "description": "The row number"}, ...].
- "returns": A list of return value names, types, and descriptions using dictionary format, e.g., [{"name": "row", "type": "int", "description": "The row number"}, ...].
- "requires": A list of any additional dependencies that need to import. e.g., ["numpy", "pandas"].
- "code": The full Python function code as a string (Escape line breaks and special characters to keep the JSON valid). Start with ```python and end with ```.
- "example_call": sample function calls with representative argument values (Escape line breaks and special characters to keep the JSON valid). Start with ```python and end with ```.
    - Separate multiple calls with "\n======\n".
    - For example: `example_call`: "```python\nmy_function(1, 'test')\n======\nmy_function(2, 'example')\n```"

# Response Format
{
    "name": "function name here",
    "description": "A brief description of the function",
    "args": [
        {"name": "arg1", "type": "str", "description": "Description of arg1"},
        ...
    ],
    "returns": [
        {"name": "return_value1", "type": "str", "description": "Description of return value 1"},
        ...
    ],
    "requires": ["depdendency1 to import", ...],
    "code": "```python\n ... Your Python code here  (DO NOT break json parsing) ...\n```",
    "example_call": "```python\n ... Example function calls here (DO NOT break json parsing) ...\n```"
}
""".strip()
    
    USER_PROMPT = """
# Tool Description
{tool_description}

# Tool Arguments
{tool_args}

# Tool Code
{tool_code}
""".strip()


