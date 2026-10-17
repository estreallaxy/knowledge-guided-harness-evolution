
FEW_SHOT_GEN_XSUM = [
    # Example 1: generate 4 sentences (2 Consistent, 2 Contradictory)
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Generate 2 sentences that are Consistent with this statement and 2 that contradict it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. The report describes Scottish council tax reform as requiring significant resources and careful planning.\n"
            "2. Officials acknowledge that overhauling Scotland's council tax system will demand substantial effort and coordination.\n"
            "3. The report characterizes council tax reform in Scotland as a simple administrative adjustment.\n"
            "4. According to the findings, reforming Scottish council tax would be a minor policy change requiring minimal effort."
        )
    },

    # Example 2: generate 2 sentences (1 Consistent, 1 Contradictory)
    {
        'role': 'user',
        'content': (
            "scenario and statement: A memorial service has been held in Portsmouth to mark the 70th anniversary of VJ Day.\n"
            "Generate 1 that is Consistent with this statement and 1 that contradicts it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. Portsmouth hosted a commemorative ceremony to honor the 70th anniversary of Victory over Japan Day.\n"
            "2. No memorial events were organized in Portsmouth for the VJ Day anniversary this year."
        )
    }
]

FEW_SHOT_VOTE_XSUM = [
    # Example 1: Consistent (matches the fact)
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Factor: Report characterizes reform as significant\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement explicitly says the report describes council tax reform as a \"major undertaking\", which aligns with characterizing it as significant.\n"
            "Final answer:\n"
            "{\"Report characterizes reform as significant\": \"Consistent\"}"
        )
    },

    # Example 2: Contradictory (conflicts with the fact)
    {
        'role': 'user',
        'content': (
            "scenario and statement: A memorial service has been held in Portsmouth to mark the 70th anniversary of VJ Day.\n"
            "Factor: No commemorative events occurred in Portsmouth\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement confirms that a memorial service was held in Portsmouth, so claiming no events occurred directly contradicts this fact.\n"
            "Final answer:\n"
            "{\"No commemorative events occurred in Portsmouth\": \"Contradictory\"}"
        )
    },

    # Example 3: Consistent
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Factor: Report exists on council tax reform\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement references a report about council tax reform, so the existence of such a report is consistent with the statement.\n"
            "Final answer:\n"
            "{\"Report exists on council tax reform\": \"Consistent\"}"
        )
    },

    # Example 4: Contradictory
    {
        'role': 'user',
        'content': (
            "scenario and statement: A memorial service has been held in Portsmouth to mark the 70th anniversary of VJ Day.\n"
            "Factor: Service commemorated 60th anniversary\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement specifies it was the 70th anniversary, not the 60th, so this factor contradicts the timeline.\n"
            "Final answer:\n"
            "{\"Service commemorated 60th anniversary\": \"Contradictory\"}"
        )
    },

    # Example 5: Consistent
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Factor: Reform applies to Scotland\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement clearly mentions council tax reform \"in Scotland\", so this geographical factor is accurate.\n"
            "Final answer:\n"
            "{\"Reform applies to Scotland\": \"Consistent\"}"
        )
    }
]

FEW_SHOT_EXT_XSUM = [
    # Example 1: Council tax reform factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report. "
            "The comprehensive review examined current valuation methods, proposed alternative assessment systems, "
            "and estimated implementation costs at £45 million over three years. Local authorities expressed concerns "
            "about administrative burden, while housing advocates welcomed potential fairness improvements.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. The report's assessment confirms that council tax reform requires substantial resources and planning.\n"
            "2. Implementation costs of £45 million demonstrate the significant scale of the proposed changes.\n"
            "3. The report describes council tax reform as a straightforward administrative process.\n"
            "4. Local authorities found the proposed changes would require minimal additional work.\n\n"
            "Extract the distinct factors and return a JSON object with two keys—\"Consistent\" and \"Contradictory\"—each mapping to the list of factors."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing the sentences:\n"
            "- Sentences 1 & 2 align with the \"major undertaking\" characterization (substantial resources, significant costs).\n"
            "- Sentences 3 & 4 contradict this assessment (straightforward process, minimal work).\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Reform complexity (substantial resources required)\",\n"
            "    \"Implementation scale (£45 million cost)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Process simplicity (straightforward administrative)\",\n"
            "    \"Work burden (minimal additional effort)\"\n"
            "]}"
        )
    },

    # Example 2: VJ Day memorial service factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: A memorial service has been held in Portsmouth to mark the 70th anniversary of VJ Day. "
            "The ceremony took place at the Naval Memorial, attended by veterans, military personnel, and local dignitaries. "
            "Wreaths were laid by the Lord Mayor and Royal Navy representatives, followed by a two-minute silence "
            "and the playing of the Last Post. The service concluded with hymns performed by the Portsmouth Military Choir.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. Portsmouth hosted a commemorative ceremony for the 70th anniversary of Victory over Japan Day.\n"
            "2. The service included traditional elements like wreath laying and military honors.\n"
            "3. No memorial events were organized in Portsmouth for VJ Day this year.\n"
            "4. The ceremony commemorated the 75th anniversary of VJ Day, not the 70th.\n\n"
            "Extract the distinct factors and return a JSON object with keys \"Consistent\" and \"Contradictory\"."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Breaking down the sentences:\n"
            "- Sentences 1 & 2 confirm the memorial service details (location, anniversary, ceremonial elements).\n"
            "- Sentences 3 & 4 contradict these facts (no events, wrong anniversary).\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Event occurrence (Portsmouth memorial service)\",\n"
            "    \"Ceremonial elements (wreath laying, military honors)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Event existence (no memorial events)\",\n"
            "    \"Anniversary timing (75th vs 70th)\"\n"
            "]}"
        )
    }
]

FEW_SHOT_PRUNE_XSUM = [
    # Example 1: Council tax reform factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Cluster 'Reform complexity', factors:\n"
            '["Major undertaking", "Significant effort required", "Substantial resources needed", '
            '"Complex implementation", "Major policy change"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Major undertaking' vs 'Significant effort required' vs 'Complex implementation': same concept → keep 'Major undertaking' (matches original statement)\n"
            "- 'Substantial resources needed' is unique (resource aspect)\n"
            "- 'Major policy change' is unique (policy classification)\n\n"
            "Final answer:\n"
            '["Major undertaking", '
            '"Substantial resources needed", '
            '"Major policy change"]'
        )
    },

    # Example 2: Memorial service factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: A memorial service has been held in Portsmouth to mark the 70th anniversary of VJ Day.\n"
            "Cluster 'Service details', factors:\n"
            '["Memorial service", "Commemorative ceremony", "VJ Day anniversary", "70th anniversary commemoration"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Memorial service' vs 'Commemorative ceremony': same concept → keep 'Memorial service' (matches original statement)\n"
            "- 'VJ Day anniversary' vs '70th anniversary commemoration': both refer to the same event → keep '70th anniversary of VJ Day' (more specific)\n\n"
            "Final answer:\n"
            '["Memorial service", "70th anniversary of VJ Day"]'
        )
    }
]

FEW_SHOT_CLUSTER_NAME_XSUM = [
    # Example 1: Reform complexity factors
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"major undertaking\", \"substantial resources needed\", \"complex implementation\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Reform Complexity"
    },
    # Example 2: Memorial service elements
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"wreath laying\", \"military honors\", \"commemorative ceremony\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Service Elements"
    },
    # Example 3: Anniversary timing
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"70th anniversary\", \"VJ Day commemoration\", \"anniversary timing\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Anniversary Details"
    },
    # Example 4: Policy impact
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"administrative burden\", \"implementation costs\", \"local authority concerns\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Implementation Impact"
    },
    # Example 5: Location specifics
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"Portsmouth venue\", \"Naval Memorial location\", \"local ceremony\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Location Details"
    },
    # Example 6: Report findings
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"report assessment\", \"official evaluation\", \"expert analysis\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Report Analysis"
    },
    # Example 7: Ceremony participants
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"veterans attendance\", \"military personnel\", \"local dignitaries\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Ceremony Participants"
    },
    # Example 8: Tax system aspects
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"valuation methods\", \"assessment systems\", \"council tax structure\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Tax System Features"
    },
    # Example 9: Memorial traditions
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"two-minute silence\", \"Last Post playing\", \"hymn performance\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Memorial Traditions"
    },
    # Example 10: Policy stakeholders
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"local authorities\", \"housing advocates\", \"government officials\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Policy Stakeholders"
    },
    # Example 11: Service timing
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"ceremony schedule\", \"memorial timing\", \"anniversary date\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Event Timing"
    },
    # Example 12: Reform scope
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"Scotland-wide reform\", \"national policy change\", \"country-level implementation\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Reform Scope"
    },
    # Example 13: Historical significance
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"VJ Day importance\", \"WWII commemoration\", \"historical remembrance\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Historical Significance"
    },
    # Example 14: Financial implications
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"implementation costs\", \"budget requirements\", \"financial planning\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Financial Implications"
    },
    # Example 15: Community response
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"public reaction\", \"stakeholder feedback\", \"community concerns\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Community Response"
    }
]

MAPPING_VOTE_SHOT_XSUM = [
    # Complex fact-checking example requiring reading comprehension
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "document excerpt: The comprehensive review of Scottish council tax highlighted significant challenges in updating "
            "property valuations, estimated costs of £45 million over three years, and concerns from local authorities "
            "about administrative complexity. The report noted that \"substantial planning and resources\" would be required "
            "for successful implementation, though some housing advocates argued the changes are \"long overdue\" and \"manageable.\"\n\n"
            "candidate factors: ["
            "\"report characterization alignment\", "
            "\"resource requirement assessment\", "
            "\"implementation complexity\", "
            "\"stakeholder opinion variance\", "
            "\"geographical scope accuracy\""
            "]\n\n"
            "task: select the factors most reasonably related to whether the claim is supported. "
            "think step by step about each factor's relevance, then provide your selection as a JSON object "
            "in this exact format: {\"answer\": [\"factor1\", \"factor2\", ...]}"
        )
    },
    {
        'role': 'assistant',
        'content': (
            "analyzing each factor:\n"
            "- \"report characterization alignment\": directly relevant - verifies if the report actually characterizes reform as \"major undertaking\".\n"
            "- \"resource requirement assessment\": highly relevant - substantial resources (£45 million) support the \"major undertaking\" claim.\n"
            "- \"implementation complexity\": directly relevant - administrative complexity aligns with \"major undertaking\" characterization.\n"
            "- \"stakeholder opinion variance\": less relevant - different opinions don't affect what the report specifically stated.\n"
            "- \"geographical scope accuracy\": relevant - confirms the reform applies to Scotland as claimed.\n\n"
            "final answer:\n"
            "{\"answer\": ["
            "\"report characterization alignment\", "
            "\"resource requirement assessment\", "
            "\"implementation complexity\", "
            "\"geographical scope accuracy\""
            "]}"
        )
    }
]



###############
'''''COVID'''''
################

FEW_SHOT_GEN_COVID = [
    # Example 1: generate 4 sentences (2 Consistent, 2 Contradictory)
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation.\n"
            "Generate 2 sentences that are Consistent with this statement and 2 that contradict it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. Recovering COVID-19 patients show protective mechanisms against blood vessel damage through ongoing immune system activity.\n"
            "2. The persistent immune response in convalescent patients provides a shield against endothelial cell dysfunction.\n"
            "3. Convalescent COVID-19 patients experience increased endothelial dysfunction despite continued immune activation.\n"
            "4. The ongoing immune response in recovered patients actually worsens blood vessel function rather than protecting it."
        )
    },

    # Example 2: generate 2 sentences (1 Consistent, 1 Contradictory)
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Generate 1 that is Consistent with this statement and 1 that contradicts it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. The report describes Scottish council tax reform as requiring significant resources and careful planning.\n"
            "2. The report characterizes council tax reform in Scotland as a simple administrative adjustment."
        )
    }
]

FEW_SHOT_VOTE_COVID = [
    # Example 1: Consistent (matches the fact)
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation.\n"
            "Factor: Immune activation provides protective effect\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement claims that persistent immune activation makes patients resistant to endothelial dysfunction, which means immune activation provides protection.\n"
            "Final answer:\n"
            "{\"Immune activation provides protective effect\": \"Consistent\"}"
        )
    },

    # Example 2: Contradictory (conflicts with the fact)
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation.\n"
            "Factor: Immune activation worsens endothelial function\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement says immune activation leads to resistance against endothelial dysfunction, but this factor claims it worsens endothelial function, which directly contradicts the protective effect.\n"
            "Final answer:\n"
            "{\"Immune activation worsens endothelial function\": \"Contradictory\"}"
        )
    },

    # Example 3: Consistent
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Factor: Report characterizes reform as significant\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement explicitly says the report describes council tax reform as a \"major undertaking\", which aligns with characterizing it as significant.\n"
            "Final answer:\n"
            "{\"Report characterizes reform as significant\": \"Consistent\"}"
        )
    },

    # Example 4: Contradictory
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation.\n"
            "Factor: Patients show increased endothelial dysfunction\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement claims patients are resistant to endothelial dysfunction, but this factor suggests they show increased dysfunction, which directly contradicts the resistance claim.\n"
            "Final answer:\n"
            "{\"Patients show increased endothelial dysfunction\": \"Contradictory\"}"
        )
    },

    # Example 5: Consistent
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation.\n"
            "Factor: Persistent immune response continues in convalescent patients\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement mentions \"persistent immune activation\" as the mechanism, so the continuation of immune response in convalescent patients is consistent.\n"
            "Final answer:\n"
            "{\"Persistent immune response continues in convalescent patients\": \"Consistent\"}"
        )
    }
]

FEW_SHOT_EXT_COVID = [
    # Example 1: COVID convalescent patients factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation. "
            "The study analyzed blood samples from 150 recovered patients and found maintained endothelial protective mechanisms. "
            "Inflammatory markers remained elevated but correlated with improved vascular function rather than damage. "
            "Researchers noted that ongoing immune activity appeared to provide a protective shield against vessel dysfunction.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. Persistent immune activation in convalescent patients creates a protective barrier against endothelial damage.\n"
            "2. The ongoing immune response maintains vascular protective mechanisms in recovered COVID-19 patients.\n"
            "3. Convalescent patients show increased endothelial dysfunction despite continued immune activation.\n"
            "4. The persistent immune response actually damages blood vessel function in recovered patients.\n\n"
            "Extract the distinct factors and return a JSON object with two keys—\"Consistent\" and \"Contradictory\"—each mapping to the list of factors."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing the sentences:\n"
            "- Sentences 1 & 2 align with the protective immune mechanism (immune barrier, vascular protection).\n"
            "- Sentences 3 & 4 contradict this protection (increased dysfunction, immune damage).\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Immune protective mechanism (barrier against damage)\",\n"
            "    \"Vascular protection maintenance (ongoing immune response)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Endothelial dysfunction increase (despite immune activation)\",\n"
            "    \"Immune-mediated vascular damage (harmful immune response)\"\n"
            "]}"
        )
    },

    # Example 2: Council tax reform factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report. "
            "The comprehensive review examined current valuation methods, proposed alternative assessment systems, "
            "and estimated implementation costs at £45 million over three years. Local authorities expressed concerns "
            "about administrative burden, while housing advocates welcomed potential fairness improvements.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. The report's assessment confirms that council tax reform requires substantial resources and planning.\n"
            "2. Implementation costs of £45 million demonstrate the significant scale of the proposed changes.\n"
            "3. The report describes council tax reform as a straightforward administrative process.\n"
            "4. Local authorities found the proposed changes would require minimal additional work.\n\n"
            "Extract the distinct factors and return a JSON object with keys \"Consistent\" and \"Contradictory\"."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Breaking down the sentences:\n"
            "- Sentences 1 & 2 confirm the \"major undertaking\" characterization (substantial resources, significant costs).\n"
            "- Sentences 3 & 4 contradict this assessment (straightforward process, minimal work).\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Reform complexity (substantial resources required)\",\n"
            "    \"Implementation scale (£45 million cost)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Process simplicity (straightforward administrative)\",\n"
            "    \"Work burden (minimal additional effort)\"\n"
            "]}"
        )
    }
]

FEW_SHOT_PRUNE_COVID = [
    # Example 1: COVID immune protection factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: Convalescent covid-19 patients are resistant to endothelial dysfunction due to persistent immune activation.\n"
            "Cluster 'Immune protective mechanisms', factors:\n"
            '["Immune activation protection", "Persistent immune response", "Ongoing immune activity", '
            '"Immune barrier against dysfunction", "Protective immune mechanisms"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Immune activation protection' vs 'Protective immune mechanisms' vs 'Immune barrier against dysfunction': same concept → keep 'Immune activation protection' (most direct)\n"
            "- 'Persistent immune response' vs 'Ongoing immune activity': same concept → keep 'Persistent immune response' (matches statement wording)\n\n"
            "Final answer:\n"
            '["Immune activation protection", '
            '"Persistent immune response"]'
        )
    },

    # Example 2: Council tax reform factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "Cluster 'Reform complexity', factors:\n"
            '["Major undertaking", "Significant effort required", "Substantial resources needed", '
            '"Complex implementation", "Major policy change"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Major undertaking' vs 'Significant effort required' vs 'Complex implementation': same concept → keep 'Major undertaking' (matches original statement)\n"
            "- 'Substantial resources needed' is unique (resource aspect)\n"
            "- 'Major policy change' is unique (policy classification)\n\n"
            "Final answer:\n"
            '["Major undertaking", '
            '"Substantial resources needed", '
            '"Major policy change"]'
        )
    }
]

FEW_SHOT_CLUSTER_NAME_COVID = [
    # Example 1: Immune protection mechanisms
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"immune activation protection\", \"persistent immune response\", \"vascular protective mechanisms\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Immune Protection"
    },
    # Example 2: Endothelial dysfunction markers
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"endothelial cell activation\", \"vascular damage markers\", \"blood vessel dysfunction\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Endothelial Dysfunction"
    },
    # Example 3: COVID convalescent status
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"recovered patients\", \"convalescent status\", \"post-COVID condition\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Patient Status"
    },
    # Example 4: Inflammatory markers
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"cytokine levels\", \"inflammatory response\", \"immune activation markers\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Inflammatory Markers"
    },
    # Example 5: Vascular function assessment
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"blood vessel function\", \"endothelial performance\", \"vascular health metrics\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Vascular Function"
    },
    # Example 6: Reform complexity factors
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"major undertaking\", \"substantial resources needed\", \"complex implementation\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Reform Complexity"
    },
    # Example 7: Research methodology
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"blood sample analysis\", \"patient cohort study\", \"biomarker measurement\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Research Methods"
    },
    # Example 8: Clinical outcomes
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"patient recovery\", \"treatment response\", \"health improvement\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Clinical Outcomes"
    },
    # Example 9: Cardiovascular risk factors
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"underlying cardiovascular risk\", \"heart disease history\", \"vascular risk factors\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Cardiovascular Risk"
    },
    # Example 10: Cellular biomarkers
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"circulating endothelial cells\", \"ICAM1 expression\", \"P-selectin levels\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Cellular Biomarkers"
    },
    # Example 11: Memorial service elements
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"wreath laying\", \"military honors\", \"commemorative ceremony\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Service Elements"
    },
    # Example 12: Immune system activity
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"T lymphocyte activation\", \"cytokine production\", \"immune cell function\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Immune Activity"
    },
    # Example 13: Study population
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"convalescent patients\", \"recovered COVID cases\", \"post-infection cohort\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Study Population"
    },
    # Example 14: Vascular protection mechanisms
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"endothelial resistance\", \"protective barriers\", \"dysfunction prevention\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Vascular Protection"
    }
]

MAPPING_VOTE_SHOT_COVID = [
    # Complex fact-checking example requiring reading comprehension
    {
        'role': 'user',
        'content': (
            "scenario and statement: Reform of the council tax in Scotland is a \"major undertaking\", according to a report.\n"
            "document excerpt: A review for the Commission on Local Tax Reform said there was no \"magic bullet\" to cure defects in the system. "
            "It said the council tax had built-in problems \"from day one\" but a failure to modify it had stored up more difficulties for policy makers. "
            "The commission, set up by the Scottish government and council body Cosla, will report back later this year. "
            "Prof Kenneth Gibb, from the University of Glasgow, was asked to review different systems of local taxation across the world. "
            "He found that a tax on property was used by almost all OECD countries and was seen by academics as a \"good tax\" because it was stable, "
            "difficult to avoid and could have a desirable impact on housing markets. But it also generated confusion with taxpayers unclear whether "
            "it was a tax on wealth or a charge for services such as refuse collection. Some felt it was unfair because it was not linked to current income. "
            "Prof Gibb noted that a local income tax, used by many countries, was generally perceived as fairer. But he found such a system created "
            "difficulties for local authorities because it meant their income fluctuated. There was also little opportunity to vary tax rates to reflect "
            "local priorities. He said: \"It is clear there is no magic bullet. Past experience from the UK and across the world shows that reform is "
            "always going to be difficult and will inevitably be bound up with the previous experiences and traumas of past reform. So whilst the current "
            "council tax has many deficiencies, change and reform is a major undertaking.\" The commission now intends to hold a public consultation "
            "across Scotland before publishing its report in the autumn.\n\n"
            "candidate factors: ["
            "\"expert direct quote confirmation\", "
            "\"reform difficulty assessment\", "
            "\"commission establishment context\", "
            "\"alternative systems comparison\", "
            "\"geographical scope verification\""
            "]\n\n"
            "task: select the factors most reasonably related to whether the claim is supported. "
            "think step by step about each factor's relevance, then provide your selection as a JSON object "
            "in this exact format: {\"answer\": [\"factor1\", \"factor2\", ...]}"
        )
    },
    {
        'role': 'assistant',
        'content': (
            "analyzing each factor:\n"
            "- \"expert direct quote confirmation\": directly relevant - Prof Gibb explicitly states \"change and reform is a major undertaking\".\n"
            "- \"reform difficulty assessment\": highly relevant - document details why reform is difficult (past traumas, no magic bullet, built-in problems).\n"
            "- \"commission establishment context\": relevant - confirms this is an official report from the Commission on Local Tax Reform.\n"
            "- \"alternative systems comparison\": less relevant - while mentioned, it doesn't directly support the \"major undertaking\" characterization.\n"
            "- \"geographical scope verification\": relevant - confirms the reform applies to Scotland as stated.\n\n"
            "final answer:\n"
            "{\"answer\": ["
            "\"expert direct quote confirmation\", "
            "\"reform difficulty assessment\", "
            "\"commission establishment context\", "
            "\"geographical scope verification\""
            "]}"
        )
    }
]



###############
'''''CNN'''''
################

FEW_SHOT_GEN_CNN = [
    # Example 1: Uber security hiring
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns . the $ 40 billion taxi service has been plagued by serious accusations of failing to vet its drivers .\n"
            "Generate 2 sentences that are Consistent with this statement and 2 that contradict it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. Facebook's former security chief Joe Sullivan has been recruited by Uber to address mounting driver vetting issues.\n"
            "2. The $40 billion ride-sharing company hired Sullivan to tackle widespread safety concerns about inadequate background checks.\n"
            "3. Joe Sullivan left Facebook to join a different tech company unrelated to transportation services.\n"
            "4. Uber has successfully resolved all driver screening issues and no longer faces safety-related accusations."
        )
    },

    # Example 2: Quokka incident
    {
        'role': 'user',
        'content': (
            "scenario and statement: two french male tourists allegedly ignited an aerosol spray with a lighter causing a large flame to make contact with a quokka on rottnest island off perth in western australia on april 3 .\n"
            "Generate 1 that is Consistent with this statement and 1 that contradicts it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. French tourists used improvised flame-throwing device to harm a native Australian animal on Rottnest Island.\n"
            "2. The two French visitors were merely taking photographs of the quokka without any harmful intent."
        )
    }
]

FEW_SHOT_VOTE_CNN = [
    # Example 1: Consistent (matches the fact)
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns . the $ 40 billion taxi service has been plagued by serious accusations of failing to vet its drivers .\n"
            "Factor: Corporate executive transition for security expertise\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement describes Joe Sullivan leaving Facebook's security chief role to help Uber, which is exactly a corporate executive transition focused on security expertise.\n"
            "Final answer:\n"
            "{\"Corporate executive transition for security expertise\": \"Consistent\"}"
        )
    },

    # Example 2: Contradictory
    {
        'role': 'user',
        'content': (
            "scenario and statement: two french male tourists allegedly ignited an aerosol spray with a lighter causing a large flame to make contact with a quokka on rottnest island off perth in western australia on april 3 .\n"
            "Factor: Accidental wildlife encounter without harm\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement describes deliberate ignition of aerosol spray causing flame contact with the animal, which contradicts the idea of an accidental encounter without harm.\n"
            "Final answer:\n"
            "{\"Accidental wildlife encounter without harm\": \"Contradictory\"}"
        )
    },

    # Example 3: Consistent
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns . the $ 40 billion taxi service has been plagued by serious accusations of failing to vet its drivers .\n"
            "Factor: Driver background check deficiencies\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement explicitly mentions Uber being 'plagued by serious accusations of failing to vet its drivers', which directly aligns with driver background check deficiencies.\n"
            "Final answer:\n"
            "{\"Driver background check deficiencies\": \"Consistent\"}"
        )
    },

    # Example 4: Contradictory
    {
        'role': 'user',
        'content': (
            "scenario and statement: two french male tourists allegedly ignited an aerosol spray with a lighter causing a large flame to make contact with a quokka on rottnest island off perth in western australia on april 3 .\n"
            "Factor: Professional wildlife research activity\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement describes tourists using improvised flame devices to harm an animal, which contradicts any professional wildlife research activity.\n"
            "Final answer:\n"
            "{\"Professional wildlife research activity\": \"Contradictory\"}"
        )
    },

    # Example 5: Consistent
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns . the $ 40 billion taxi service has been plagued by serious accusations of failing to vet its drivers .\n"
            "Factor: High-value company valuation\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement specifically mentions 'the $40 billion taxi service', which confirms the high valuation of the company.\n"
            "Final answer:\n"
            "{\"High-value company valuation\": \"Consistent\"}"
        )
    }
]

FEW_SHOT_EXT_CNN = [
    # Example 1: Uber security hiring factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns . the $ 40 billion taxi service has been plagued by serious accusations of failing to vet its drivers . "
            "Sullivan brings extensive cybersecurity experience from the Justice Department and major tech companies. "
            "His appointment comes amid multiple lawsuits and high-profile assault cases involving Uber drivers. "
            "The company hopes his expertise can address both digital security and physical safety challenges.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. Facebook's security chief Joe Sullivan has been recruited specifically to address Uber's driver vetting failures.\n"
            "2. The $40 billion ride-sharing company hired Sullivan due to mounting safety-related accusations and legal challenges.\n"
            "3. Joe Sullivan left Facebook to join a startup focused on social media analytics rather than transportation.\n"
            "4. Uber has resolved all safety concerns and hired Sullivan for routine technology maintenance tasks.\n\n"
            "Extract the distinct factors and return a JSON object with two keys—\"Consistent\" and \"Contradictory\"—each mapping to the list of factors."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing the sentences:\n"
            "- Sentences 1 & 2 align with the security expertise transfer and safety crisis response.\n"
            "- Sentences 3 & 4 contradict the transportation focus and urgent safety needs.\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Executive security expertise transfer (Facebook to Uber)\",\n"
            "    \"Safety crisis response (driver vetting failures)\",\n"
            "    \"High-stakes company valuation ($40 billion)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Non-transportation industry focus (social media analytics)\",\n"
            "    \"Routine maintenance hiring (resolved safety concerns)\"\n"
            "]}"
        )
    },

    # Example 2: Quokka incident factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: two french male tourists allegedly ignited an aerosol spray with a lighter causing a large flame to make contact with a quokka on rottnest island off perth in western australia on april 3 . "
            "The incident occurred at a protected wildlife sanctuary where quokkas are native species. "
            "Witnesses reported seeing the tourists deliberately create makeshift flamethrowers. "
            "The animal suffered minor burns but survived the attack.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. French tourists used improvised flame devices to deliberately harm a native Australian marsupial.\n"
            "2. The incident took place on April 3rd at Rottnest Island involving aerosol ignition and animal contact.\n"
            "3. The visitors were conducting a scientific experiment on animal behavior with proper permits.\n"
            "4. No flame or harmful contact occurred during the tourists' wildlife photography session.\n\n"
            "Extract the distinct factors and return a JSON object with keys \"Consistent\" and \"Contradictory\"."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Breaking down the sentences:\n"
            "- Sentences 1 & 2 confirm the deliberate harm and specific incident details.\n"
            "- Sentences 3 & 4 contradict the harmful intent and flame contact.\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Deliberate animal harm (improvised flame devices)\",\n"
            "    \"Specific incident details (April 3, Rottnest Island, aerosol ignition)\",\n"
            "    \"Tourist nationality identification (French visitors)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Scientific research justification (proper permits)\",\n"
            "    \"No harmful contact (photography session)\"\n"
            "]}"
        )
    }
]

FEW_SHOT_PRUNE_CNN = [
    # Example 1: Uber security factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns .\n"
            "Cluster 'Executive transitions', factors:\n"
            '["Corporate security chief departure", "Facebook executive exit", "Leadership role transition", '
            '"Senior security position change", "Chief security officer movement"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Corporate security chief departure' vs 'Facebook executive exit' vs 'Senior security position change' vs 'Chief security officer movement': same concept → keep 'Facebook executive exit' (most specific)\n"
            "- 'Leadership role transition' is unique (broader transition aspect)\n\n"
            "Final answer:\n"
            '["Facebook executive exit", '
            '"Leadership role transition"]'
        )
    },

    # Example 2: Wildlife incident factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: two french male tourists allegedly ignited an aerosol spray with a lighter causing a large flame to make contact with a quokka on rottnest island .\n"
            "Cluster 'Animal harm methods', factors:\n"
            '["Aerosol spray ignition", "Improvised flamethrower creation", "Lighter flame generation", '
            '"Makeshift fire device", "Flame contact method"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Aerosol spray ignition' vs 'Lighter flame generation': different components → keep both\n"
            "- 'Improvised flamethrower creation' vs 'Makeshift fire device': same concept → keep 'Improvised flamethrower creation' (more descriptive)\n"
            "- 'Flame contact method' is unique (describes the harm mechanism)\n\n"
            "Final answer:\n"
            '["Aerosol spray ignition", '
            '"Lighter flame generation", '
            '"Improvised flamethrower creation", '
            '"Flame contact method"]'
        )
    }
]

FEW_SHOT_CLUSTER_NAME_CNN = [
    # Example 1: Security expertise transfer
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"facebook security chief departure\", \"uber safety concerns\", \"executive recruitment\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Security Leadership"
    },
    # Example 2: Driver vetting issues
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"driver background checks\", \"vetting failures\", \"safety accusations\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Driver Screening"
    },
    # Example 3: Corporate valuation
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"40 billion dollar valuation\", \"company worth\", \"market value\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Company Valuation"
    },
    # Example 4: Tourist incident details
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"french tourists\", \"rottnest island location\", \"april 3 date\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Incident Details"
    },
    # Example 5: Animal harm method
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"aerosol spray ignition\", \"lighter flame\", \"fire contact\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Harm Method"
    },
    # Example 6: Wildlife protection
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"quokka species\", \"native animal protection\", \"wildlife sanctuary\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Wildlife Protection"
    },
    # Example 7: Legal consequences
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"animal cruelty charges\", \"court appearance\", \"tourist eviction\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Legal Consequences"
    },
    # Example 8: Geographic location
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"western australia\", \"perth vicinity\", \"rottnest island\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Geographic Location"
    },
    # Example 9: Executive background
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"cybersecurity experience\", \"justice department background\", \"tech industry expertise\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Professional Background"
    },
    # Example 10: Safety crisis
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"multiple lawsuits\", \"assault cases\", \"public safety concerns\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Safety Crisis"
    }
]

MAPPING_VOTE_SHOT_CNN = [
    # Complex news verification example requiring fact-checking
    {
        'role': 'user',
        'content': (
            "scenario and statement: joe sullivan , 46 , will leave his role as facebook 's security chief to help uber defend safety concerns . the $ 40 billion taxi service has been plagued by serious accusations of failing to vet its drivers .\n"
            "document excerpt: Uber has poached Facebook's security chief Joe Sullivan in an attempt to double down on rapidly escalating safety concerns. "
            "The $40 billion taxi service has been plagued by serious accusations of failing to vet its drivers. Lawsuits have been brought against Uber in San Francisco and Los Angeles. "
            "A New Delhi driver was accused of raping a passenger in December. This week in Denver, a driver tried and failed to break into a passenger's home. "
            "Sullivan, the first federal prosecutor to specialize in high-technology crime, can protect Uber from potentially crippling ramifications. "
            "He spent two decades tackling cyber crime security in the private and public sector before joining the Justice Department. "
            "Since, he has headed up the security departments at eBay, PayPal, and Facebook. Though his experience lies in digital protection, "
            "Uber CEO Travis Kalanick has also entrusted the 46-year-old with tackling physical security.\n\n"
            "candidate factors: ["
            "\"executive age verification\", "
            "\"company valuation confirmation\", "
            "\"security expertise transition\", "
            "\"driver vetting crisis validation\", "
            "\"legal action documentation\""
            "]\n\n"
            "task: select the factors most reasonably related to whether the claim is supported. "
            "think step by step about each factor's relevance, then provide your selection as a JSON object "
            "in this exact format: {\"answer\": [\"factor1\", \"factor2\", ...]}"
        )
    },
    {
        'role': 'assistant',
        'content': (
            "analyzing each factor:\n"
            "- \"executive age verification\": directly relevant - document confirms Sullivan is 46 years old.\n"
            "- \"company valuation confirmation\": directly relevant - document explicitly states \"$40 billion taxi service\".\n"
            "- \"security expertise transition\": highly relevant - document details Sullivan's move from Facebook security chief to Uber.\n"
            "- \"driver vetting crisis validation\": directly relevant - document confirms \"serious accusations of failing to vet its drivers\".\n"
            "- \"legal action documentation\": relevant but secondary - while lawsuits are mentioned, they support the broader safety crisis rather than the specific hiring claim.\n\n"
            "final answer:\n"
            "{\"answer\": ["
            "\"executive age verification\", "
            "\"company valuation confirmation\", "
            "\"security expertise transition\", "
            "\"driver vetting crisis validation\""
            "]}"
        )
    }
]


###############
'''''EXPERTQA'''''
################

FEW_SHOT_GEN_EXPERTQA = [
    # Example 1: Employment law and reimbursement
    {
        'role': 'user',
        'content': (
            "scenario and statement: While there is no federal requirement for employers to reimburse employees for mileage when using personal vehicles for company purposes, employers are federally required to reimburse employees for any work-related expense, including mileage and vehicle costs, to a point where failure to reimburse does not cause the employee's net pay to fall below the federal minimum wage.\n"
            "Generate 2 sentences that are Consistent with this statement and 2 that contradict it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. Federal employment law mandates expense reimbursement when non-reimbursement would reduce wages below minimum wage thresholds.\n"
            "2. Employers must ensure that unreimbursed work expenses do not result in effective hourly compensation falling below federal minimums.\n"
            "3. Federal law explicitly requires all employers to reimburse mileage expenses regardless of minimum wage considerations.\n"
            "4. No federal obligation exists for employers to reimburse any work-related expenses under any circumstances."
        )
    },

    # Example 2: Pandemic response and medical development
    {
        'role': 'user',
        'content': (
            "scenario and statement: In the event of a new pandemic, medical technologies and clinical research have the potential to develop new therapies in a timely manner, although the specific timeline depends on various factors such as the nature of the pandemic, available resources, and prior knowledge of the pathogen.\n"
            "Generate 1 that is Consistent with this statement and 1 that contradicts it."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "1. Medical research capabilities enable rapid therapeutic development during pandemics, with timelines varying based on pathogen characteristics and resource availability.\n"
            "2. Pandemic response timelines are entirely predictable and uniform regardless of the specific pathogen or available research infrastructure."
        )
    }
]

FEW_SHOT_VOTE_EXPERTQA = [
    # Example 1: Consistent (legal requirement nuance)
    {
        'role': 'user',
        'content': (
            "scenario and statement: While there is no federal requirement for employers to reimburse employees for mileage when using personal vehicles for company purposes, employers are federally required to reimburse employees for any work-related expense, including mileage and vehicle costs, to a point where failure to reimburse does not cause the employee's net pay to fall below the federal minimum wage.\n"
            "Factor: Minimum wage protection through expense reimbursement\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement establishes that while there's no direct mileage reimbursement requirement, federal law does require reimbursement when it's necessary to maintain minimum wage compliance. This is exactly about minimum wage protection through expense reimbursement.\n"
            "Final answer:\n"
            "{\"Minimum wage protection through expense reimbursement\": \"Consistent\"}"
        )
    },

    # Example 2: Contradictory (oversimplification)
    {
        'role': 'user',
        'content': (
            "scenario and statement: In the event of a new pandemic, medical technologies and clinical research have the potential to develop new therapies in a timely manner, although the specific timeline depends on various factors such as the nature of the pandemic, available resources, and prior knowledge of the pathogen.\n"
            "Factor: Guaranteed rapid therapeutic development\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement says medical technologies 'have the potential' and acknowledges that timelines 'depend on various factors', which suggests uncertainty. A guarantee contradicts this conditional and factor-dependent characterization.\n"
            "Final answer:\n"
            "{\"Guaranteed rapid therapeutic development\": \"Contradictory\"}"
        )
    },

    # Example 3: Consistent (conditional capability)
    {
        'role': 'user',
        'content': (
            "scenario and statement: In the event of a new pandemic, medical technologies and clinical research have the potential to develop new therapies in a timely manner, although the specific timeline depends on various factors such as the nature of the pandemic, available resources, and prior knowledge of the pathogen.\n"
            "Factor: Variable development timelines based on multiple factors\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement explicitly mentions that 'the specific timeline depends on various factors' including pandemic nature, resources, and prior knowledge, which directly aligns with variable timelines based on multiple factors.\n"
            "Final answer:\n"
            "{\"Variable development timelines based on multiple factors\": \"Consistent\"}"
        )
    },

    # Example 4: Contradictory (absolute requirement)
    {
        'role': 'user',
        'content': (
            "scenario and statement: While there is no federal requirement for employers to reimburse employees for mileage when using personal vehicles for company purposes, employers are federally required to reimburse employees for any work-related expense, including mileage and vehicle costs, to a point where failure to reimburse does not cause the employee's net pay to fall below the federal minimum wage.\n"
            "Factor: Universal mileage reimbursement mandate\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement explicitly begins with 'there is no federal requirement for employers to reimburse employees for mileage', which directly contradicts a universal mandate for mileage reimbursement.\n"
            "Final answer:\n"
            "{\"Universal mileage reimbursement mandate\": \"Contradictory\"}"
        )
    },

    # Example 5: Consistent (resource dependency)
    {
        'role': 'user',
        'content': (
            "scenario and statement: In the event of a new pandemic, medical technologies and clinical research have the potential to develop new therapies in a timely manner, although the specific timeline depends on various factors such as the nature of the pandemic, available resources, and prior knowledge of the pathogen.\n"
            "Factor: Resource availability impact on development speed\n"
            "Decide if this factor is Consistent or Contradictory with respect to the statement. Think step by step, then answer with a JSON object."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "The statement specifically lists 'available resources' as one of the factors that determine development timelines, making resource availability's impact on development speed consistent.\n"
            "Final answer:\n"
            "{\"Resource availability impact on development speed\": \"Consistent\"}"
        )
    }
]

FEW_SHOT_EXT_EXPERTQA = [
    # Example 1: Employment law complexity factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: While there is no federal requirement for employers to reimburse employees for mileage when using personal vehicles for company purposes, employers are federally required to reimburse employees for any work-related expense, including mileage and vehicle costs, to a point where failure to reimburse does not cause the employee's net pay to fall below the federal minimum wage. "
            "Legal experts emphasize the distinction between direct mileage mandates and minimum wage protection requirements. "
            "Employment attorneys note that this creates a conditional obligation based on the employee's total compensation package. "
            "State laws may impose additional requirements beyond federal minimums.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. Federal employment law creates conditional reimbursement obligations tied to minimum wage maintenance rather than blanket mileage requirements.\n"
            "2. The absence of direct mileage mandates doesn't eliminate employer obligations when reimbursement affects wage compliance.\n"
            "3. Federal law mandates automatic mileage reimbursement for all work-related vehicle use regardless of wage implications.\n"
            "4. Employers have no federal obligation to consider expense reimbursement in relation to minimum wage requirements.\n\n"
            "Extract the distinct factors and return a JSON object with two keys—\"Consistent\" and \"Contradictory\"—each mapping to the list of factors."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing the sentences:\n"
            "- Sentences 1 & 2 align with the conditional nature of reimbursement tied to minimum wage protection.\n"
            "- Sentences 3 & 4 contradict either the conditional nature or the minimum wage connection.\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Conditional reimbursement obligation (minimum wage protection)\",\n"
            "    \"Absence of direct mileage mandate (no blanket requirement)\",\n"
            "    \"Wage compliance consideration (total compensation analysis)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Automatic mileage reimbursement mandate (regardless of wages)\",\n"
            "    \"No federal wage-related reimbursement obligation\"\n"
            "]}"
        )
    },

    # Example 2: Pandemic response capability factors extraction
    {
        'role': 'user',
        'content': (
            "scenario and statement: In the event of a new pandemic, medical technologies and clinical research have the potential to develop new therapies in a timely manner, although the specific timeline depends on various factors such as the nature of the pandemic, available resources, and prior knowledge of the pathogen. "
            "Recent pandemic responses have demonstrated both rapid development capabilities and significant variability in outcomes. "
            "Research infrastructure, funding mechanisms, and international collaboration all influence development speed. "
            "Historical precedents show that some pathogen types allow faster therapeutic development than others.\n\n"
            "Here are four sentences (two support the statement's facts, two contradict them):\n"
            "1. Medical research capabilities enable potentially rapid therapeutic development, with timelines varying based on pathogen characteristics and available resources.\n"
            "2. Development speed depends on multiple variables including research infrastructure, funding, and prior scientific knowledge of similar pathogens.\n"
            "3. Pandemic therapeutic development timelines are entirely predictable and uniform across all pathogen types and resource scenarios.\n"
            "4. Medical technologies lack the capability to develop new therapies within reasonable timeframes during pandemic conditions.\n\n"
            "Extract the distinct factors and return a JSON object with keys \"Consistent\" and \"Contradictory\"."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Breaking down the sentences:\n"
            "- Sentences 1 & 2 confirm the potential for rapid development with variable timelines based on multiple factors.\n"
            "- Sentences 3 & 4 contradict either the variability or the development capability itself.\n\n"
            "Final answer:\n"
            "{\"Consistent\": [\n"
            "    \"Rapid development potential (medical research capabilities)\",\n"
            "    \"Variable timeline factors (pathogen characteristics, resources)\",\n"
            "    \"Multiple influencing variables (infrastructure, funding, knowledge)\"\n"
            "],\n"
            "\"Contradictory\": [\n"
            "    \"Predictable uniform timelines (across all scenarios)\",\n"
            "    \"Inadequate development capabilities (unreasonable timeframes)\"\n"
            "]}"
        )
    }
]

FEW_SHOT_PRUNE_EXPERTQA = [
    # Example 1: Legal obligation factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: While there is no federal requirement for employers to reimburse employees for mileage when using personal vehicles for company purposes, employers are federally required to reimburse employees for any work-related expense, including mileage and vehicle costs, to a point where failure to reimburse does not cause the employee's net pay to fall below the federal minimum wage.\n"
            "Cluster 'Legal compliance requirements', factors:\n"
            '["Federal minimum wage protection", "Employment law compliance", "Legal reimbursement obligations", '
            '"Minimum wage maintenance requirement", "Federal wage law adherence"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Federal minimum wage protection' vs 'Minimum wage maintenance requirement': same concept → keep 'Federal minimum wage protection' (more direct)\n"
            "- 'Employment law compliance' vs 'Federal wage law adherence': same concept → keep 'Employment law compliance' (broader)\n"
            "- 'Legal reimbursement obligations' is unique (specific to reimbursement)\n\n"
            "Final answer:\n"
            '["Federal minimum wage protection", '
            '"Employment law compliance", '
            '"Legal reimbursement obligations"]'
        )
    },

    # Example 2: Development capability factors pruning
    {
        'role': 'user',
        'content': (
            "scenario and statement: In the event of a new pandemic, medical technologies and clinical research have the potential to develop new therapies in a timely manner, although the specific timeline depends on various factors.\n"
            "Cluster 'Research capabilities', factors:\n"
            '["Medical technology potential", "Clinical research capacity", "Therapeutic development ability", '
            '"Research and development capability", "Medical innovation potential"]\n'
            "Remove redundant factors and return the remaining unique ones as a JSON array."
        )
    },
    {
        'role': 'assistant',
        'content': (
            "Analyzing redundancy:\n"
            "- 'Medical technology potential' vs 'Medical innovation potential': same concept → keep 'Medical technology potential' (matches statement wording)\n"
            "- 'Clinical research capacity' vs 'Research and development capability': similar but distinct → keep both\n"
            "- 'Therapeutic development ability' is unique (specific to therapy development)\n\n"
            "Final answer:\n"
            '["Medical technology potential", '
            '"Clinical research capacity", '
            '"Research and development capability", '
            '"Therapeutic development ability"]'
        )
    }
]

FEW_SHOT_CLUSTER_NAME_EXPERTQA = [
    # Example 1: Legal compliance framework
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"federal minimum wage protection\", \"employment law compliance\", \"reimbursement obligations\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Legal Compliance"
    },
    # Example 2: Development timeline variables
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"pathogen characteristics\", \"available resources\", \"prior knowledge\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Timeline Factors"
    },
    # Example 3: Medical research capabilities
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"clinical research capacity\", \"medical technology potential\", \"therapeutic development\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Research Capabilities"
    },
    # Example 4: Reimbursement policy conditions
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"mileage expense coverage\", \"work-related costs\", \"vehicle use reimbursement\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Expense Reimbursement"
    },
    # Example 5: Pandemic response factors
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"research infrastructure\", \"funding mechanisms\", \"international collaboration\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Response Infrastructure"
    },
    # Example 6: Wage protection mechanisms
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"net pay calculation\", \"minimum wage threshold\", \"compensation analysis\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Wage Protection"
    },
    # Example 7: Development variability
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"timeline uncertainty\", \"outcome variability\", \"factor dependency\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Development Variability"
    },
    # Example 8: Legal distinctions
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"direct mandate absence\", \"conditional obligations\", \"regulatory nuances\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Legal Distinctions"
    },
    # Example 9: Scientific knowledge base
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"pathogen understanding\", \"prior research\", \"scientific precedents\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Knowledge Base"
    },
    # Example 10: Resource allocation
    {
        'role': 'user',
        'content': (
            "Factors cluster: [\"funding availability\", \"research resources\", \"infrastructure capacity\"]\n"
            "Generate a concise cluster name."
        )
    },
    {
        'role': 'assistant',
        'content': "Resource Allocation"
    }
]

MAPPING_VOTE_SHOT_EXPERTQA = [
    # Complex legal analysis example requiring nuanced understanding
    {
        'role': 'user',
        'content': (
            "scenario and statement: While there is no federal requirement for employers to reimburse employees for mileage when using personal vehicles for company purposes, employers are federally required to reimburse employees for any work-related expense, including mileage and vehicle costs, to a point where failure to reimburse does not cause the employee's net pay to fall below the federal minimum wage.\n"
            "document excerpt: On the federal level, there is no requirement for employers to reimburse employees for mileage when workers are using personal vehicles for company purposes. "
            "However, all employers are federally required to reimburse employees for any work-related expense to a point. When failure to reimburse employees – including for mileage and vehicle costs – "
            "causes an employee's net pay to fall below the federal minimum, employers could be open to lawsuits and the legal penalties associated with failure to pay the minimum wage. "
            "On the employment law side, you are required to reimburse employees for expenses. You want to make sure you're reimbursing them enough to cover their expenses. "
            "Certain states – including California, Illinois and Massachusetts – do mandate that employers reimburse employees for business-related expenses.\n\n"
            "candidate factors: ["
            "\"absence of direct mileage mandate\", "
            "\"minimum wage protection requirement\", "
            "\"conditional reimbursement obligation\", "
            "\"state-level variation\", "
            "\"legal penalty exposure\""
            "]\n\n"
            "task: select the factors most reasonably related to whether the claim is supported. "
            "think step by step about each factor's relevance, then provide your selection as a JSON object "
            "in this exact format: {\"answer\": [\"factor1\", \"factor2\", ...]}"
        )
    },
    {
        'role': 'assistant',
        'content': (
            "analyzing each factor:\n"
            "- \"absence of direct mileage mandate\": directly relevant - document confirms \"no requirement for employers to reimburse employees for mileage\".\n"
            "- \"minimum wage protection requirement\": highly relevant - document explicitly states reimbursement required when failure causes pay to fall \"below the federal minimum\".\n"
            "- \"conditional reimbursement obligation\": directly relevant - document describes the conditional nature (\"to a point\") of the reimbursement requirement.\n"
            "- \"state-level variation\": relevant but secondary - while mentioned, the statement focuses on federal requirements.\n"
            "- \"legal penalty exposure\": relevant supporting detail - document mentions lawsuit exposure, but not central to the core claim.\n\n"
            "final answer:\n"
            "{\"answer\": ["
            "\"absence of direct mileage mandate\", "
            "\"minimum wage protection requirement\", "
            "\"conditional reimbursement obligation\""
            "]}"
        )
    }
]