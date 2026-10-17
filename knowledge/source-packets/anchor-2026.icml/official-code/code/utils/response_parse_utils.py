import json
import re

from typing import List, Dict, Any, Tuple, Union
def safe_json_parse(response, default_value=None, context=""):
    """
    Unified JSON parsing function that handles failures gracefully.
    Uses multiple strategies to extract valid JSON from response.
    """
    # Strategy 1: Direct parsing after cleaning
    try:
        # Strip any extra whitespace and try to parse
        cleaned_response = response.strip()

        # Remove common model tokens that might interfere with JSON parsing
        tokens_to_remove = ['<|eot_id|>', '<|end_of_text|>', '<|endoftext|>', '', '<|im_end|>']
        for token in tokens_to_remove:
            cleaned_response = cleaned_response.replace(token, '')

        # Clean up any trailing whitespace after token removal
        cleaned_response = cleaned_response.strip()

        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract JSON using regex patterns
    print(f"[JSON Parse] Direct parsing failed, trying regex extraction...")

    # First try to find JSON after "Final answer:" or similar markers
    final_answer_patterns = [
        r'Final answer:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
        r'Final answer:\s*(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])',
        r'Answer:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
        r'Answer:\s*(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])',
        r'Result:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
        r'Result:\s*(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])'
    ]

    for pattern in final_answer_patterns:
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                extracted_json = json.loads(match.strip())
                print(f"[JSON Parse] Successfully extracted JSON from final answer: {extracted_json}")
                return extracted_json
            except json.JSONDecodeError:
                continue

    # If no final answer marker found, try general JSON patterns
    # Pattern for JSON objects: {...}
    json_object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    # Pattern for JSON arrays: [...]
    json_array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'

    # Try to find JSON arrays first (more common for factor extraction)
    for pattern in [json_array_pattern, json_object_pattern]:
        matches = re.findall(pattern, response, re.DOTALL)
        # Try matches in reverse order (last JSON is likely the final answer)
        for match in reversed(matches):
            try:
                extracted_json = json.loads(match.strip())
                print(f"[JSON Parse] Successfully extracted JSON using regex: {extracted_json}")
                return extracted_json
            except json.JSONDecodeError:
                continue

    # Strategy 3: For factor extraction, try to parse as text list
    if context == "Factor extraction" and isinstance(default_value, list):
        print(f"[JSON Parse] Trying text-based factor extraction...")
        factors = []

        # Pattern 1: Numbered lists (1. factor, 2. factor, etc.)
        numbered_pattern = r'^\s*\d+\.\s*(.+?)(?=\n\s*\d+\.|$)'
        numbered_matches = re.findall(numbered_pattern, response, re.MULTILINE | re.DOTALL)
        if numbered_matches:
            factors.extend([match.strip().strip('"\'') for match in numbered_matches])
            print(f"[JSON Parse] Found numbered list: {numbered_matches}")

        # Pattern 2: Bullet points (- factor, * factor, • factor)
        if not factors:
            bullet_pattern = r'^\s*[-*•]\s*(.+?)(?=\n\s*[-*•]|$)'
            bullet_matches = re.findall(bullet_pattern, response, re.MULTILINE | re.DOTALL)
            if bullet_matches:
                factors.extend([match.strip().strip('"\'') for match in bullet_matches])
                print(f"[JSON Parse] Found bullet list: {bullet_matches}")

        # Pattern 3: Quoted strings (for cases like "factor1", "factor2")
        if not factors:
            quoted_pattern = r'"([^"]+)"'
            quoted_matches = re.findall(quoted_pattern, response)
            if quoted_matches and len(quoted_matches) > 1:  # Only if multiple quotes found
                factors.extend([match.strip() for match in quoted_matches])
                print(f"[JSON Parse] Found quoted factors: {quoted_matches}")

        # Pattern 4: Fallback to line-by-line parsing
        if not factors:
            print("[JSON Parse] No patterns matched, trying line-by-line parsing...")
            lines = [line.strip() for line in response.split('\n') if line.strip()]

            for line in lines:
                # Skip lines that look like instructions or explanations
                if any(word in line.lower() for word in ['extract', 'factor', 'list', 'array', 'json']):
                    continue

                # Clean up the line
                cleaned_line = line
                # Remove numbered list markers (1. 2. etc.)
                cleaned_line = re.sub(r'^\d+\.\s*', '', cleaned_line)
                # Remove bullet points (- * •)
                cleaned_line = re.sub(r'^[-*•]\s*', '', cleaned_line)
                # Remove quotes if present
                cleaned_line = cleaned_line.strip('"\'')
                # Remove trailing punctuation
                cleaned_line = re.sub(r'[,;.]+$', '', cleaned_line)

                if cleaned_line and len(cleaned_line) > 2:  # Avoid single characters
                    factors.append(cleaned_line)

        # Remove duplicates and empty strings
        if factors:
            factors = list(set([f.strip() for f in factors if f.strip()]))
            print(f"[JSON Parse] Text extraction succeeded: {factors}")
            return factors

    # Strategy 4: For voting, try to extract choice from text
    if "Voting for factor" in context and isinstance(default_value, dict):
        print(f"[JSON Parse] Trying text-based voting extraction...")

        # Extract factor name from context
        factor_match = re.search(r"Voting for factor '([^']+)'", context)
        if factor_match:
            factor = factor_match.group(1)
            valid_choices = ['Statement1', 'Statement2', 'Both', 'Neutral']

            # Pattern 1: Look for explicit choice statements
            choice_patterns = [
                rf'{re.escape(factor)}.*?(?:supports?|chooses?|is|->|:)\s*(Statement[12]|Both|Neutral)',
                rf'(Statement[12]|Both|Neutral).*?{re.escape(factor)}',
                rf'Factor.*?{re.escape(factor)}.*?(Statement[12]|Both|Neutral)',
                rf'(Statement[12]|Both|Neutral).*?for.*?{re.escape(factor)}'
            ]

            for pattern in choice_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if match in valid_choices:
                        result = {factor: match}
                        print(f"[JSON Parse] Text extraction found choice: {result}")
                        return result

            # Pattern 2: Look for any valid choice in the text (fallback)
            for choice in valid_choices:
                if choice.lower() in response.lower():
                    result = {factor: choice}
                    print(f"[JSON Parse] Fallback found choice: {result}")
                    return result

    # Strategy 5: For clustering, ensure we return a dict format
    if context == "Factor clustering" and isinstance(default_value, dict):
        print(f"[JSON Parse] Trying text-based clustering extraction...")

        # Try to extract cluster-like patterns from text
        # Pattern: "cluster_name": ["factor1", "factor2"]
        cluster_pattern = r'"([^"]+)":\s*\[([^\]]+)\]'
        cluster_matches = re.findall(cluster_pattern, response)

        if cluster_matches:
            clusters = {}
            for cluster_name, factors_str in cluster_matches:
                # Extract factors from the string
                factor_pattern = r'"([^"]+)"'
                factors_in_cluster = re.findall(factor_pattern, factors_str)
                if factors_in_cluster:
                    clusters[cluster_name] = factors_in_cluster

            if clusters:
                print(f"[JSON Parse] Text extraction found clusters: {clusters}")
                return clusters

    # Strategy 6: For pruning, try to extract factor list from text
    if "Pruning cluster" in context and isinstance(default_value, list):
        print(f"[JSON Parse] Trying text-based pruning extraction...")

        # Try to find factors mentioned in the text
        factors_mentioned = []
        for factor in default_value:
            if factor.lower() in response.lower():
                factors_mentioned.append(factor)

        if factors_mentioned:
            print(f"[JSON Parse] Text extraction found factors: {factors_mentioned}")
            return factors_mentioned

        # If no factors found in text, return original list
        print(f"[JSON Parse] No factors found in text, returning original list")
        return default_value

    # Strategy 7: Failed - return default
    print(f"[JSON Parse Error] {context}")
    print(f"[JSON Parse Error] Original response: {response}")
    print(f"[JSON Parse Error] All parsing strategies failed, returning default value: {default_value}")
    return default_value


def extract_choice_from_response(parsed_response, factor):
    """
    Extract choice from parsed JSON response, handling various formats.
    """
    if isinstance(parsed_response, dict):
        # Try exact match first
        if factor in parsed_response:
            return parsed_response[factor]

        # Try case-insensitive match
        for key, value in parsed_response.items():
            if key.lower().strip() == factor.lower().strip():
                return value

        # Try partial match (in case of slight differences)
        for key, value in parsed_response.items():
            if factor in key or key in factor:
                print(f"[Match] Using partial match: '{factor}' -> '{key}' = {value}")
                return value

        # If no match found, try to get the first value if there's only one
        if len(parsed_response) == 1:
            value = list(parsed_response.values())[0]
            print(f"[Match] Using single value from response: {value}")
            return value

    print(f"[Match] No match found for factor: '{factor}' in response: {parsed_response}")
    return 'Neutral'


def extract_json_block(text: str) -> str:
    """
    Extract the first JSON object string from raw text.
    Supports:
      1. ```json ... ``` code blocks
      2. First {...} block in plain text, automatically balancing braces
    """
    # 1. Try to match ```json ... ``` blocks
    fenced = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
    if fenced:
        return fenced.group(1)
    # 2. Match the first { and find balanced }
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in text")
    count = 0
    for i, ch in enumerate(text[start:], start):
        if ch == '{':
            count += 1
        elif ch == '}':
            count -= 1
            if count == 0:
                return text[start:i+1]
    raise ValueError("Could not find complete JSON object block")



def parse_latents(
    raw_text: str
) -> List[Dict[str, Any]]:
    """
    Extract and parse JSON containing 'latents' field from raw text,
    Returns:
      latents: List[{'name': str, 'factors': List[str]}]

    Raises ValueError if format error occurs.
    """
    # Extract JSON substring
    json_str = extract_json_block(raw_text)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

    # Validate fields
    if 'latents' not in data:
        raise ValueError("JSON must contain 'latents' field")

    # Parse latents
    raw_latents = data['latents']
    if not isinstance(raw_latents, list):
        raise ValueError("'latents' should be a list")

    latents: List[Dict[str, Any]] = []
    for item in raw_latents:
        if not isinstance(item, dict):
            raise ValueError("Each element in latents should be a dict")
        name = item.get('name')
        factors = item.get('factors')
        if not isinstance(name, str) or not isinstance(factors, list):
            raise ValueError("Each latent must have 'name'(str) and 'factors'(list)")
        latents.append({'name': name, 'factors': factors})

    return latents


import json
import re
import ast
from typing import Dict, Any

def parse_latents_prob(text: str) -> Dict[str, Any]:
    """
    Stably extract and parse JSON structure from text that may contain extra text 
    or Python dict syntax (single quotes, trailing commas, etc.).

    Args:
        text: Raw text containing JSON or Python dict literal
    Returns:
        dict: Parsed Python dictionary
    Raises:
        ValueError: If JSON block is not found or all parsing attempts fail
    """
    # 1. First try to find the outermost braces and extract substring
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or start > end:
        raise ValueError("Could not locate JSON brace block")
    snippet = text[start:end+1].strip()

    # 2. First try standard JSON parsing
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        pass

    # 3. Common fix 1: Remove trailing commas
    snippet2 = re.sub(r',\s*([}\]])', r'\1', snippet)

    # 4. Common fix 2: Replace single quote literals with double quotes
    #    Only match real string literals, don't touch numerical values
    def _fix_quotes(m):
        inner = m.group(0)
        return '"' + inner[1:-1].replace('"', '\\"') + '"'
    snippet2 = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", _fix_quotes, snippet2)

    try:
        return json.loads(snippet2)
    except json.JSONDecodeError:
        pass

    # 5. Finally try ast.literal_eval (can parse Python dict syntax)
    try:
        obj = ast.literal_eval(snippet)
    except Exception as e:
        raise ValueError(f"Cannot parse as JSON or Python literal: {e}")

    # 6. Ensure result is dict and contains only numbers or nested dicts
    if not isinstance(obj, dict):
        raise ValueError("Parsed result is not a dict")
    return obj
