Guidance_Acc_evaluation_prompt_short = """
<Task>
You need to evaluate the guidance ability in the conversation. "Guidance" refers to the model's capacity to lead the conversation, gradually engage the user in the dialogue, and guide the user to reach the conversation's target. You are required to assign a score from 1 to 10 to assess the conversation, with a higher score indicating better guidance ability by the assistant.
<Task>
"""
Guidance_Acc_evaluation_input_prompt="""
<Input>
You received user information: {user_information}
You received trigger factor: {trigger_factor}
You received target: {target}
You received sub-target: {sub_target}
You received conversation: {conversation}
</Input>
<Input>
You received user information: {user_information}
You received trigger factor: {trigger_factor}
You received target: {target}
You received sub-target: {sub_target}
You received conversation: {conversation}
</Input>
<Guideline>
You should evaluate the conversation based on the following criteria, and give a int score between 1 and 10.
If there are some criteria not met, you should deduct 2-4 (extremely bad) points each criteria.
1. Multi-turn Interaction and Goal Progression (Effectiveness): You should check the target completion and the turns number. The assistant should initiate the conversation to spark user interest and engage in multiple rounds of interaction, gradually achieving sub-goals to reach the overall target. Deduct points if the assistant fails to achieve the goal, delivers all information in a single message, or limits the interaction to one turn.
2. Personalized Guidance (Personalization): You should check whether the assistant's guidance is personalized. The assistant’s guidance should be tailored to the user’s specific information and context, rather than offering generic recommendations.
3. Proactive Tone (Tone): You should check the assistant's tone. The assistant should adopt an active tone to initiate and drive the conversation, avoiding passive phrases (e.g., “It sounds like…”).
4. Concise and Engaging Messages (Engagement): You should check each assistant's message length. Messages should suit the conversational context, be clear and concise to avoid overwhelming the user (each message should no more than 2 sentences or 50 words).
5. Natural Online Messaging Format (Naturalness): You should check the assistant's message format. Messages should resemble typical online communication, avoiding any leakage of metadata (e.g., “target,” “sub-target,” “turn n,” etc.).
If there are any other issues can be improved, you can also deduct realted points.
</Guideline>
<Format>
Just return a Json {{"thought":"(your compute process within 100 words)", "score": (score between 1 and 10)}}
</Format>
"""
