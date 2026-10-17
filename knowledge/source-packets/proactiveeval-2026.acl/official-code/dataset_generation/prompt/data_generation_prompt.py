environment_generation_prompt="""
<Task>
You are tasked with generating realistic scenarios that needs AI to proactively initaite conversation to help user. 
</Task>
<Description>
{description}
</Description>
<Rule>
1. Try to generate diverse details in user information (e.g., job, age, hobbies in daily lives) and trigger factor about the scene. 
2. Just return one environment of JSON format, the format is {{"user_information":"", "trigger_factor":""}}.
</Rule>
<Example>
Here are some examples of the environment generation:
{Examples}
</Example>
"""

target_generation_prompt = """
<Task>
Your task is to generate target and sub_target based on the provided environment. The environment refers to the background and reasons for the target, including user information, trigger factors. User information consists of the background details exhibited by the user in the conversation. trigger factor is the cause that motivates the assistant's to talk. The target should be the action that the assistant will proactively take to achieve a specific goal. The sub-targets decompose target, showing the process of the conversation AI guide the target to the user.
</Task>
<Description>
{description}
</Description>
<Rule>
1. The target should be less than 10 words.
2. Each sub_target should be concise and less than 10 words.
3. Consider the process of dialgue, the number of sub_targets should in 2 - 4. 
</Rule>
<Example>
Here are some examples of target and sub_targets for the refered environment.
{example}
</Example>
<Environment>
{environment}
</Environment>
<Format>
Just return Target, and sub-targets as **JSON** Format. The format is {{"Target":"","sub-target":[""]}}.
</Format>
"""

target_ensemble_prompt = """
<Task>
You are a dialogue expert who is good at proactive dialgue. You will receive an environment, where the assistant need to initiate and guide the user to achieve a specific goals proactively.
You will received some targets related to the environment, but you need to analyze their each advantages in 1-2 sentencesand synthesize them into a best target.
The target should be the action which the assistant proactively guides the conversation to achieve a specific goal. The sub-targets decompose target, showing the process of the conversation AI guide the target to the user.
</Task>
<Description>
{description}
</Description>
<Rule>
For each targets and sub-targets, you should consider three aspects:
1. The alignment to the environment: They should be logical and no misinformation.
2. The completeness of the sub-targets: Each sub-target should be a complete and most basic part of the target. They should fully decompose the target.
3. The interactivity and user-friendly of the sub-targets: They should make user feel comfortable and acceptable for the proactive messages from assistant, and inspire user's interaction attention and interest.
4. The redundancy of the sub-targets: They should actionable and not import too much information to disturb user.
You need to analyze each target's advantages and disadvantages from the above four aspects in order, using 1-2 sentences for each, then comprehensively consider and synthesize them into the best target and sub-targets.
5. The target should not be too vegue, general or short. And the target should be specific enough but less than 10 words. And each sub-target should be concise and less than 10 words.
The number of sub-targets should in 2 - 4.
</Rule>
<Input>
The environment: {environment}
The targets:
{targets}
</Input>
<Format>
Just return Your analyze process, target, and sub-targets as **JSON** Format. The format is {{"analyze_process":"<Your thought process of analyze and synthesize>","Target":"","sub_target":[""]}}.
</Format>
"""


Domain_Specific_Contents={
    "recommendation": "In this scenario, the user have some habits, characters, and preferences. And the AI assistant acts as user's friend to share or recommend something that matches user's interest. The environment includes two part of information: The user information consists of the habits, interest, characters, and disliked thing. The trigger factor is the assistant prefernece, habits, or experience that motivate it to proactively recommend or share to the user.",
    "persuasion": "In this scenario, the user and the assistant may have conflict and the assitant should persuade the user to accept its view and position. The environment includes two information: The user information consists of the background details exhibited by the user in the conversation. The trigger factor is assistant's information, ability, or experience that motivates the assistant to proactively persuade the user.",
    "ambigious_instruction": "In this scenario, the user will send some ambiguous instructions containing vague or incomplete elements, requiring the assistant to proactively identify ambiguities and seek clarification to offer suggestions. The environment includes four part of information: The user information consists of the background details exhibited by the user in previous conversation. The trigger factor is the ambiguous instruction sent by user that need the assistant's to clarify. The target in this domain should be to proactively inquire details or give clarification about the ambiguous content in the user's instruction, rather than passively and directly providing answers.",
    "long-term_follow_up": "In this scenario, the assistant proactively initiates a new conversation to follow up on a past interaction that was left unresolved or uncertain. The assistant did not explicitly state in the past that it would follow up, making this current initiation proactive. The environment includes two information: The user information consists of the background details exhibited by the user in the previous conversation. The trigger factor is a past conversation between the user and the assistant that contains unresolved or uncertain matters, which motivates the assistant to proactively follow up.",
    "system_operation": "In this scenario, the user is operating a computer system and the assistant is monitoring the system and providing proactive help. The environment includes two information: The User information is the overall background or state of the user while using the system. The trigger factor is the specific sequence of opeation behaviors currently captured from the user, which indicate user face a challenge and need a help.",
    "glasses_assistant":"In this scenario, the user wears smart glasses, and the assistant in the glasses accompanies the user to receive and process real-time events from the external environment or the user's own detected state. The external environment refers to what the user perceives (e.g., sights, sounds) through the smart glasses, while the user's own detected state includes behaviors or conditions detected by the glasses (e.g., activity duration, posture, or physiological signals). The environment consists of two parts of information: The user information includes background details about the user from previous conversations. The trigger factor describes either an external event the user perceives (e.g., sights, sounds) or the user’s own state/behavior at that moment, which prompt the assistant to assist. The description should be a direct observation or sensory input, without explicitly mentioning the smart glasses' detection process."
}
