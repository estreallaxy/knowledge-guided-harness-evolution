# -*- coding: utf-8 -*-
FEW_SHOT_GEN = [
    # Example 1
    {'role': 'user', 'content': (
        "Scenario: Alice is training for a marathon.\n"
        "Statement: Running on a treadmill improves her endurance.\n"
        "Opposite Statement: Running on a treadmill does not improve her endurance.\n"
        "Generate 2 sentences.")},
    {'role': 'assistant', 'content': (
        "1. Treadmill training allows Alice to maintain a consistent pace and monitor heart rate, boosting her aerobic capacity.\n"
        "2. The treadmill's adjustable incline simulates hill workouts, increasing leg strength and stamina.")},
    # Example 2
    {'role': 'user', 'content': (
        "Scenario: Bob studies every evening.\n"
        "Statement: Studying in short, focused bursts enhances retention.\n"
        "Opposite Statement: Studying in short, focused bursts does not enhance retention.\n"
        "Generate 2 sentences.")},
    {'role': 'assistant', 'content': (
        "1. Brief study sessions with breaks prevent mental fatigue and improve long-term recall.\n"
        "2. Frequent reviews in small intervals reinforce memory pathways, aiding retention.")}
]


# Few-shot examples for factor extraction
FEW_SHOT_EXT = [
    {'role': 'user', 'content': (
        "Extract distinct factors from these sentences as a JSON array.\n"
        "1. Treadmill training allows maintaining a consistent pace and monitoring heart rate, boosting aerobic capacity.\n"
        "2. The treadmill's adjustable incline simulates hill workouts, increasing leg strength and stamina.")},
    {'role': 'assistant', 'content': (
        "Let me analyze these sentences to identify the key factors:\n\n"
        "From sentence 1: The treadmill allows consistent pace (pace consistency) and heart rate monitoring, which boosts aerobic capacity.\n"
        "From sentence 2: The adjustable incline feature simulates hills, which increases leg strength.\n\n"
        "Key factors identified:\n"
        "- Pace consistency (ability to maintain steady speed)\n"
        "- Heart rate monitoring (tracking cardiovascular response)\n"
        "- Adjustable incline (variable difficulty/terrain simulation)\n"
        "- Leg strength (muscle development)\n\n"
        "Final answer:\n"
        '["Pace consistency","Heart rate monitoring","Adjustable incline","Leg strength"]')},
    
    {'role': 'user', 'content': (
        "Extract distinct factors from these sentences as a JSON array.\n"
        "1. Group work requires coordination between team members.\n"
        "2. Individual tasks allow for personal control and efficiency.")},
    {'role': 'assistant', 'content': (
        "Let me identify the key factors from these sentences:\n\n"
        "From sentence 1: Group work needs coordination between team members.\n"
        "From sentence 2: Individual tasks provide personal control and efficiency.\n\n"
        "Key factors:\n"
        "- Coordination requirements (need for team synchronization)\n"
        "- Personal control (individual autonomy)\n"
        "- Efficiency (productivity/effectiveness)\n"
        "- Team collaboration (working together)\n\n"
        "Final answer:\n"
        '["Coordination requirements","Personal control","Efficiency","Team collaboration"]')}
]

FEW_SHOT_VOTE = [
    {
        'role': 'user',
        'content': (
            "Scenario: Alice trains for a marathon.\n"
            "Statement1: Treadmill running improves endurance.\n"
            "Statement2: Treadmill running does not improve endurance.\n"
            "Factor: Pace consistency\n"
            "Decide which statement this factor supports: Statement1, Statement2, or Both. "
            "Think step by step, then answer in JSON."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Pace consistency forces a steady speed, building aerobic capacity and sustained effort.\n"
            "Final answer:\n"
            '{"Pace consistency": "Statement1"}'
        )
    },
    {
        'role': 'user',
        'content': (
            "Scenario: Alice trains for a marathon.\n"
            "Statement1: Treadmill running improves endurance.\n"
            "Statement2: Treadmill running does not improve endurance.\n"
            "Factor: Weather conditions\n"
            "Decide which statement this factor supports: Statement1, Statement2, or Both. "
            "Think step by step, then answer in JSON."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Treadmill gives consistent conditions, yet outdoor weather readies race adaptability.\n"
            "Final answer:\n"
            '{"Weather conditions": "Both"}'
        )
    }
]



# Few-shot for clustering
FEW_SHOT_CLUSTER = [
    {'role': 'user', 'content': (
        "Cluster these factors into thematic groups. Think about how they relate to each other, "
        "then provide a JSON object mapping cluster names to factor lists. Use English cluster names.")},
    {'role': 'assistant', 'content': (
        "Let me analyze these factors and group them by theme:\n\n"
        "Looking at the factors:\n"
        "- Pace consistency: Related to training control and mechanics\n"
        "- Heart rate monitoring: Also related to training control and measurement\n"
        "- Adjustable incline: Related to physical challenge and strength\n"
        "- Leg strength: Related to physical development and strength\n\n"
        "I can see two main themes:\n"
        "1. Training Mechanics: Factors related to training control, measurement, and consistency\n"
        "2. Strength Factors: Factors related to physical development and muscle building\n\n"
        "Final answer:\n"
        '{"Training Mechanics":["Pace consistency","Heart rate monitoring"],"Strength Factors":["Adjustable incline","Leg strength"]}')}
]

# Few-shot for pruning redundant factors
FEW_SHOT_PRUNE = [
    {'role': 'user', 'content': (
        "From these factors in cluster 'Training Methods', remove redundant ones. "
        "Think about which factors are essentially the same concept, then return a JSON array of the remaining unique factors.\n"
        '["Consistent pace", "Steady rhythm", "Heart rate monitoring", "Pulse tracking"]')},
    {'role': 'assistant', 'content': (
        "Let me analyze these factors for redundancy:\n\n"
        "Looking at the factors:\n"
        "- 'Consistent pace' and 'Steady rhythm': These are essentially the same concept - maintaining a regular speed/tempo\n"
        "- 'Heart rate monitoring' and 'Pulse tracking': These are also the same concept - measuring heart rate\n\n"
        "Redundant pairs identified:\n"
        "- 'Consistent pace' vs 'Steady rhythm' → Keep 'Consistent pace' (more specific to running)\n"
        "- 'Heart rate monitoring' vs 'Pulse tracking' → Keep 'Heart rate monitoring' (more comprehensive term)\n\n"
        "Final answer:\n"
        '["Consistent pace","Heart rate monitoring"]')}
]

# JSON correction prompt for retry attempts
JSON_CORRECTION_PROMPT = {
    'role': 'system', 
    'content': (
        "Your previous response was not valid JSON. You can think about your reasoning, "
        "but please end with 'Final answer:' followed by a valid JSON object "
        "with the exact factor name as the key and your choice (Statement1, Statement2, or Both) as the value. "
        "Example format:\n"
        "Final answer:\n"
        "{\"factor name\": \"Statement1\"}"
    )
}


CLUSTER_NAME_PROMPT = [
    {
        'role': 'user',
        'content': (
            "Generate a theme name for these related factors:\n"
            '["energy expenditure", "energy efficiency", "energy transfer efficiency"]'
        )
    },
    {
        'role': 'assistant',
        'content': "Energy Efficiency"
    },
    {
        'role': 'user',
        'content': (
            "Generate a theme name for these related factors:\n"
            '["precision control", "better control (accuracy)", "control and precision"]'
        )
    },
    {
        'role': 'assistant',
        'content': "Control Precision"
    },
]


'''''''MAPPING FEW SHOT PROMPTS'''''''


MAPPING_VOTE_SHOT = [
    {
        "role": "user",
        "content": (
            "Scenario: A student is preparing for final exams.\n"
            "Condition: The student spends more time in the library.\n"
            "Candidate factors: [\"Better time management\", \"More stress\", \"Increased social activities\"]\n\n"
            "Task: Select the factor list that is most reasonably related to the given condition. "
            "Think step by step about each factor's relevance, then provide your selection. "
            "Please respond with your reasoning followed by 'Final answer:' and a JSON object in this exact format: {\"answer\": [\"factor1\", \"factor2\", ...]}"
        )
    },
    {
        "role": "assistant",
        "content": (
            "Let me analyze each factor:\n\n"
            "- \"Better time management\": Spending more time in the library suggests the student is organizing their study schedule better and dedicating focused time to studying. This is directly related.\n"
            "- \"More stress\": While exam preparation can be stressful, spending more time in the library is typically a positive study behavior, not necessarily indicating increased stress.\n"
            "- \"Increased social activities\": Libraries are generally quiet study spaces, not social venues. More library time would likely mean less social activities.\n\n"
            "Final answer:\n"
            "{\"answer\": [\"Better time management\"]}"
        )
    },
    {
        "role": "user",
        "content": (
            "Scenario: A company introduces remote working policies.\n"
            "Condition: Employees can work from home twice a week.\n"
            "Candidate factors: [\"Improved work-life balance\", \"Reduced office costs\", \"More commuting\"]\n\n"
            "Task: Select the factor list that is most reasonably related to the given condition. "
            "Think step by step about each factor's relevance, then provide your selection. "
            "Please respond with your reasoning followed by 'Final answer:' and a JSON object in this exact format: {\"answer\": [\"factor1\", \"factor2\", ...]}"
        )
    },
    {
        "role": "assistant",
        "content": (
            "Let me evaluate each factor:\n\n"
            "- \"Improved work-life balance\": Working from home twice a week allows employees to save commute time, have more flexibility, and better integrate work with personal life. This is directly related.\n"
            "- \"Reduced office costs\": With employees working from home part-time, the company needs less office space, utilities, and resources. This is a logical consequence.\n"
            "- \"More commuting\": This is contradictory - working from home twice a week would actually reduce commuting, not increase it.\n\n"
            "Final answer:\n"
            "{\"answer\": [\"Improved work-life balance\", \"Reduced office costs\"]}"
        )
    }
]


MAPPING_REFLECTION_SHOT = [
    {
        "role": "user",
        "content": (
            "Condition: City implements a bike-sharing program.\n"
            "Initially selected factors: [\"Increased bike usage\", \"Higher car sales\", \"More traffic jams\"]\n\n"
            "Task: Review and keep factors reasonably related to the condition. "
            "Think step by step about each factor's relevance, then 'Final answer:' with a JSON array."
        )
    },
    {
        "role": "assistant",
        "content": (
            "“Increased bike usage” is the direct result of more shared bikes—keep it.\n"
            "“Higher car sales” has no clear link to bike sharing—remove it.\n"
            "“More traffic jams” could occur if road space shifts to bikes and cars interact—keep it.\n\n"
            "Final answer:\n"
            "[\"Increased bike usage\", \"More traffic jams\"]"
        )
    },
    {
        "role": "user",
        "content": (
            "Condition: Students study in a quiet library.\n"
            "Initially selected factors: [\"Better concentration\", \"Distractions from phones\", "
            "\"Improved retention\", \"Reduced social interaction\"]\n\n"
            "Task: Review and keep factors reasonably related to the condition. "
            "Think step by step about each factor's relevance, then 'Final answer:' with a JSON array."
        )
    },
    {
        "role": "assistant",
        "content": (
            "“Better concentration” follows from a quiet space aiding focus—keep it.\n"
            "“Distractions from phones” contradicts the library’s purpose—remove it.\n"
            "“Improved retention” naturally arises from focused study—keep it.\n"
            "“Reduced social interaction” is a likely side-effect of silence—keep it.\n\n"
            "Final answer:\n"
            "[\"Better concentration\", \"Improved retention\", \"Reduced social interaction\"]"
        )
    }
]


generate_para_prob_shots = [
{
  "role": "system",
  "content": "You are an AI assistant whose task is: given a user-provided scenario comparing two statements and a list of factor values, estimate for each factor the probability (a float between 0 and 1) that it supports Statement 1 rather than Statement 2. Return your answer strictly as a JSON object mapping each factor value to its probability. Use 0.5 to indicate a neutral case (factor equally supports both statements), values greater than 0.5 to indicate stronger support for Statement 1, and values less than 0.5 to indicate stronger support for Statement 2."
},
        {
            "role": "user",
            "content": "Given the scenario:\n\"\"\"Comparing the ease of carrying a heavy box upstairs by one person vs. two people.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. carrying by one person is easier)\nrather than Statement 2 (i.e. carrying by two people is easier).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"One person\", \"Two people\", \"Box weight is under 10 kg\", \"Box weight exceeds 30 kg\", \"Staircase is narrow\", \"Staircase is wide\", \"Good coordination required\", \"No coordination needed\"]"
        },
        {
            "role": "assistant",
            "content": "{\n  \"One person\": 0.30,\n  \"Two people\": 0.70,\n  \"Box weight is under 10 kg\": 0.85,\n  \"Box weight exceeds 30 kg\": 0.15,\n  \"Staircase is narrow\": 0.20,\n  \"Staircase is wide\": 0.60,\n  \"Good coordination required\": 0.40,\n  \"No coordination needed\": 0.75\n}"
        },
        {
            "role": "user",
            "content": "Given the scenario:\n\"\"\"Comparing the speed of downloading a 1GB file over Wi-Fi vs. 4G cellular network.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. downloading over Wi-Fi is faster)\nrather than Statement 2 (i.e. downloading over 4G is faster).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"Wi-Fi connection\", \"4G connection\", \"Average Wi-Fi bandwidth ≥ 100 Mbps\", \"Average 4G bandwidth ≤ 20 Mbps\", \"Signal is stable\", \"Signal fluctuates frequently\", \"No data cap\", \"Strict monthly data cap\"]"
        },
        {
            "role": "assistant",
            "content": "{\n  \"Wi-Fi connection\": 0.88,\n  \"4G connection\": 0.12,\n  \"Average Wi-Fi bandwidth ≥ 100 Mbps\": 0.92,\n  \"Average 4G bandwidth ≤ 20 Mbps\": 0.25,\n  \"Signal is stable\": 0.80,\n  \"Signal fluctuates frequently\": 0.30,\n  \"No data cap\": 0.70,\n  \"Strict monthly data cap\": 0.15\n}"
        },
    {
        "role": "user",
        "content": "Given the scenario:\n\"\"\"Comparing reading on a digital screen vs printed paper.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. reading on screen is better)\nrather than Statement 2 (i.e. reading on paper is better).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"High contrast display\", \"High contrast print\", \"Screen glare present\", \"Glare absent\", \"Font size identical\", \"Lighting conditions identical\"]"
    },
    {
        "role": "assistant",
        "content": "{\n"
                   "  \"High contrast display\": 0.60,\n"
                   "  \"High contrast print\": 0.40,\n"
                   "  \"Screen glare present\": 0.30,\n"
                   "  \"Glare absent\": 0.70,\n"
                   "  \"Font size identical\": 0.50,\n"
                   "  \"Lighting conditions identical\": 0.50\n"
                   "}"
    },
    {
        "role": "user",
        "content": "Given the scenario:\n\"\"\"Comparing fuel efficiency of diesel cars vs gasoline cars.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. diesel cars are more fuel-efficient)\nrather than Statement 2 (i.e. gasoline cars are more fuel-efficient).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"Diesel vehicles typically generate more torque\", \"Gasoline vehicles typically generate more torque\", \"Vehicle weight and aerodynamics identical\", \"Fuel price difference negligible\"]"
    },
    {
        "role": "assistant",
        "content": "{\n"
                   "  \"Diesel vehicles typically generate more torque\": 0.65,\n"
                   "  \"Gasoline vehicles typically generate more torque\": 0.35,\n"
                   "  \"Vehicle weight and aerodynamics identical\": 0.50,\n"
                   "  \"Fuel price difference negligible\": 0.50\n"
                   "}"
    }
    ]

generate_para_prob_shots_cot_v0 = [
    {
        "role": "system",
        "content": "Please perform a brief chain-of-thought (step-by-step) before outputting the final JSON:\n\nYou are an AI assistant whose task is: given a user-provided scenario comparing two statements and a list of factor values, estimate for each factor the probability (a float between 0 and 1) that it supports Statement 1 rather than Statement 2. Return your answer strictly as a JSON object mapping each factor value to its probability. Use 0.5 to indicate neutrality, values greater than 0.5 to indicate stronger support for Statement 1, and values less than 0.5 to indicate stronger support for Statement 2."
    },
    {
        "role": "user",
        "content": "Given the scenario:\n\"\"\"Comparing the ease of carrying a heavy box upstairs by one person vs. two people.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. carrying by one person is easier)\nrather than Statement 2 (i.e. carrying by two people is easier).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"One person\", \"Two people\", \"Box weight is under 10 kg\", \"Box weight exceeds 30 kg\", \"Staircase is narrow\", \"Staircase is wide\", \"Good coordination required\", \"No coordination needed\"]"
    },
    {
        "role": "assistant",
        "content": "Thought: A single person has limited strength, so two people generally handle heavy loads better, especially in wide spaces; narrow stairs limit teamwork.\n{\n  \"One person\": 0.30,\n  \"Two people\": 0.70,\n  \"Box weight is under 10 kg\": 0.85,\n  \"Box weight exceeds 30 kg\": 0.15,\n  \"Staircase is narrow\": 0.20,\n  \"Staircase is wide\": 0.60,\n  \"Good coordination required\": 0.40,\n  \"No coordination needed\": 0.75\n}"
    },
    {
        "role": "user",
        "content": "Given the scenario:\n\"\"\"Comparing the speed of downloading a 1GB file over Wi-Fi vs. 4G cellular network.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. downloading over Wi-Fi is faster)\nrather than Statement 2 (i.e. downloading over 4G is faster).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"Wi-Fi connection\", \"4G connection\", \"Average Wi-Fi bandwidth ≥ 100 Mbps\", \"Average 4G bandwidth ≤ 20 Mbps\", \"Signal is stable\", \"Signal fluctuates frequently\", \"No data cap\", \"Strict monthly data cap\"]"
    },
    {
        "role": "assistant",
        "content": "Thought: Wi-Fi typically offers higher and more stable throughput, and no data cap avoids throttling or interruptions.\n{\n  \"Wi-Fi connection\": 0.88,\n  \"4G connection\": 0.12,\n  \"Average Wi-Fi bandwidth ≥ 100 Mbps\": 0.92,\n  \"Average 4G bandwidth ≤ 20 Mbps\": 0.25,\n  \"Signal is stable\": 0.80,\n  \"Signal fluctuates frequently\": 0.30,\n  \"No data cap\": 0.70,\n  \"Strict monthly data cap\": 0.15\n}"
    },
    {
        "role": "user",
        "content": "Given the scenario:\n\"\"\"Comparing reading on a digital screen vs printed paper.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. reading on screen is better)\nrather than Statement 2 (i.e. reading on paper is better).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"High contrast display\", \"High contrast print\", \"Screen glare present\", \"Glare absent\", \"Font size identical\", \"Lighting conditions identical\"]"
    },
    {
        "role": "assistant",
        "content": "Thought: High-contrast screens can aid legibility, but glare disadvantages screens while paper remains glare-free.\n{\n  \"High contrast display\": 0.60,\n  \"High contrast print\": 0.40,\n  \"Screen glare present\": 0.30,\n  \"Glare absent\": 0.70,\n  \"Font size identical\": 0.50,\n  \"Lighting conditions identical\": 0.50\n}"
    },
    {
        "role": "user",
        "content": "Given the scenario:\n\"\"\"Comparing fuel efficiency of diesel cars vs gasoline cars.\"\"\"\nFor each of the following factor values, please estimate the probability (a float between 0 and 1)\nthat this factor value supports Statement 1 (i.e. diesel cars are more fuel-efficient)\nrather than Statement 2 (i.e. gasoline cars are more fuel-efficient).\nReturn a JSON mapping from factor value to probability.\n\nFactor values:\n[\"Diesel vehicles typically generate more torque\", \"Gasoline vehicles typically generate more torque\", \"Vehicle weight and aerodynamics identical\", \"Fuel price difference negligible\"]"
    },
    {
        "role": "assistant",
        "content": "Thought: Diesels generally have higher thermal efficiency and torque, but with identical weight/aero and fuel cost, the efficiency edge narrows.\n{\n  \"Diesel vehicles typically generate more torque\": 0.65,\n  \"Gasoline vehicles typically generate more torque\": 0.35,\n  \"Vehicle weight and aerodynamics identical\": 0.50,\n  \"Fuel price difference negligible\": 0.50\n}"
    }
]

generate_para_prob_shots_cot_v1 = [
    {
        "role": "user",
        "content": """Given the scenario:
"Comparing working from home vs working in the office."
For each of the following factor values, please estimate the probability (a float between 0 and 1)
that this factor value supports Statement 1 (i.e. working from home is more advantageous)
rather than Statement 2 (i.e. working in the office is more advantageous).
Return a JSON mapping from factor value to probability.

Factor values:
["Commute time eliminated", "Structured schedule", "Flexible hours", "Office social interactions", "Household distractions", "Professional equipment at office", "Self-discipline required", "Access to office networking", "Ergonomic workstation", "Stability of home internet"]"""
    },
    {
        "role": "assistant",
        "content": """Thought: Eliminating the commute and having flexible hours strongly favor working from home; conversely, a structured schedule, professional equipment, social interactions, and networking opportunities favor the office. Household distractions and internet stability can tip either way depending on the home environment.
{
  "Commute time eliminated": 0.90,
  "Structured schedule": 0.30,
  "Flexible hours": 0.85,
  "Office social interactions": 0.25,
  "Household distractions": 0.40,
  "Professional equipment at office": 0.35,
  "Self-discipline required": 0.45,
  "Access to office networking": 0.20,
  "Ergonomic workstation": 0.40,
  "Stability of home internet": 0.75
}"""
    },
    {
        "role": "user",
        "content": """Given the scenario:
"Comparing LED bulbs vs incandescent bulbs in home lighting."
For each of the following factor values, please estimate the probability (a float between 0 and 1)
that this factor value supports Statement 1 (i.e. LED bulbs are more advantageous)
rather than Statement 2 (i.e. incandescent bulbs are more advantageous).
Return a JSON mapping from factor value to probability.

Factor values:
["Initial cost per bulb", "Energy consumption per hour", "Lifespan hours", "Color rendering index", "Warm color temperature", "Instant full brightness", "Dimmable compatibility", "Mercury content", "Heat generation", "Availability"]"""
    },
    {
        "role": "assistant",
        "content": """Thought: LEDs excel in low energy use, longevity, low heat output, and no mercury, but cost more upfront, may have lower CRI, different warmth, and varying dimming support and availability.
{
  "Initial cost per bulb": 0.30,
  "Energy consumption per hour": 0.95,
  "Lifespan hours": 0.90,
  "Color rendering index": 0.25,
  "Warm color temperature": 0.40,
  "Instant full brightness": 0.50,
  "Dimmable compatibility": 0.35,
  "Mercury content": 0.85,
  "Heat generation": 0.88,
  "Availability": 0.45
}"""
    },
    {
        "role": "user",
        "content": """Given the scenario:
"Comparing convenience of streaming movies online vs renting Blu-ray discs."
For each of the following factor values, please estimate the probability (a float between 0 and 1)
that this factor value supports Statement 1 (i.e. streaming is more convenient)
rather than Statement 2 (i.e. renting Blu-ray is more convenient).
Return a JSON mapping from factor value to probability.

Factor values:
["Internet bandwidth", "Video quality potential (Blu-ray)", "Library availability online", "Physical disc ownership", "Load time vs buffering", "No subscription fee", "Need for disc drive", "Portability of files", "Multiple device streaming", "Resale value of disc"]"""
    },
    {
        "role": "assistant",
        "content": """Thought: Streaming offers instant access, broad libraries, multi-device support, and no hardware requirements, whereas Blu-ray provides top video quality, ownership, no buffering, pay-per-rental simplicity, and resale value.
{
  "Internet bandwidth": 0.80,
  "Video quality potential (Blu-ray)": 0.30,
  "Library availability online": 0.85,
  "Physical disc ownership": 0.25,
  "Load time vs buffering": 0.35,
  "No subscription fee": 0.40,
  "Need for disc drive": 0.75,
  "Portability of files": 0.65,
  "Multiple device streaming": 0.90,
  "Resale value of disc": 0.30
}"""
    }
]


LLM_LATENT_SHOTS = [
    # System instruction
    {
        "role": "system",
        "content": (
            "You are an AI assistant tasked with identifying latent variables and assigning "
            "each latent only factors drawn from the provided list. Do NOT output any edges. "
            "Return a JSON object with a single field:\n"
            "  latents: an array of objects, each with:\n"
            "    - name: string\n"
            "    - factors: array of strings (each chosen from the provided Factors list)\n"
            "Ensure the JSON parses correctly and strictly follows this schema."
        )
    },
    # Example 1 user dialogue
    {
        "role": "user",
        "content": (
            "Please identify latent variables and assign each factor to a latent. "
            "Then return JSON with fields:\n"
            "  latents: [{\"name\": string, \"factors\": [...]}, ...],\n"
            "Factors: [\"Nutrition\", \"Vitamins\", \"Taste\", \"Convenience\"]"
        )
    },
    # Example 1 assistant output
    {
        "role": "assistant",
        "content": (
            "{\"latents\":["
            "{\"name\":\"HealthLat\",\"factors\":[\"Nutrition\",\"Vitamins\"]},"
            "{\"name\":\"EnjoyLat\",\"factors\":[\"Taste\",\"Convenience\"]}"
            "]}"
        )
    },
    # Example 2 user dialogue
    {
        "role": "user",
        "content": (
            "Please identify latent variables and assign each factor to a latent. "
            "Then return JSON with fields:\n"
            "  latents: [{\"name\": string, \"factors\": [...]}, ...],\n"
            "Factors: [\"Reward\", \"Risk\", \"TimePressure\", \"Collaboration\"]"
        )
    },
    # Example 2 assistant output
    {
        "role": "assistant",
        "content": (
            "{\"latents\":["
            "{\"name\":\"BenefitLat\",\"factors\":[\"Reward\"]},"
            "{\"name\":\"CostLat\",\"factors\":[\"Risk\",\"TimePressure\"]},"
            "{\"name\":\"SocialLat\",\"factors\":[\"Collaboration\"]}"
            "]}"
        )
    }
]

LLM_LATENT_SHOTS_COT = [
    # System instruction, requiring brief reasoning first, then final JSON output
    {
        "role": "system",
        "content": (
            "Please perform a brief chain-of-thought (step-by-step reasoning) before outputting the final JSON.\n\n"
            "You are an AI assistant tasked with identifying latent variables and assigning each latent only factors drawn from the provided list. "
            "Do NOT output any edges. Return a JSON object with a single field:\n"
            "  latents: an array of objects, each with:\n"
            "    - name: string\n"
            "    - factors: array of strings (each chosen from the provided Factors list)\n"
            "Ensure the JSON parses correctly and strictly follows this schema."
        )
    },
    # Example 1 user dialogue
    {
        "role": "user",
        "content": (
            "Please identify latent variables and assign each factor to a latent. "
            "Then return JSON with fields:\n"
            "  latents: [{\"name\": string, \"factors\": [...]}, ...],\n"
            "Factors: [\"Nutrition\", \"Vitamins\", \"Taste\", \"Convenience\"]"
        )
    },
    # Example 1 assistant output (with CoT)
    {
        "role": "assistant",
        "content": (
            "Thought: Nutrition and Vitamins both relate to health aspects of food, while Taste and Convenience relate to user enjoyment and practicality.\n"
            "{\n"
            "  \"latents\": [\n"
            "    {\"name\": \"HealthLat\", \"factors\": [\"Nutrition\", \"Vitamins\"]},\n"
            "    {\"name\": \"EnjoyLat\", \"factors\": [\"Taste\", \"Convenience\"]}\n"
            "  ]\n"
            "}"
        )
    },
    # Example 2 user dialogue
    {
        "role": "user",
        "content": (
            "Please identify latent variables and assign each factor to a latent. "
            "Then return JSON with fields:\n"
            "  latents: [{\"name\": string, \"factors\": [...]}, ...],\n"
            "Factors: [\"Reward\", \"Risk\", \"TimePressure\", \"Collaboration\"]"
        )
    },
    # Example 2 assistant output (with CoT)
    {
        "role": "assistant",
        "content": (
            "Thought: Reward represents benefits gained, Risk and TimePressure both represent potential costs or pressures, and Collaboration relates to social interaction.\n"
            "{\n"
            "  \"latents\": [\n"
            "    {\"name\": \"BenefitLat\", \"factors\": [\"Reward\"]},\n"
            "    {\"name\": \"CostLat\", \"factors\": [\"Risk\", \"TimePressure\"]},\n"
            "    {\"name\": \"SocialLat\", \"factors\": [\"Collaboration\"]}\n"
            "  ]\n"
            "}"
        )
    },
    # Example 3 user dialogue
    {
        "role": "user",
        "content": (
            "Please identify latent variables and assign each factor to a latent. "
            "Then return JSON with fields:\n"
            "  latents: [{\"name\": string, \"factors\": [...]}, ...],\n"
            "Factors: [\"Speed\", \"Accuracy\", \"Cost\", \"Scalability\"]"
        )
    },
    # Example 3 assistant output (with CoT)
    {
        "role": "assistant",
        "content": (
            "Thought: Speed, Accuracy, and Scalability all describe performance-related characteristics, while Cost describes resource expenditure.\n"
            "{\n"
            "  \"latents\": [\n"
            "    {\"name\": \"PerformanceLat\", \"factors\": [\"Speed\", \"Accuracy\", \"Scalability\"]},\n"
            "    {\"name\": \"CostLat\", \"factors\": [\"Cost\"]}\n"
            "  ]\n"
            "}"
        )
    },
    # Example 4 user dialogue
    {
        "role": "user",
        "content": (
            "Please identify latent variables and assign each factor to a latent. "
            "Then return JSON with fields:\n"
            "  latents: [{\"name\": string, \"factors\": [...]}, ...],\n"
            "Factors: [\"Usability\", \"Security\", \"Maintainability\", \"Portability\", \"Reliability\"]"
        )
    },
    # Example 4 assistant output (with CoT)
    {
        "role": "assistant",
        "content": (
            "Thought: Usability and Portability focus on user experience and access, Reliability and Maintainability focus on software quality over time, and Security is a distinct concern.\n"
            "{\n"
            "  \"latents\": [\n"
            "    {\"name\": \"UXLat\", \"factors\": [\"Usability\", \"Portability\"]},\n"
            "    {\"name\": \"QualityLat\", \"factors\": [\"Reliability\", \"Maintainability\"]},\n"
            "    {\"name\": \"SecurityLat\", \"factors\": [\"Security\"]}\n"
            "  ]\n"
            "}"
        )
    }
]


GENERATE_LATENT_PROBS_SHOTS = [
    {
        "role": "system",
        "content": (
            "Please perform a brief chain-of-thought (step-by-step) before outputting the final JSON:\n\n"
            "You are an AI assistant. You will be given:\n"
            "  • A list of latents where each latent has:\n"
            "    – its name\n"
            "    – the list of factor descriptions it groups\n"
            "  • Two competing statements (Statement1 vs. Statement2)\n\n"
            "Your task: Think through the semantic content of the factors relative to the statements, "
            "and estimate for each latent a probability pair [p1, p0]:\n"
            "  • p1 = probability the latent supports Statement1\n"
            "  • p0 = probability the latent supports Statement2\n\n"
            "Begin your answer with “Thought:” to show your reasoning, then output exactly a JSON object "
            "mapping each latent name to its [p1, p0] (no extra text)."
        )
    },
    # Example 1
    {
        "role": "user",
        "content": (
            "Latents with factors:\n"
            "[\n"
            "  {\"name\":\"Performance\",\"factors\":[\"Faster processing\",\"Efficient resource use\"]},\n"
            "  {\"name\":\"Stability\",\"factors\":[\"Crash reports\",\"Memory leaks\"]}\n"
            "]\n\n"
            "Statement1: The system improves performance.\n"
            "Statement2: The system does not improve performance."
        )
    },
    {
        "role": "assistant",
        "content": (
            "Thought: The Performance latent groups factors that directly indicate faster and more efficient operation, "
            "which strongly supports Statement1. The Stability latent lists issues that undermine reliability, which indirectly "
            "suggests performance might not improve overall. I’d estimate Performance around [0.85, 0.15] and Stability around [0.30, 0.70].\n"
            "{\n"
            "  \"Performance\": [0.85, 0.15],\n"
            "  \"Stability\":   [0.30, 0.70]\n"
            "}"
        )
    },
    # Example 2
    {
        "role": "user",
        "content": (
            "Latents with factors:\n"
            "[\n"
            "  {\"name\":\"HealthLat\",\"factors\":[\"Nutrition benefits\"]},\n"
            "  {\"name\":\"EnjoyLat\",\"factors\":[\"Taste appeal\",\"Fun presentation\"]}\n"
            "]\n\n"
            "Statement1: Healthy eating is fun.\n"
            "Statement2: Healthy eating is not fun."
        )
    },
    {
        "role": "assistant",
        "content": (
            "Thought: Nutrition benefits relate to health but don’t guarantee fun, so HealthLat feels neutral to slightly positive. "
            "EnjoyLat clearly centers on taste and fun aspects, strongly supporting Statement1. I’d give HealthLat [0.55, 0.45] and EnjoyLat [0.85, 0.15].\n"
            "{\n"
            "  \"HealthLat\": [0.55, 0.45],\n"
            "  \"EnjoyLat\":  [0.85, 0.15]\n"
            "}"
        )
    },
    # Example 3
    {
        "role": "user",
        "content": (
            "Latents with factors:\n"
            "[\n"
            "  {\"name\":\"CostLat\",\"factors\":[\"High price\",\"Subscription fees\"]},\n"
            "  {\"name\":\"ValueLat\",\"factors\":[\"Quality components\",\"Rich feature set\"]}\n"
            "]\n\n"
            "Statement1: The product offers good value for money.\n"
            "Statement2: The product is overpriced."
        )
    },
    {
        "role": "assistant",
        "content": (
            "Thought: CostLat’s factors emphasize expense, which leans toward overpriced, but subscription might add long-term value so moderate. "
            "ValueLat’s factors directly point to quality and rich features, strongly favoring good value. I’d estimate CostLat [0.40, 0.60] "
            "and ValueLat [0.80, 0.20].\n"
            "{\n"
            "  \"CostLat\":  [0.40, 0.60],\n"
            "  \"ValueLat\": [0.80, 0.20]\n"
            "}"
        )
    },
    # Example 4
    {
        "role": "user",
        "content": (
            "Latents with factors:\n"
            "[\n"
            "  {\"name\":\"TrustLat\",\"factors\":[\"Brand reputation\",\"Positive reviews\"]}\n"
            "]\n\n"
            "Statement1: Brand X is trustworthy.\n"
            "Statement2: Brand X is not trustworthy."
        )
    },
    {
        "role": "assistant",
        "content": (
            "Thought: Brand reputation and positive reviews both semantically signal trustworthiness, so this latent strongly supports Statement1. "
            "I’d estimate TrustLat at [0.90, 0.10].\n"
            "{\n"
            "  \"TrustLat\": [0.90, 0.10]\n"
            "}"
        )
    }
]
