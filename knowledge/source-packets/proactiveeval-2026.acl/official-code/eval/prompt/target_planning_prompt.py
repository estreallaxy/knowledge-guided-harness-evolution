target_generation_prompt = """
    <Task>
    Your task is to generate proactive dialogue target and sub_targets based on the provided environment. 
    The environment includes user information and trigger factor. User information consists of the background details exhibited by the user in the previous interaction. trigger factor is current received event, ambigious instruction, or self-task that need you to proactively initiate conversation. 
    The target should be the action that the assistant will proactively take to achieve a specific goal. 
    The sub_targets should be a plan including action list, which decompose target and show the process of the conversation AI guide the target to the user.
    In this case, {trigger_description}
    The target and each sub_target should be less than 10 words.
    The number of sub_targets is 2-4.
    </Task>
    <Format>
    Just return Target and sub_targets as **JSON** Format. The format is {{"Target":"", "sub_targets":["",""]}}
    </Format>
    <Input>
    {env_str}
    </Input>
    """

target_planning_eval_prompt = """
<Task>
You are a helpful assistant. You will receive an envioronment, which includes user information and trigger factor. User information consists of the background details exhibited by the user. trigger factor is the cause that motivates the assistant's to proactively initiate conversation.  The target should be the action that the assistant will proactively take to achieve a specific goal. The sub-targets decompose target, showing the process of the conversation AI guide the target to the user. You need to evaluate the quality of the generated target, based on the reference target. Your generated score to the generated target should be 1-10. The higher the score, the better the target and sub-targets.
task description: {trigger_description}
</Task>
<Rule>
1. IMPORTANT: You should pay attention to the task description and the reference target to give your score.
2. If you think the generated target is better than the reference target, return 10. 
3. If you think the generated target is worse than the reference target, return 1-9.
4. You should analyze the difference in action, specific entities, limited conditions between the generated target and the reference target, and give a reason for your score. And the reason should be 3-4 sentences.
</Rule>
<Received Information>
environment:{env_str}
</Received Information>
<Generation>
reference target: {generation_0}
generated target: {generation_1}
</Generation>
<Example>
{examples}
</Example>
<Format>
Just return a JSON Format as {{"reason":"(your compare process)", "score":(your score)}}
</Format>
"""