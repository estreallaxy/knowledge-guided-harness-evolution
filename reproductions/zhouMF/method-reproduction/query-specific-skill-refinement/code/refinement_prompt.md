You are refining candidate Skills for one target task.

## Inputs

- Original task instruction: `/root/task_instruction.md`
- Candidate Skills: `/root/candidate_skills/`

Read every candidate `SKILL.md`. Read its supporting files only when they are relevant to this task.

## Work

1. Identify the task's required capabilities, constraints, and likely failure points.
2. Attempt the task once in the supplied environment while actively testing relevant candidate guidance.
3. Determine which guidance was useful, irrelevant, incorrect, or incomplete.
4. Produce the smallest coherent set of task-specific Skills that would help a fresh execution agent.

Preserve useful instructions, remove noise, correct demonstrated errors, and combine complementary material. Add knowledge discovered during exploration only when the environment provides concrete support for it. Do not present an unverified guess as a successful method.

## Boundaries

- Perform one exploration and one refinement pass.
- Do not ask for user input.
- Do not search for papers, repositories, or additional methods.
- Do not infer success from a hidden verifier; no real verifier is available.
- Do not place task solutions, secrets, benchmark answers, or test artifacts in a Skill.
- Make each Skill narrowly scoped; make its name and description useful for routing.
- Keep reusable instructions in `SKILL.md`, deterministic repeated operations in `scripts/`, and conditional details in `references/`.

## Output

Write the refined Skills under `{refined_skills_path}/`, one directory per Skill. Every directory must contain a non-empty `SKILL.md` with YAML frontmatter containing `name` and `description`. Include supporting code or references when they are necessary to use the Skill without further research.
