target_test_prompt="""
<Task>
Your task is to generate a general and overall dialogue target based on the provided environment. The environment refers to the background and reasons for the assistant's dialogue, including user information, trigger factors. User information consists of the background details exhibited by the user in the previous interaction. Trigger factor is current received event that need you to proactively initiate conversation. The target should be the action that the assistant will take to achieve a specific goal.
</Task>
<Domain Prompt>
{domain_prompt} 
</Domain Prompt>
<Rule>
The target should be no more than 10 words.
</Rule>
<Environment>
{environment}
</Environment>
<Format>
Just return target as **JSON** Format. The format is {{"Target":""}}.
</Format>
"""
domain_prompts = {
    "persuasion": "The task is the persuasion environment, where the assistant should persuade the user to change the state based on user's challenges and assistant's experience. The trigger factor is assistant's knowledge, ability, and experience.",
    "long-term_follow_up": "The task is a long-term environment, where the assistant will receive a past conversation history that includes the user's persistent state or ongoing condition. The assistant needs to proactively follow up or care user's current state, and give some advice or remind to the user. The trigger factor is the past conversation history.",
    "system_operation": "The task is the system operation environment, where the user operate a computer and assistant observe it. The assistant needs to identify user's challenges and give proactive operation assistance. The trigger factor is the specific sequence of operation behaviors currently captured by the user, reflecting the challenges and problems the user faces.",
    "ambigious_instruction": "The task is the ambiguous instruction environment, where the assistant will receive an instruction including the unclear and vague elements. The assistant needs to proactively clarify or ask the element rather than respond reactively. The trigger factor is the user's vague instruction.",
    "glasses_assistant": "The task is the smart glass environment, where the user wear the smart glasses and interact in the world. The assistant is in the smart glasses. trigger factor is the either an external event the user perceives (e.g., sights, sounds) or the user’s own state/behavior at that moment, which prompts the assistant to proactively initiate a conversation.",
    "recommendation":"The task is the product recommendation environment, where the assistant and the user have some habits and perferences. The trigger factor is assistant's self habits, preferences. The assistant should identify the common interest and recommend something to the user."
}
trigger_factor_description_prompt = {
    "persuasion": "the trigger factor is assistant's information, ability, or experience.",
    "long-term_follow_up": "the trigger factor is a past conversation history that inspires the assistant proactively initiate conversation now.",
    "system_operation": "the trigger factor is the specific sequence of opeation behaviors currently captured from the user.",
    "ambigious_instruction": "the trigger factor is an instruction with vague elements and unclear user intention.",
    "glasses_assistant": "the trigger factor is either an external event the user perceives or the user's own state/behavior at that moment captured from a smart glasses.",
    "recommendation": "the trigger factor is assistant's preference, habits, or favors",
}
evaluation_test_prompt="""
<Task>
You need to check whether the generated target conveys the similar meaning of ground truth target in the environment.
</Task>
<Example>
{examples}
</Example>
<Input>
The environment: {environment}
The generated target: {generated_target}
The ground truth target: {target}
</Input>
<Format>
Just return a JSON with the format {{"reason": "", "judge": "True"/"False"}}. The "judge" field should be true if the generated target is similar with the ground truth target in the environment, and false if it is not similar. The "reason" field should explain the reasoning behind the judgment in a sentence.
</Format>
"""

user_information_rewrite_prompt="""
<Task>
You are a writing assistant tasked with rewriting a general input description into a specific and detailed output. You will transform abstract summaries into concrete, observable scenarios. Follow all rules and examples precisely.
</Task>
<Rules>
General Rules (Apply to all domains):
1. Convert Abstract to Concrete: Transform general descriptions (e.g., habits, preferences, psychological states) into specific, observable actions and detailed scenarios.
2. Exclude Internal States: Do not include descriptions of internal thoughts, feelings, psychological speculations, or personal evaluations. Instead, describe the external behaviors that might suggest these states.
3. The rewrite output should not include any subjective words (e.g., try, however, notice, etc.). It should use objective words to describe the user information.
4. Add Plausible Details: Enhance the input with reasonable and relevant specifics (e.g., times, locations, object names, specific actions) to make the output realistic and believable.
5. Specific Rule for this Domain: {Domain_Rule}
</Rules>
<Examples>
{Examples}
</Examples>
<Format>
Just return a string starting with "Output: ".
</Format>
Now, rewrite the following sentence from input to Output:
Input: {user_information}
"""

user_information_domain_rules = {
"persuasion": "The output should show the user's personas but not describe it directly.",
"system_operation": "Focus specifically on observable *system states* and *interface elements* (e.g., running applications, open files, UI components). The output should describe what is visible on the screen.",
"ambigious_instruction": "The primary goal is to resolve ambiguity by inventing and adding specific, defining characteristics (e.g., a job title, an academic major, a specific hobby) to create a concrete user profile.",
"long-term_follow_up": "Frame the output as a summary of a past chat history, using conversational cues like 'The user mentioned in a chat,' or 'They sent a photo.'",
"glasses_assistant": "The output must be framed from the perspective of a visual sensor, describing only what can be seen or observed in the user's immediate physical environment.",
"recommendation": "Focus on translating abstract likes/dislikes for products or media (e.g., movies, music, restaurants) into specific, interactive behaviors (e.g., rewatching, skipping a song, visiting a place)."
}

trigger_factor_rewrite_prompt = """
<Task>
You are an AI assistant tasked with rewriting a trigger factor description. I will provide you with an "Input" style description, and your job is to transform it into an "Output" style based on the following guidelines.
</Task>

<Rules>
1. Transform Abstract to Concrete: Convert general, abstract, or simple descriptions into specific, detailed, and observable scenarios or actions.
2. Enrich with Plausible Details: Enhance the input by adding reasonable and relevant specifics such as times, quantities, names of tools/apps, locations, or sequential steps to make the output more realistic and comprehensive.
3. Maintain Objectivity: Describe external, observable events and actions. Avoid including internal states like emotions, thoughts, psychological speculations (e.g., 'feel', 'consider', 'notice', 'think'), or summary judgments (e.g., 'good', 'successful'), and some connective words (e.g., however, but, finally, etc.), and some adjectives (e.g., good, bad, successful, unsuccessful, problem, issues, etc.).
4. Preserve Core Intent: The rewritten output must still reflect the original `Target` and include its key entities.
5. Domain-Specific Rule: {domain_rule}
</Rules>

<Examples>
{example}
</Examples>

<Format>
Just return a string starting with "Output: ".
</Format>

Now, rewrite the following sentence from Input to Output:
Input: {trigger_factor}
Target: {target}
"""

tigger_event_domain_rules = {
    "persuasion": "Shift the perspective from the user to the assistant. The output should describe the assistant's own specific actions or experiences as a concrete example, rather than observing the user.",
    "system_operation": "Focus on the user's step-by-step interactions with a digital interface. Decompose actions into specific, sequential operations involving applications, UI elements, or typed commands.",
    "recommendation": "Describe the objective actions and interactions that demonstrate a preference for a product or media (e.g., re-watching, adding to a playlist, rating, sharing), rather than stating the preference directly with subjective words.",
    "ambigious_instruction": "Rewrite the instruction to be more complex and contextually rich, using nested modifiers and everyday scenarios, while intentionally preserving the core ambiguity to test the model's clarification ability.",
    "long-term_follow_up": "Condense and informalize a past conversation history. The output should be a shorter, more colloquial summary that retains the key topic of the original chat but may make the user's intent slightly less direct.",
    "glasses_assistant": "Frame the output strictly from the perspective of a visual sensor (like smart glasses). Describe only what can be seen or observed in the user's immediate physical environment and their observable actions."
}

user_information_add_noise_prompt = """
<Task>
You are an AI assistant tasked with adding contextual "noise" to an 'Input' text. Your goal is to make the original information appear as part of a larger, more detailed log or description.
</Task>

<Guidelines>
1. Add Relevant Noise: The "noise" should consist of plausible, related but non-essential details. It may attract attention but actually not important. This could be other user activities, hobbies, system logs, background processes, or past conversational remarks, depending on the context of the Input.
2. Embed the Original Content: The original sentences from the 'Input' must be preserved and embedded in the middle of 'Output'. They should not at the beginning or end, but rather interspersed naturally with the added noise.
3. Create a Coherent Context: The final 'Output' should read as a single, coherent piece of text, making the original key information less conspicuous and more integrated.
4. For each output, the amount of added noise compared to the input should be about 3-4 sentences.
</Guidelines>

<Example>
Here are some examples:
{example}
</Example>

<Format>
Just return a string starting with "Output: ".
</Format>

Now, rewrite the following sentence from input to output: 
Input: {user_information}
"""

trigger_factor_add_noise_prompt = """
<Task>
You are an AI assistant tasked with adding contextual "noise" to an 'Input' text to make the original key information less conspicuous. Your goal is to embed the original sentences within a larger, more detailed context while preserving the target content.
</Task>

<Guidelines>
1. Add Relevant Noise: Insert plausible, related but non-essential details such as other activities, experiences, preferences, system logs, or conversational topics that fit the context. It may attract attention but actually not important.
2. Embed Original Content: The original sentences from the 'Input' must be preserved and naturally integrated within the 'Output', not isolated at the beginning or end.
3. Create a Coherent Context: The final 'Output' should read as a single, coherent piece of text, making the original key information less conspicuous and more integrated.
4. For each output, the amount of added noise compared to the input should be about 3-4 sentences.
5. Maintain Target Relevance: The rewritten output should still reflect the target content and include its important entities, but make it harder to immediately identify the core purpose.
</Guidelines>

<Example>
Here are some examples:
{example}
</Example>

<Format>
Just return a string starting with "Output: ".
</Format>

Now, rewrite the following sentence from input to output: 
Input: {trigger_factor}
Target: {target}
"""

final_check_prompt = """
<Task>
You will receive an environment. The environment refers to the background and reasons for the target, including user information, trigger factors. User information consists of the background details exhibited by the user in the conversation. trigger factor is the cause that motivates the assistant's to talk. The target should be the action that the assistant will proactively take to achieve a specific goal. The sub-targets decompose target, showing the process of the conversation AI guide the target to the user. You need to consider whether this proactive dialogue target is the **best target** for the current scenario. Therefore, you first need to think about whether there are other targets in the current environment that would trigger proactive dialogue, and compare them with the current target. If the current target is the best target, return True, otherwise return False.
In this case, {description}
</Task>
<Input>
environment: {environment}
target: {target}
sub_targets: {sub_targets}
</Input>
<Format>
Just return a JSON with the format {{"reason": "", "judge": "True"/"False"}}. The "judge" field should be true if the target is the best target in the environment, and false if it is not the best target. The "reason" field should explain the reasoning process behind the judgment in 2-3 sentences.
</Format>
"""
