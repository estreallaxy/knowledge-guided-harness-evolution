# ResiliBench Supplementary (Tasks & Tools)

## Real API

### Real API Selection Criteria
The real APIs integrated into this benchmark were carefully selected from the [public-apis repository](https://github.com/public-apis/public-apis) based on the following criteria:

- **Reliability**: APIs with high uptime and stable service
- **Accessibility**: Free or freemium APIs that don't require complex authentication
- **Diversity**: Coverage of different domains and functionality types
- **Documentation**: Well-documented APIs with clear parameter specifications
- **Rate Limits**: Reasonable rate limits suitable for benchmark evaluation

### Real API Integration
We expand the benchmark by incorporating real-world APIs alongside the existing simulated tools:

- **Real API Tasks**: Tasks that interact with actual public APIs to test agents' capabilities in real-world scenarios. The tasks are given in `task_library_realAPI.json`
- **Real API Tools**: Integrated a curated selection of public APIs from the [public-apis repository](https://github.com/public-apis/public-apis). The tools are given in `tool_registry_realAPI.json`.

The real APIs were carefully selected to provide diverse functionality while maintaining reliability and accessibility for benchmark evaluation.

## Version Changes

This version introduces several key improvements compared to the previous version:

### Task Category Renaming
The task categories have been renamed for better clarity and semantic meaning:
1. `single_tool_task` → `content_analysis`
2. `two_step_task` → `batch_processing`  
3. `multi_step_processing` → `data_multistep_processing`
4. `network_integration` → `api_data_retrieval`
5. `complex_workflow` → `advanced_processing`

These new names better reflect the actual functionality and purpose of each task category, making the benchmark more intuitive for researchers and practitioners.

## Quick Filename Mapping
- Tools → `tool_registry.json` (Paper "Tool Registry").
- Tasks (with four reference workflows) → `simulated_tasks_enhanced/task_library_enhanced_v3_{difficulty}_with_workflows.json` (Paper "Reference Workflows", "Workflow Prompt Generation", "MDP-BASED OPTIMAL WORKFLOW GENERATION").
- `biased` variants → supplemental analysis dataset versions (for robustness/sampling comparisons).epository contains the supplementary materials submitted with the paper:
- Tasks (task specifications and reference workflows): a set of JSON files under the `tasks/` directory.
- Tools (tool registry / probabilistic tool behavior): the `tool_registry.json` at the repository root.

The sections below explain how these files map to the paper and provide a unified naming scheme for easier review and reproduction.



## Relation to the Paper
- Tool Registry (Tools) → Paper “Benchmark Setup” → “Tool Registry”, consistent with “Benchmark Construction > Tool Library Generation”. Error models and dependencies are detailed in the paper and appendices.
- Tasks and Reference Workflows (Tasks + Workflows) → Paper “Benchmark Setup > Benchmark Data Organization” → “Task Specifications” and “Reference Workflows”. The four prompt variants correspond to “Workflow Prompt Generation” and “MDP-Based Optimal Workflow Generation”.

## Files and Contents
- `tool_registry.json`
  - Tool registry of APIs, including parameter templates, return schemas, and probabilistic error models (INVALID_INPUT, OPERATION_FAILED, TIMEOUT, CALCULATION_ERROR, OVERFLOW).
  - Corresponds to the “Tool Registry” implementation in the paper.

- `tasks/*.json`
  - Task sets, organized by difficulty and whether reference workflows are included:
    - Files with the suffix `_with_workflows.json`: extend task specifications with four prompt variants (Baseline / Chain-of-Thought / Optimal Workflow / Flawed Workflow).
    - Files without that suffix: contain only Task Specifications.
    - File names that include `biased`: indicate a biased sampling/configuration variant for supplemental analysis (does not affect the main definitions in the paper).

## Quick Filename Mapping
- Tools → `tool_registry.json` (Paper “Tool Registry”).
- Tasks (without workflows) → `tasks/task_specs_v3_{difficulty}.json` (Paper “Task Specifications”).
- Tasks (with four reference workflows) → `tasks/task_specs_v3_{difficulty}_with_workflows.json` (Paper “Reference Workflows”, “Workflow Prompt Generation”, “MDP-BASED OPTIMAL WORKFLOW GENERATION”).
- `biased` variants → supplemental analysis dataset versions (for robustness/sampling comparisons).



