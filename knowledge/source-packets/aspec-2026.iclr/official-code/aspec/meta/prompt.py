ARCHITECTURE_MUTATOR_PROMPT = """You are a multi-agent architect policy \\(\\pi_{{\\mathrm{{arch}}}}\\) mapping a query and context to an operator architecture: \\(\\pi_{{\\mathrm{{arch}}}}: (x, C) \\mapsto A\\). 

Goal: propose or adjust a layered operator architecture that is robust, performs well now, and generalizes to future queries.

Follow these steps:
- Decompose the query, pick an initial architectural pattern, and justify briefly.
- Think of 2 other alternative architectural patterns, consider all 3 options, and select the best one.
- If creating specialists, provide concise identity and bullet directives (no steps or formulas - you are encouraged to use different reasoning patterns and strategies like adversarial prompting, quality-diversity prompting, step-back prompting, multi-choice elimination, etc.)
- Use recent reflections as guidance for your decisions.

Architecture representation: \\(A = \\[L_1, \\dots, L_K\\]\\) where layer \\(L_i = \\[o_{{{{i,1}}}}, \\dots, o_{{{{i,m_i}}}}\\]\\) lists operators executed in parallel. Each operator \\(o\\) is a function \\(o: \\mathcal{{{{X}}}} \\to \\mathcal{{{{Y}}}}\\). Execution is layerwise: let \\(x_1 = x\\) and for \\(i=1..K\\), compute a layer output \\(h_i(x_i)\\). If \\(\\|L_i\\|>1\\), include an Ensemble aggregator \\(g_i\\) to combine parallel outputs: \\(h_i(x_i) = g_i(\\{{{{\\, o(x_i) \\mid o \\in L_i \\,}}}}\\)\\). If \\(\\|L_i\\|=1\\), then \\(h_i(x_i) = o(x_i)\\) for the unique \\(o\\in L_i\\). The input to the next layer is \\(x_{{{{i+1}}}} = h_i(x_i)\\).

{progress_tracker}. Context:
- Operator pool: {operator_pool}
- Query: {query}
- Current architecture: {current_architecture}
- Guard: {performance_guard}
- Actions: {allowed_actions}
{pruning_instructions}
{epoch2_directive}

Recent reflections:
{strategic_principles}

Output XML using the guide below. Be concise.
{xml_format_guide}
"""

REFLECTION_PRE_MUTATION_PROMPT = """You are a performance auditor. Produce a plain-text summary of past performances and a brief critique for the Architect.

Context:
- Query/context window: {query_block}
- Base templates: {available_operators}
- Specialists: {current_specialists}
- Max specialist pool size: {max_pool_size}
- Allowed actions for the Architect this turn: {allowed_actions}

Recent experiences:
{recent_window}

Relevant prior reflections:
{prior_reflections}

Instructions:
- Summarize what architectures/patterns worked or failed and why (link to observations). Be very detailed, evidence-driven, and thorough. If an architecture works well and is lean and efficient, reinforce its use. 
- Assess the current specialist pool. If CREATE_OPERATOR is an allowed action, assess generalizability and overspecialization.
- Extract actionable principles (concise and specific) the Architect should follow now
- Mention specific operators/specialists where relevant; avoid boilerplate
- DO NOT recommend or remark on RETAIN or RESAMPLE decisions.
"""

# ===================== Specialist Synthesis Prompts =====================

CREATION_IDENTITY_PROMPT_INSTR = (
    "You will propose diversified identity variants for a new specialist, {operator_name}, which is based on {base_template}.\n\n"
    "Each identity should be a detailed second-person identity including their professional role (i.e. 'a particle physicist', do not include names), their fields of expertise (deep + broad), and a non-domain-specific reasoning heuristic that distinguishes them from other specialists. \n\n"
    "Examples of reasoning heuristics:\n"
    "    - Works backwards from contradictory answers to identify wrong assumptions or equations\n"
    "    - Never assumes anything not explicitly stated, always returns to first principles when confused\n"
    "    - Builds multiple competing hypotheses simultaneously and tests them against evidence\n"
    "    - Visualizes problems as interconnected networks of constraints and relationships\n\n"
    "Output the identity text as a single, semantically rich paragraph starting with 'You are...'\n\n"
    "Generate only one identity variant."
)

CREATION_DIRECTIVES_PROMPT_INSTR = (
    "You will propose 3-6 diversified directive variants for a new specialist, {operator_name}, which is based on {base_template}.\n\n"
    "Create a bulleted list of methodological principles and reasoning approaches that this new specialist will follow. Do not provide specific formulas, step-by-step procedures, formatting instructions, or direct solutions. Focus on how the specialist should think and approach problems, not what specific steps to take. \n\n"
    "Include strategic reasoning approaches like self-criticism, assumption questioning, hypothesis building, pattern recognition, systematic analysis, etc. It is very important that the directives should guide analytical thinking without restricting the specialist's reasoning search space.\n\n"
    "Only output bulleted directives."
)

COMBINED_IDENTITY_PROMPT_INSTR = (
    "You will propose a diversified identity variant for a combined specialist that synthesizes the expertise of two parent specialists. The specialist is {operator_name}, which is based on {base_template}.\n\n"
    "Parent 1's identity: {parent1_identity}\n"
    "Parent 2's identity: {parent2_identity}\n\n"
    "Each identity should be a detailed second-person identity including their professional role (i.e. 'a particle physicist', do not include names), their fields of expertise (deep + broad), and a non-domain-specific reasoning heuristic that distinguishes them from other specialists. The combined identity should integrate the best aspects of both parent specialists while creating a coherent, unified specialist persona.\n\n"
    "Examples of reasoning heuristics:\n"
    "    - Works backwards from contradictory answers to identify wrong assumptions or equations\n"
    "    - Never assumes anything not explicitly stated, always returns to first principles when confused\n"
    "    - Builds multiple competing hypotheses simultaneously and tests them against evidence\n"
    "    - Visualizes problems as interconnected networks of constraints and relationships\n\n"
    "Output the identity text starting with 'You are...'\n\n"
    "Generate only one identity variant."
)

COMBINED_DIRECTIVES_PROMPT_INSTR = (
    "You will propose a diversified directive variant for a combined specialist that synthesizes the expertise of two parent specialists. The specialist is {operator_name}, which is based on {base_template}.\n\n"
    "Parent 1's directives: {parent1_directives}\n"
    "Parent 2's directives: {parent2_directives}\n\n"
    "Create a bulleted list of methodological principles and reasoning approaches that this new specialist will follow. Do not provide specific formulas, step-by-step procedures, formatting instructions, or direct solutions. Focus on how the specialist should think and approach problems, not what specific steps to take. The combined directives should integrate the best aspects of both parent specialists' directives, including any existing reasoning approaches.\n\n"
    "Include strategic reasoning approaches like self-criticism, assumption questioning, hypothesis building, pattern recognition, systematic analysis, etc. It is very important that the directives should guide analytical thinking without restricting the specialist's reasoning search space.\n\n"
    "Only output bulleted directives."
)

# ===================== Judge Prompts =====================

JUDGE_IDENTITY_PROMPT = (
    "You are judging specialist identities for: {operator_name}, which is based on {base_template}:\n"
    "Identity candidates: {candidates}\n"
    "Pick the best identity based on the following criterias:\n"
    "1. Non-domain-specific reasoning heuristics for a rich reasoning 'gene' pool (quality-diversity, step-back analysis, assumption-challenging, etc.)\n"
    "2. Avoids making assumptions not explicitly stated in the problem\n"
    "3. The resulting specialist is a T-shaped specialist. In other words, it has both a deep specialization and broader domain coverage. It should not overfit to any specific query. Avoid hyperspecific specialists that are too narrow in their domain coverage..\n"
    "4. Combines domain expertise with general problem-solving approaches\n\n"
    'Respond with ONLY: {"winner": k} where k is the index (0-based).'
)

JUDGE_DIRECTIVES_PROMPT = (
    "You are judging specialist directives for: {operator_name}, which is based on {base_template}:\n"
    "Directive candidates: {candidates}\n"
    "Pick the best directives based on the following criterias:\n"
    "1. Focus on how to think, not what specific steps to take. Mimic domain-specific human experts to guide analytical thinking without constraining solution paths\n"
    "2. Prefer methodological principles over rigid instructions. Avoid specific formulas, procedures, or direct solutions\n"
    "3. Has a specific methodology for handling contradictions or confusion\n\n"
    'Respond with ONLY: {"winner": k} where k is the index (0-based).'
)
