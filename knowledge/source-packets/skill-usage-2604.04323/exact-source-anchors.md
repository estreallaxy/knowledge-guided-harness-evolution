# Exact source anchors

# Papers

|Content to check|Exact Location|Scope of original support|
| --- | --- | --- |
|Gap between real-life skills retrieval, loading and implementation| §3.3,PDF pp.5–7,Table 1 |Compared, retrieved with no-skill settings; failure to produce any external knowledge increases ant.|
| Query-agnostic refinement | §4.1,PDF p.7 |Each retrieved skill is independently rewrited without knowing the target mission; it cannot cross the skill mix.|
| Query-specific refinement | §4.1,PDF pp.7–8 |Read tasks and all searchable skills, first exploring and self-assessment, then extracting, deleting or combining skills.|
|Overall results of Refinement| §4.2,PDF pp.8–9,Table 2 |Report SkillsBench and Pass/load on Terminal-Bench 2.0; there are conditions of decline or weakness.|
|Multi-skilled synthesis cases| §4.2,PDF p.9,Figure 3 |The display of two incomplete skills in the tensor-parallel mission combined with one mission condition.|
|Dependence on initial search quality| §4.2,PDF p.9,Table 3 |Refinement is closer to scaling up existing knowledge and does not allow for the stable creation of knowledge when it is completely missing.|
|Details of experiments and tips| Appendix B–C,PDF pp.13–17 |Recurring experimental conditions such as models, skills loading, retrieval and refining tips.|

# Official code

|Mechanism or evidence|File & Line Number|Role|
| --- | --- | --- |
|Query-specific reminder| `official-code/scripts/query_specific_refinement.py:53-128` |Clear access to mission and candidate skills, practical exploration, self-assessment and generation of refined reports.|
|Load tasks, candidate skills and skill-creator into quarantine tasks| `official-code/scripts/query_specific_refinement.py:175-254` |Constructs a Harbor temporary task and replaces the original test with a search environment with no real value verifier.|
|Harbor Configuration for Refinement| `official-code/scripts/query_specific_refinement.py:256-321` |Fixed anent, model, hair, artifacts and data paths.|
|Collected| `official-code/scripts/query_specific_refinement.py:323-401` |Writes the running product back to the task directory and distinguishes between access, missing and keep-original.|
|Mission condition skills search| `official-code/scripts/retrieve_skills.py:34-242` |Constructs the task environment, loads different searches, Skills, and saves found skill IDs.|
|Hybrid, keyword, semantic search portal| `official-code/data/find-skills*/SKILL.md` |Gives three search interfaces and calls protocols.|
|Retrieving and evaluation| `official-code/scripts/select_top_k_skills.py`,`eval_retrieval.py`,`check_skill_usage.py`,`calculate_results.py` |Process candidate selection, search evaluation, track-use inspection and summary of results, respectively.|
|Retrieving services| `official-code/search_server/` |Includes BM25, security, hybrid services and index construction codes.|

Line number is based on the`source-packet.json`fixed official code review.
