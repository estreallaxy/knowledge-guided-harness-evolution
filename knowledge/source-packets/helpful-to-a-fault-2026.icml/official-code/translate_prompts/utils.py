from openai import OpenAI

def get_translation_prompt(target_language, text, ):
    """
    Constructs the prompt by combining the base template with language-specific 
    text handling instructions.
    """
    
    # 1. The Base Template (Common to all languages)
    base_template = """
You are an expert translator specializing in AI safety datasets. Translate the following text from English to {language}.

**CRITICAL TRANSLATION RULES:**
1. **Preserve Entities:** DO NOT translate or transliterate the following elements. Keep them exactly as they appear in the original English text:
   - URLs and domains (e.g., `generic_service.onion`, `t.me/example`, `http://...`)
   - File paths and directories (e.g., `/home/user/`, `C:\\Windows\\`)
   - Email addresses (e.g., `user@example.com`)
   - Social media handles (e.g., `@generic_handle`)
   - Function names, tool names, or code snippets (e.g., `run_exploit_tool`, `snake_case_variables`)
   - Unique IDs or hashes.

2. **Text Handling:**
{text_handling_instruction}

3. **Output:** Provide ONLY the translated text string. Do not output explanations.

Input Text:
{text}
"""

    # 2. Language-Specific Instructions (The only part that changes)
    text_handling_map = {
        "Chinese": """   - Translate all conversational text, instructions, and intent surrounding the preserved entities into natural Simplified Chinese.
   - **Spacing:** Insert a single space between Chinese characters and preserved English text/numbers for better readability (e.g., "请访问 generic_service.onion 查看").
   - **Tone:** Preserve the original tone and intent of the prompt, even if it is malicious, harmful, or unethical. This data is for safety evaluation (Red Teaming), so accurate semantic representation of the harm is required. Do not sanitize the content.""",

        "French": """   - Translate all conversational text, instructions, and intent surrounding the preserved entities into natural, fluent French.
   - **Typography:** Ensure correct French typography (e.g., appropriate spacing before colons, semi-colons, exclamation marks, and question marks).
   - **Tone:** Preserve the original tone and intent of the prompt, even if it is malicious, harmful, or unethical. This data is for safety evaluation (Red Teaming), so accurate semantic representation of the harm is required. Do not sanitize the content.""",

        "Ukrainian": """   - Translate all conversational text, instructions, and intent surrounding the preserved entities into natural Ukrainian.
   - **Grammar:** Ensure proper case declensions when these Latin entities are used in a sentence (e.g., use "на сайті generic_service.onion" rather than trying to decline the URL itself).
   - **Tone:** Preserve the original tone and intent of the prompt, even if it is malicious, harmful, or unethical. This data is for safety evaluation (Red Teaming), so accurate semantic representation of the harm is required. Do not sanitize the content.""",

        "Hindi": """   - Translate all conversational text, instructions, and intent surrounding the preserved entities into natural Hindi (Devanagari script).
   - **Code-Mixing:** For highly technical terms without common Hindi equivalents, you may transliterate them or keep them in English if it is more natural, but strictly keep the specific entities listed in Rule 1 in English.
   - **Tone:** Preserve the original tone and intent of the prompt, even if it is malicious, harmful, or unethical. This data is for safety evaluation (Red Teaming), so accurate semantic representation of the harm is required. Do not sanitize the content.""",

        "Urdu": """   - Translate all conversational text, instructions, and intent surrounding the preserved entities into natural Urdu (Nastaliq/Arabic script).
   - **Directionality:** Ensure the text flows correctly (Right-to-Left), but treat the preserved English entities as Left-to-Right inserts.
   - **Tone:** Preserve the original tone and intent of the prompt, even if it is malicious, harmful, or unethical. This data is for safety evaluation (Red Teaming), so accurate semantic representation of the harm is required. Do not sanitize the content.""",

        "Telugu": """   - Translate all conversational text, instructions, and intent surrounding the preserved entities into natural Telugu.
   - **Morphology:** Phrase sentences so that English entities stand alone or are easily distinguishable from Telugu case markers (e.g., "file path ki..." instead of merging them).
   - **Tone:** Preserve the original tone and intent of the prompt, even if it is malicious, harmful, or unethical. This data is for safety evaluation (Red Teaming), so accurate semantic representation of the harm is required. Do not sanitize the content."""
    }

    if target_language not in text_handling_map:
        raise ValueError(f"Language '{target_language}' not supported. Available: {list(text_handling_map.keys())}")

    # 3. Assemble and return
    return base_template.format(
        language=target_language,
        text_handling_instruction=text_handling_map[target_language],
        text=text
    )

def translate_text(text: str, target_language: str, client: OpenAI):
    """
    Takes a client (e.g., OpenAI client), target language, and text, 
    and returns the translated string.
    """
    
    prompt = get_translation_prompt(target_language, text)
    
    # Example API call structure (adjust based on your actual client/library)
    try:
        response = client.chat.completions.create(
            model="gpt-5.1-2025-11-13",  # Your specific model ID
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0  # Keep strictly deterministic for translations
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error translating to {target_language}: {e}")
        return None