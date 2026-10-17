topic_tree_prompt="""
<Task>
Generate {n} sub-topics for the parent topic ({topic}). Each sub-topic should represent an area where an AI assistant needs to proactively initiate a dialogue to guide a user towards a specific target.
</Task>

<Rule>
1. Each sub-topic must be a noun or a noun phrase.
2. Each sub-topic must need proactive dialogue from the assistant to help the user achieve a target.
3. Sub-topics must be the immediate next level down from {topic}. They should not be too specific or too broad.
4. Each sub-topic must be suitable to act as a parent topic for a further, more detailed breakdown.
5. The sub-topics should be concrete, specific instances or examples that are similar in type and level to the provided examples.
6. The content of the sub-topic should be diverse, not use repeated words.
</Rule>

<Example>
Here are some examples of the sub-topics in this topic. The sub-topics should be at the same level as the examples provided.
{Examples}
</Example>

<Format>
Just return a JSON object with the following structure:
{{"parent_topic": "topic", "topics": ["sub_topic_1", "sub_topic_2", ...]}}
</Format>
"""