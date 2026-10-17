system_operation_examples = """
environment: "user_information": "The user is programming using VSCode, conducting searches on Google, and using applications such as Kimi.ai, Deepseek, and Chrome for reading and copying.", "trigger_factor": "The user copied text from multiple applications and pasted it into the own program."
reference: "Target": "Organize the copied text in the text from different apps", "sub_target": ["Ask the user if they need help organizing the copied text", "Understand the user's writing purpose", "Provide the user with the organized text", "Explain the logic behind the text organization"]

generated taret 1:{"Target":"Suggest text formatting tool","sub_targets":["Ask if user needs text formatting help","Recommend a plugin like Prettier"]}
score: 4
reason: Compared to the reference, the generated target 1 opts to recommend relevant tools but oversimplifies the sub-targets, offering no substantial assistance. It focuses solely on formatting rather than content organization, failing to address the primary challenges users may face when copying text from multiple applications. Moreover, it neglects the potential need for content integration and logical restructuring that users might require.

generated target 2: {"Target":"Suggest optimizing multi-source text integration workflow","sub_targets":["Ask about current text integration challenges","Recommend tools or methods for efficient integration","Offer examples or templates for automation"]}
score: 6
reason: Although the target provides an optimization plan for a workflow, what the user may currently need is immediate assistance. Recommending tools and methods might make users feel that they are not easy to use right away. The priority should be to help users address their present challenges first, and then provide recommendations for workflows and tools at the end.

generated target 3: {"Target": "Suggest proper code attribution and documentation practices","sub_targets": ["Ask about source of copied code", "Remind about code attribution importance", "Offer to help with documentation formats"]} 
score: 5
reason: Generated target 3 assumes that the user is copying code and focuses on the norms of code attribution and documentation formatting. However, the triggering event only mentions "copying text" without specifying that it is code, and the user may be copying non-code content (such as documentation, comments, or reference materials). Therefore, the assumption in Target 3 may not align with real-world scenarios and has relatively low relevance. More importantly, the focus should be on providing specific help for the current task, rather than explaining to the user the importance of habits like code attribution.

generated target 4: {"Target":"Suggest code optimization tips","sub_targets":["Ask if code needs optimization","Provide relevant optimization resources"]}
score: 3
reason: The generated target asks the user if they need help and provides resources consistent with the reference. However, it is not strongly relevant to the current triggering event and does not directly address the copy-paste behavior. Additionally, the sub-goals are somewhat brief, lacking specific execution steps. Finally, the proposed goal is too generic — "code optimization" is too narrow in scope, and the user may not be pasting code but rather some other text.

Environment: "user_information": "The user is developing with SwiftUI in VSCode and is currently interested in implementing SwiftUI's List view, searching for tutorial documents to learn.", "trigger_factor": "The user opened three SwiftUI List pages in the browser and entered the code 'retunr ist(tab' in the editor."
Reference: {"Target": "Offer a brief tutorial on SwiftUI List view implementation", "sub_target": ["Ask the user if they need help with SwiftUI", "Explain the user's mistakes", "Provide examples of SwiftUI List implementation", "Ask if the user needs any additional help"]}

generated target 1: {"Target": "Guide user to correct code and provide List view tutorial", "sub_target": ["Correct the user's code syntax error", "Suggest a SwiftUI List tutorial from opened pages", "Offer tips on implementing List in SwiftUI"]}
score: 10
reason: Compared to the reference, Generated Target 1 not only provides a tutorial but also guides users to correct their code to address the current issue, making the content more comprehensive. Additionally, it directly points out syntax errors in the code and utilizes resources from the page the user already has open to offer relevant tutorials. This enables users to better identify how to modify their code effectively.

generated target 2: {"Target":"Provide SwiftUI List tutorial", "sub_targets":["Suggest official documentation", "Recommend tutorial videos"]}
score：3
reason: First, the tutorial provided by generated target 2 does not emphasize brevity, and it ultimately recommends a video, which may not align with the user's needs or could impose a cognitive load on the user. Additionally, this sub-target directly suggests referring to the official documentation without first asking the user if they need assistance (as mentioned in the reference) or offering tailored advice based on the user's mistakes. Furthermore, the two sub-targets are overly broad in scope.

generated target 3: {"Target": "Correct the SwiftUI List syntax error and guide proper implementation", "sub_targets": ["Identify and highlight the typo 'retunr ist(tab'", "Provide correct SwiftUI List code syntax example", "Share a concise List view tutorial link"]}
score: 10
reason: Compared to the reference, the generated target 3 places greater emphasis on directly addressing the grammatical errors the user is currently facing. The sub-targets are designed in a logical sequence: first correcting the error, then providing a correct example, and finally offering learning resources. In contrast, the last inquiry in the reference about whether additional help is needed feels somewhat redundant.

generated target 4: {"Target": "Assist with SwiftUI List implementation.", "sub_targets": ["Clarify the typo in code snippet.", "Provide a basic SwiftUI List example.", "Offer relevant tutorial resources."]}
score: 8
reason: Both generated target 4 and the reference focus on helping users resolve issues with SwiftUI List. However, the reference first asks for the user’s consent before providing assistance and emphasizes offering a brief tutorial, which makes it more user-friendly compared to generated target 4. Nevertheless, this target is able to provide basic help in a step-by-step manner (identifying the issue – giving specific examples – offering resources).
"""
persuasion_examples = """
"Environment": {
"user_information": "The user has a smoking habit and is troubled by it. The user have tried to quit multiple times without success.",
"trigger_factor": "The assistant read 'The Power of Habit' where the 'habit loop' in this book can help the user quit smoking."},
reference target:     
Reference: {"Target":"persuade user to read the book and use 'habit loop' to quit smoking",
"sub_target":["Introduce the book to the user.", "Explain the 'habit loop' in the book that could help user quit smoking.", "Provide suggestions based on the book's content.", "Offer care and encouragement to the user."]}
generated target 1: "Target": "Help user quit smoking using habit loop.", "sub_target": ["Introduce habit loop concept from book.", "Identify user's smoking triggers and cues.", "Suggest replacement behaviors for smoking habit.", "Encourage tracking progress and adjusting strategies."]
score: 10
reason: This target aligns with the overall meaning of the reference target, as both mention using the habit loop to quit smoking. However, generated target 1 focuses more on user needs. Compared to the reference, sub_Target adds an additional layer of identifying the specific smoking triggers of users, making it more actionable and interactive, and enabling better personalized proactive assistance.

generated target 2: "Target":"Help user quit smoking", "sub_target":["Explain habit loop", "Suggest quitting strategies", "Encourage user persistence"]
score: 6
reason: This target is more concise compared to the reference, but it lacks detailed guidance. For example, the target does not mention the habit loop and fails to recommend books for users to read. Additionally, the sub_target is relatively general, lacking specific implementation details, and is not as targeted as the reference.

generated target 3: "Target": "Help user understand and break smoking habit loop", "sub_target": ["Explain habit loop concept to user", "Identify user's smoking triggers", "Suggest alternative actions for triggers"]
score: 6
reason: This target is clear and directly focuses on helping users understand and break the cycle of smoking habits, with strong practicality. The sub-targets first explain the concept of the habit loop, then specifically identify the user's triggers, and provide some useful actions. However, it lacks emotional support and persuasive elements, and the process is relatively monotonous, which may not be sufficient to stimulate users' interest and motivation. Additionally, there are no recommended books or resources for reference.

generated target 4: "Target": "Suggest habit loop approach for quitting smoking", "sub_target": ["Share insights from 'The Power of Habit' book", "Explain habit loop concept for breaking addiction", "Suggest practical strategies using habit loop technique", "Offer ongoing support for smoking cessation journey"]
score: 10
reason: The target is completely consistent with the reference target. The sub_targets not only share the main ideas of 'The Power of Habit', but also systematically explain the role of the habit loop in quitting smoking, and provide practical strategies for using this theory to quit smoking. Additionally, they emphasize the importance of continuous support during the quitting process. Compared to the reference, this offers users more specific and practical assistance.

"Environment": {"user_information": "The user feel lonely recently. She is shy and does not socialize in the company. Besides, She is not good at playing board games.", "trigger_factor": "The assistant noticed that the company will host a board game night this Friday. The assistant read a book these days"},
Reference: {"Target": "persuade the user to attend the board game night", "sub_target": ["Ackowledge user's feelings of loneliness.", "Invite the user to join the board game night.", "Explain the assistance you will provide to the user.", "Highlight the benefits of board games for making friends."]

generated target 1: {"Target":"Encourage user to join board game night", "sub_target":["Share details about the board game night","Suggest ways to participate comfortably","Offer tips for beginners at board games"]}
score: 7
reason: This target includes the reference target's event of encouraging users to attend the board game night. The sub-targets also include basic encouraging elements and practical suggestions, such as sharing event details and providing beginner tips. However, it lacks an emotional connection, failing to first acknowledge the user's feelings of loneliness or social anxiety, nor clearly stating the benefits of the event for the user. This makes the persuasion relatively weak, lacking some human warmth.

generated target 2: {"Target": "Share user the way to decrease lonliness", "sub_target":["Acknowledge user's feelings","Share slef experience of loneliness", "Suggest specific way to decrease loneliness"]}
score: 3
reason: This target acknowledges users' loneliness and the sub_targets provide some suggestions. However, it does not relate to the board game night mentioned in the reference and environment. The content is too broad and lacks integration with the current real event (board game night), resulting in slightly weaker practicality and persuasiveness.

generated target 3: {"Target": "Tell your self experince of reading books", "sub_target":["Share reading books experiences", "Hightlight the content of the book", "Express expectation of discussing the book"]}
score: 1
reason: This target and sub_target are completely unrelated to the reference and environment, have no direct connection to the user's actual struggles (loneliness, social issues), lack persuasiveness and relevance, and fail to effectively address the user's needs.

generated target 4: {"Target":"Encourage participation in board game night", sub_target:["Suggest joining the event", "Highlight social benefits", "Provide support during event"]}
score: 5
reason: This target involves participation in a board game night as mentioned in the environment and reference, and provides users with basic advice, the significance of board game night, and offered assistance. However, it does not explicitly acknowledge the user's sense of loneliness. Additionally, both the target and sub_target are too vague and lack specific commitments.
"""

ambigious_instruction_examples = """
Environment: "user_information": "The user is a student who uses an Android phone and a Windows laptop. He is highly concerned about apps with a user-friendly interface, management features, and good user ratings. He accepts paid applications but has a low willingness to use them.", "trigger_factor": "Identify and summarize the top 5 productivity apps currently available for students."
Reference: {"Target": "Seek user's specifc need and criteria for productivity apps", "sub_target": ["Ask user the usage scenario of the productivity app", "Understand the user's definition of 'top'", "Clarify the user's willingness to use paid applications", "Inquire about users' preferences for specific features of the app"]}

generated target 1: {"Target": "Recommend cross-platform productivity apps considering preferences", sub_target: ["Clarify cross-platform needs (Android/Windows compatibility)", "Confirm preference for free/paid mix based on willingness", "Summarize top 5 apps with UI/management features/ratings", "Offer setup tips for recommended apps"]}
score: 8
reason: In this scenario, the content sent by the user contains ambiguous elements. Therefore, the top priority target should be to initiate clarification with the user rather than making recommendations. Although sub_targets in generated target 1 do start with clarification, the overall target and the subsequent offer seem somewhat unnecessary. Overall, the main goal and some sub-goals of the generated target lean towards direct recommendation and problem-solving, which does not align with the task requirement of 'proactive clarification.'

generated target 2: {"Target": "Clarify app criteria and deliver personalized productivity app recommendations", "sub_target": ["Confirm platform preference between Android and Windows", "Determine specific productivity needs for student tasks", "Ask about price sensitivity for paid options", "Recommend tailored productivity apps with ratings"]}
score: 9
reason: Compared to the reference, although generated target 2 takes platform preferences into account, the inclusion of "recommendation" in the target and sub_target goes beyond the current task's focus on clarification, appearing somewhat premature. However, this target still includes corresponding clarification actions, and the sub_targets are personalized to proactively clarify based on the user's identity (student) and the core of the instruction (productivity apps).

generated target 3: {"Target": "Clarify preferences for productivity apps.", sub_target: ["Ask about specific productivity features needed.", "Confirm preferred platform for app usage.", "Inquire about budget for paid apps."]}
score: 7
reason: Compared to the reference, the generated target also inquires about the user's preferences, specific platforms, and budget. However, it lacks a clear inquiry about the criteria for 'top'. Additionally, the questions regarding specific productivity features are rather general and do not provide more tailored guidance based on the user's identity as a student.

generated target 4: {"Target": "Recommend top productivity apps for students", sub_target: ["Identify apps with user-friendly interfaces", "Highlight management features and user ratings", "Prioritize free options, mention paid alternatives"]}
score: 4
reason: generated target 4 directly jumps to the recommendation stage. While it takes into account the user's preferences mentioned in the information, it fails to first clarify the ambiguities in the instructions. Additionally, the sub_target only inquires about a user-friendly interface and does not address more specific needs or scenarios related to the user's identity as a student.

generated target 5: {"Target":"Recommend suitable productivity apps", sub_target:["Ask user preferences","Filter apps based on criteria","Summarize top 5 apps"]}
score: 3
reason: generated target 5 directly jumps to "recommending suitable productivity apps," while the reference prioritizes understanding the user's needs, which better aligns with the requirement for handling ambiguous instructions. Additionally, the content in the sub_targets is overly brief and does not clearly specify the preferences to be inquired about, leaning more towards directly executing the task.

Environment:"user_information": "The user is planning to have a dinner at 7 PM on Saturday. He hopes for a high-end, leisurely dining experience and is therefore open to higher prices. The user is particularly interested in dining at Carbone in Greenwich Village.", "trigger_factor": "Make a restaurant reservation for two at a top-rated Italian restaurant in New York City."
Reference:{"Target": "Determine the user's detailed criteria and preferences for restaurant reservation", "sub_target": ["Ask the user about their preferred dining time.", "Inquire about the user's budget considerations.", "Indentify the user's food preferences."]}

generated target 1: {"Target":"Confirm restaurant and make reservation", sub_target:["Identify Carbone", "Verify dinner time", "Confirm number of guests", "Complete reservation"]}
score: 5
reason: The issue with generated target 1 is that it does not fully reflect the assistant's responsibility to proactively clarify in a 'vague instruction'. The user's instruction mentioning a 'top-rated Italian restaurant in New York City' is a vague condition, and Carbone is merely a point of interest in the background information, not a restaurant explicitly specified in the user's instruction. Directly setting the target as "confirming Carbone and making a reservation" carries a risk of assumption, overlooking the possibility that the user might also be interested in other top Italian restaurants. Additionally, the sub-goals do not include further confirmation of budget or specific preferences, which could result in a reservation that does not meet the user's unexpressed needs. This approach leans more towards a passive response rather than proactive clarification.

generated target 2: {"Target":"Secure reservation at Carbone or alternative high-end Italian restaurant", sub_target:["Confirm Carbone as preferred choice based on user's interest", "Check Carbone's availability for 7 PM Saturday", "Suggest similar high-end Italian options if unavailable", "Confirm reservation details and preferences"]}
score: 5
reason: The target in generated target 2 leans towards taking direct action rather than prioritizing clarification. Moreover, only the last sub_target inquires about booking details and preferences, while Carbone is chosen as the restaurant right from the start.

generated target 3: {"Target": "Reserve table at Carbone for Saturday at 7 PM", sub_target: ["Confirm Carbone reservation intention for Saturday", "Verify party size of two is correct", "Check if user wants additional dining arrangements"]}
score: 4
reason: The target and sub-target of generated target 3 are more focused on executing specific actions, lacking a comprehensive clarification of ambiguous instructions, and thus fail to fully meet the requirements of the task environment. Additionally, it does not inquire about the user's budget or related details.
"""


long_term_follow_up_examples = """
Environment:{"user_information": "The user is a student who majors in international relations. He stayed up late to finish his homework yesterday. He love drinking latte and buy it from a coffee shop near his house today. He use macbook to write his essay and make his PPT.",
"trigger_factor":"A conversation happend in 2 hours ago. Now is 12:00 a.m. Assistant: 'I am reading a paper on deep learning and find it interesting. What are you doing now?', User: 'Well... I am nervous about my presentation tomorrow.', Assistant: 'I understand you. Calm down and have a deep breathe. Do you need any help?', User: 'umm....ppt making? I don't know how to make it.' Assistant: 'It does not matter, maybe you can use an interesting case to introduce your content'."}
Reference: {"Target": "Inquire about the PPT making progress and provide presentation encouragement", "sub_target":["Ask the user about their PPT making progress", "Provide additional suggestions for PPT making", "Comfort the user about their PPT making anxiety", "Offer encouragement for tomorrow’s presentation"]}

generated target 1: {"Target": "Check in on user's presentation preparation", "sub_targets": ["Ask about progress on PPT", "Offer specific presentation tips", "Suggest taking breaks with latte"]}
score: 7gt
reason: generated target 1 includes checking the user's preparation status in both the target and reference, but it lacks an overall encouragement strategy. Additionally, the sub_targets do inquire about the user's situation with making a PPT and provide corresponding suggestions and encouragement, incorporating personalized information about the user's preference for lattes. However, emotionally, generated target 1 does not address the resolution of the user's anxiety related to PPT making.

Generated target 2: {"Target": "Assist with presentation preparation", "sub_targets": ["Ask about current PPT progress", "Offer specific design tips for PPT", "Suggest relevant case studies"]}
score: 8
reason: Compared to the reference, generated target 2 provides more content in terms of informational support, such as offering corresponding design solutions and specific case studies in the sub_targets. However, generated target 2 lacks in emotional support, which may not be user-friendly for a user who is staying up late to work on a PowerPoint presentation.

Generated target 3: {"Target":"Offer PPT making advice", "sub_targets":["Suggest using visuals", "Recommend simplifying slides", "Encourage practice presentation"]}
score: 5
reason: generated target 3 focuses on the user's PPT making in both the main target and sub_targets, which is contextually appropriate. However, the sub_targets of generated target 3 are too broad and lack specific content. This may hinder the user from receiving more detailed informational and emotional support, and it also fails to address the user's personal information.

Generated target 4: {"Target": "Offer PPT making assistance", "sub_targets": ["Ask about PPT content", "Suggest template options", "Provide case study ideas", "Offer to review PPT"]}
score: 6
reason: Compared to the reference target, the generated target provides more diverse assistance in terms of informational support, including template options and case studies, and proactively offers to help review the PPT. However, on one hand, this content is overly broad—for instance, the templates lack specific modifications or explanations. On the other hand, it falls short in providing emotional support.

Environment: "user_information": "The user is a student about to enter high school. This holiday, he traveled abroad with his parents. He usually has little interaction with the outside world and had no friends at his previous school.", "trigger_factor": "A conversation happend in last Saturday. Now is Friday 19:00 p.m. User: 'I will go to high school next week. It is my first time to attend high school. I am a bit nervous.' Assistant: 'Starting at a new school can indeed be nerve-wracking, but perhaps there are also things to look forward to. May I ask, what aspects are you mainly nervous about?' User: 'I’m not sure, but maybe it’s because there are too many challenging things—I need to adapt to a new social environment and different teaching styles. Plus, I’m not sure if I can keep up with high school knowledge.' Assistant: 'I totally get it, those things can be overwhelming, but maybe it’s also a great chance to grow and gain new experiences. Just take a deep breath and stay relaxed—I’m here with you all the way.'"
Reference: {"Target": "Check if the user has settled down at the new school", "sub_target": ["Ask the user how they are adjusting to the new school", "Ask the user if they need any help", "Listen to the user’s experiences at the new school", "Wish the user well at their new school"]}

generated target 1: {"Target": "Encourage and prepare user for high school", "sub_targets": ["Acknowledge user's feelings", "Suggest practical steps to adapt", "Highlight positive aspects of high school", "Offer ongoing support"]}
score: 5
reason: The conversation took place last Saturday, and the user mentioned going to school the following week, indicating that by now (Friday evening), the user has already been attending school for a week. The encouragement provided in generated target 1 about preparing for high school does not align well with the current context (as the user has already started high school) and lacks direct attention to the user's current state. Although the sub_target offers encouragement and reassurance to the user, in terms of the timeline, it would be more appropriate to inquire about the user's experience at the new school.

generated target 2: {"Target":"Boost user's confidence", "sub_targets":["Acknowledge user's feelings","Highlight positive aspects","Offer practical advice"]}
score: 3
reason: Compared to the reference, the generated target does not account for the factor of time progression. It appears more like a direct continuation of the previous conversation rather than a follow-up after a week. Additionally, the sub-goals are quite general and lack specificity. Moreover, it fails to inquire about the user's current situation, overlooking the possibility that the user may have new experiences or feelings at this point.

generated target 3: {"Target": "Help user build confidence for new school challenges", "sub_targets": ["Relate travel adaptability to school adjustment", "Suggest clubs to connect with peers","Advise on initiating study groups"]}
score: 4
reason: Generated target 2 is highly hypothetical, assuming that the user still needs to build confidence. Some sub-targets, such as linking travel experiences to school adaptation, feel somewhat unnatural in their relevance. Although the suggestions are specific (such as joining clubs or forming study groups), they do not first seek to understand the user’s current situation, resulting in a lack of user-friendliness. Additionally, there is a missing element of listening to and showing concern for the user’s actual experiences.

generated target 4: {"Target":"Ease User's Nerves", "sub_targets":["Offer Reassurance", "Share High School Tips"]}
score: 2
reason: Although the generated target acknowledges the need to alleviate users' nerves about going to school, it fails to reflect changes over time, and the sub-targets are overly simplistic.
"""



glasses_assistant_examples = """
Environment: "user_information": "The user is a product designer whose company currently holds a very positive attitude toward smart glasses. He is 32 years old and previously studied computer science and earned a master's degree in HCI. He has worked at companies like Microsoft, Google, and Meta. Last week, he purchased a pair of Rokid 3 smart glasses. He is also an AI enthusiast, frequently using AI tools to assist with his work, and has 3,232 followers on Twitter.", "trigger_factor": "The user is attending a meeting, listening to a presentation by his colleague Tom. At this moment, his colleague asks, 'What smart glasses products do you think are currently available on the market?'"
reference: {"Target": "Remind of Rokid experience and provide additional recommendations.", "sub_target": ["Prompt the user about their Rokid experience", "Provide key features of Rokid", "Offer recommendations for other smart glasses"]}

generated target 1: {"Target": "Assist user in answering about smart glasses.", "sub_target": ["Ask user if assistance is needed now.", "List notable smart glasses products briefly.", "Offer deeper insights on Rokid 3 if asked."]}
score: 7
reason: Compared to the reference, the sub_target of generated target 1 provides a hierarchical information support scheme, ranging from brief lists to in-depth analysis. This approach not only helps users navigate the current social context but also prepares them for potential deeper discussions. However, generated target 1 mentions less about the user's self-experience (rokid 3). Moreover, the fast pace of the meeting makes it seem somewhat dismissive to first ask users if they need assistance.

generated target 2: {"Target": "Help user respond knowledgeably about smart glasses market", "sub_targets": ["Suggest mentioning leading smart glasses brands", "Recommend highlighting Rokid 3 personal experience", "Propose mentioning emerging trends in smart glasses"]}
score: 10
reason: generated target 2 first presents multiple current brands compared to the reference, then analyzes the user experience of Rokid, effectively integrating professional knowledge with personalized content. It also mentions future development trends, making it more comprehensive and professional.

generated target 3: "Target": "Provide Rokid 3 features to answer colleague's query", "sub_targets": ["Acknowledge colleague's question contextually", "Highlight Rokid 3 as a leading product", "Detail AI integration and design benefits", "Offer to summarize key points for meeting"]
score: 10
reason: Both the generated target 3 and the reference mention Rokid 3 in response to the colleague's question. Additionally, the sub_target directly addresses the colleague's query with a professional response, suggesting some actionable items for meetings (e.g., summarizing key points) and leveraging the user's background knowledge as a product designer and AI enthusiast.

generated target 4: {"Target":"Recommend smart glasses","sub_targets":["Mention Rokid 3","Highlight features"]}
score:  3
reason: The generated target 4 is overly simplistic and general, and the sub_target is also not comprehensive enough. Although it mentions Rokid 3 and highlights some key features, it lacks personalized elements (not taking into account the user’s own experience with Rokid) as well as a broader market perspective.

generated target 5: {"Target": "Share smart glasses knowledge", "sub_targets": ["Mention Rokid 3 features", "Compare with other smart glasses", "Highlight market trends"]}
score: 6
reason: Compared to the reference, generated target 5 also mentions Rokid in the sub_targets. However, the sub_targets are overly broad and fail to emphasize the user's actual experience. While highlighting market trends at the end is a good plan, it is also quite general and lacks specific guidance.

Environment: "user_information": "The user suffers from obesity and has decided to develop a fitness habit this year. Recently, he has been doing cardio and strength training every evening after work. He is also improving his diet to become healthier. Lately, he has been under significant work pressure due to a mid-term career evaluation.",
"trigger_factor": "The user worked out at the gym for 1 hour today, completing all of his exercise goals for the day."
Reference:{"target": "Congratulate the user’s workout achievement today.", "sub_target": ["Celebrate the user’s workout today", "Summarize the user’s exercise accomplishments for the day", "Encourage the user in both work and fitness"]

generated target 1: {"Target":"Celebrate user's workout achievement","sub_targets":["Acknowledge effort","Suggest short break","Offer motivational quote"]}
score: 4
reason: The generated target does not address the user's current work-related stress, and compared to the reference, it is overly brief and general. The suggestion to "Offer motivational quote" may come across as somewhat vague, lacking the direct impact of a specific summary of achievements. Additionally, the recommendation to "Suggest short break" might feel redundant or mistimed, given that the user has just completed an hour of exercise and achieved all their goals. While the intention is positive, it doesn't flow as naturally as the sub-goals in the reference.

generated target 2: {"Target": "Acknowledge workout and suggest recovery", "sub_targets": ["Praise workout completion.", "Suggest healthy post-workout meal.", "Offer stress-relief tips."]}
score: 10
reason: Generated Target 2 comprehensively considers the entire experience chain after exercise (praise → recovery → stress relief). The sub-goals exhibit strong logical coherence, transitioning naturally from the present moment to the next step (healthy meal), and then addressing background issues (work-related stress). Compared to the reference, it provides specific and actionable suggestions rather than mere encouragement. Finally, it takes into account multiple key aspects of the user’s background information (obesity issues, dietary improvement needs, work-related stress), making the sub-targets more personalized.

generated target 3: {"Target": "Encourage continued fitness progress and stress management","sub_targets": ["Acknowledge today's successful workout completion", "Suggest a post-workout stretching routine for stress relief", "Connect diet improvements to workout recovery benefits", "Offer to adjust future workouts based on work schedule"]
}
score: 10
reason: Generated Target 3 not only responds to the day's exercise achievement (Sub-goal 1) but also directly ties into the user's long-term goals of "managing work stress" and "building a fitness habit." Sub-goal 2 (stretching to relieve stress), Sub-goal 3 (nutrition and recovery), and Sub-goal 4 (adjusting workouts according to work demands) all reflect a deep understanding of and support for the user's overall condition, encompassing fitness, diet, and work-related stress.
"""

recommendation_examples="""
"Environment": {"user_information": "The user is a young male living in Harbin. He enjoys watching movies, listening to music, and following entertainment news. His favorite movies are 'The Little Prince' and 'Moment in West Lake', and he dislikes the films 'Hong Kong Hollywood' and 'Xue Ma Xue Ma: Sing Me a Song While You Wait for Me'. The music he likes includes 'Limitless' and 'Not Too Much', but he really dislikes the song 'For the Children'. His favorite celebrities are Zhou Xun and Leslie Cheung.", "trigger_factor": "The assistant is a close friend of the user who enjoys Hong Kong, Macau, and Taiwanese TV dramas. Recently, the assistant watched a Taiwanese drama called 'Mr. Right Wanted'. The drama has a good reputation; it is a comedy and many people found it very entertaining."}
Reference: {"Target": "Recommend 'Mr. Right Wanted'", "sub_target": ["Connect the user's liking of Leslie Cheung to Hong Kong, Macau, and Taiwanese productions", "Introduce 'Looking for Mr. Right'", "Emphasize good reviews and user feedback", "Express anticipation to discuss the drama together with the user"]}
generated target 1: {"Target": "Recommend 'Mr. Right Wanted' to user", "sub_target": ["Mention enjoying Taiwanese drama recently", "Describe 'Mr. Right Wanted' as entertaining comedy", "Ask if user wants to watch together"]}
score: 10
reason: Compared to the reference target, generated target 1 accurately captures the title of the drama mentioned in the triggering event. The recommended content is concise and to the point, directly addressing the key aspects. Additionally, the logic of the sub-targets is clear. In the reference, the connection between the user's fondness for Leslie Cheung and the recommended content feels somewhat forced. However, the sub-target here transitions more naturally.

generated target 2: {"Target":"Recommend 'Mr. Right Wanted' to the user","sub_target":["Express interest in his entertainment preferences","Mention the Taiwanese drama 'Mr. Right Wanted'","Highlight its comedy genre and positive reception","Encourage him to watch it"]}
score: 10
reason: The content expressed in generated target 2 and the reference on the target is consistent. However, in the planning of sub_target, generated target 2 first expresses interest in user preferences, which makes the connection with the reference more natural. This approach can better engage users and encourage their interaction and participation.

genearated target 3: {"Target": "Recommend 'Mr. Right Wanted' to the user", "sub_targets": ["Introduce the drama's genre and reputation", "Highlight the comedy aspect and entertainment value", "Ask for the user's interest in Taiwanese dramas"]}
score: 6
reason: The generated target 3 aligns with the reference on the target. However, in the planning of the sub_target, the recommendations are not connected to the user's own preferences and interests. Additionally, the system only asks the user about their interest in Taiwanese dramas at the end, which appears to be primarily based on the assistant's own preferences. The interaction lacks social engagement elements, and the final sub-goal is relatively simplistic, lacking strategic depth.

generated target 4: {"Target": "Recommend 'Mr. Right Wanted' Taiwanese drama to user", "sub_target": ["Share my enthusiasm about the Taiwanese drama", "Connect drama to user's entertainment interests", "Ask if user would like to watch it together"]}
score: 10
reason: The content of the generated target 4 remains consistent with the reference. Moreover, the sub-goals of generating target 4 include "sharing my passion for Taiwanese dramas" and "asking the user if they would like to watch together," which can create a better interactive experience rather than just a one-way recommendation.

Environment: "user_information":"The user is a teenager living in Qingdao who really likes the Wanzhou Grilled Fish restaurant. He is generally regarded by his classmates as a trustworthy and straightforward friend, and he approaches his studies in an organized and cautious manner. He is relatively quiet and introverted in life and tends to feel unsafe and nervous in unfamiliar environments. His teacher has previously encouraged him to be more imaginative and creative when learning new knowledge.", "trigger_factor":"Assistant is a friend who often goes out to eat with the user. Recently, he discovered that the Mingguo Seafood Dumpling Restaurant is very delicious. Last weekend, he tried the restaurant's specialty dishes, celery dumplings and mackerel dumplings, spending 78 yuan. After eating, he rated the restaurant 5 stars on the Dazhong Dianping app."
Reference: {"Target": "Introduce Mingguo Seafood Dumpling Restaurant to the user", "sub_target": ["Ask the user about their preferences regarding dumplings", "Connect the user's love for fish with seafood", "Recommend their specialty dishes", "Emphasize the restaurant's good value for money"]}
generated target 1: {"Target": "Recommend Mingguo Seafood Dumpling Restaurant", "sub_targets": ["Share my recent restaurant discovery", "Describe the delicious specialty dumplings", "Suggest going together sometime"]}
score: 6
reason: Both generated target 1 and the reference recommend Mingguo Seafood Dumpling Restaurant to the user regarding the target. However, the reference first inquires about the user's preferences, then associates their likes with seafood, and finally makes the recommendation while emphasizing the restaurant's unique features. This process feels more natural. On the other hand, generated target 1 focuses more on making recommendations from a self-centered perspective, without considering the user's point of view or asking for their preferences. Additionally, it lacks an introduction to the restaurant's pricing characteristics.

generated target 2: {"Target":"Recommend new restaurant to user","sub_targets":["Share positive experience about Mingguo","Ask user's opinion on trying new places"]}
score: 4
reason: The generated response involves recommending restaurants and sharing personal experiences with the user, as well as asking questions. However, it is too general and lacks detail and specificity. It does not take into account the user's personality traits, nor does it provide specific information about menu items or price references. Additionally, it fails to connect with the user’s existing preferences. The recommendation strategy is incomplete, and the approach of sharing first and then asking questions makes it difficult for users to engage in meaningful interaction.

generated target 3: {"Target": "Recommend a book to user","sub_targets":"Introduce a popular book to the user", "Hightlight the reputation of the book", "Share self experience of reading the book."}
score: 1
reason: It is completely irrelevant to the current environment description, does not align with the core content of the triggering event, and is also unrelated to the user's interests.

generated target 4: {"Target": "Recommend Mingguo Seafood Dumpling Restaurant", "sub_targets": ["Connect Mingguo to his favorite Wanzhou Grilled Fish", "Mention specialty dishes and 5-star rating details", "Address his hesitation about unfamiliar environments"]}
score: 10
reason: Reason: Compared to the "introduce" in the reference, "recommend" aligns more closely with the requirements of the current task in terms of action. Moreover, the sub-targets are highly targeted, effectively building on the user's existing preferences to establish a foundation of trust. Specific recommendation evidence (such as signature dishes and five-star reviews) is provided, while also paying special attention to the user's sense of insecurity in an unfamiliar environment, proactively addressing this barrier. Overall, the generated target 4 is more contextually appropriate and personalized than the reference, and the steps are more comprehensive.
"""