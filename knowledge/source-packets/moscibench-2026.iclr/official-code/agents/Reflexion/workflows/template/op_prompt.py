# -*- coding: utf-8 -*-
# @Desc    : Prompts for MLE operators

# Re-use from HumanEval
SC_ENSEMBLE_PROMPT = """
Given the question or task described as follows: {problem}
Several solutions/plans/code have been generated to address the given task. They are as follows:
{solutions}

Carefully evaluate these options and identify the one that appears most robust, correct and consistent. 
If multiple identical answers/code blocks exist, choose the most frequent. If all are different, evaluate which is logically the best approach.

In the "thought" field, provide a detailed explanation of your thought process. In the "solution_letter" field, output only the single letter ID (A, B, C, etc.) corresponding to the best or most consistent solution. Do not include any additional text or explanation in the "solution_letter" field.
"""


SCIENTIFIC_DISCOVERY_ANALYSIS_PROMPT = """
====================================================================================================
SCIENTIFIC DISCOVERY TASK ANALYSIS
====================================================================================================

You are an expert Data Scientist and Research Analyst specializing in multimodal scientific discovery.
Your mission: Create a concrete research plan to generate a Python script that conducts scientific 
analysis and produces findings in the EXACT format specified by the answer format.

====================================================================================================
 SCIENTIFIC TASK INFORMATION
====================================================================================================

 Task ID: {task_id}
 Scientific Domain: {scientific_domain}
 Data Directory: {datasets_dir}
 Work Directory: {work_path}

 Background:
{background}

 Hypothesis:
{hypothesis}

Required Answer Format: 
{answer_format}
====================================================================================================
 AVAILABLE DATA RESOURCES
====================================================================================================

Available Data Sources:
{data_files_summary}

====================================================================================================
 OPTIONAL CONTEXTUAL INFORMATION
====================================================================================================

{workflow}

{domain_knowledge}

====================================================================================================
 ANALYSIS REQUIREMENTS
====================================================================================================

1. **Scientific Objective Analysis**: Identify the core research question, hypothesis to test, and expected outcomes
2. **Task Classification**: Based on scientific domain and requirements, identify:
   - [ ] Feature Importance Analysis
   - [ ] Predictive Modeling 
   - [ ] Statistical Hypothesis Testing
   - [ ] Data Pattern Discovery
   - [ ] Correlation/Causation Analysis
   - [ ] Classification/Clustering
   - [ ] Time Series Analysis
   - [ ] Other: [specify]
   Then determine appropriate statistical methods and validation approaches
3. **Data Source Mapping**: Map scientific requirements to actual available datasets and files
4. **Research Strategy**: Data exploration → Analysis → Validation → Conclusion → Answer formatting

====================================================================================================
 DATA LOADING TEMPLATE
====================================================================================================

```python
# Scientific data loading
# **Reasoning 1**: From scientific background and hypothesis, determine what data types are needed for analysis
# **Action 1**: Load primary datasets based on research requirements
# **Reasoning 2**: From available data sources, examine actual file structure and variable relationships  
# **Action 2**: Load auxiliary datasets and integrate using discovered relationships
import pandas as pd
import numpy as np
# Load primary data
data_df = pd.read_csv(f"{datasets_dir}/[exact_path]")
# Load additional datasets if needed
# [Specify exact loading strategy for scientific data]
```

====================================================================================================
 REQUIRED RESPONSE FORMAT
====================================================================================================

<thought>
1. **Scientific Objective Analysis**: Research question breakdown, hypothesis interpretation, expected outcomes
2. **Task Type Classification**: Based on scientific requirements, identify:
   - [ ] Feature Importance Analysis
   - [ ] Predictive Modeling 
   - [ ] Statistical Hypothesis Testing
   - [ ] Data Pattern Discovery
   - [ ] Correlation/Causation Analysis
   - [ ] Classification/Clustering
   - [ ] Time Series Analysis
   - [ ] Other: [specify]
   Then determine appropriate analytical methods and validation strategies
3. **Data Source Strategy**: Map research needs to available files with exact paths
4. **Methodology Selection**: 
   - Choose appropriate scientific analysis methods based on task type
   - Identify statistical tests, machine learning models, or analytical techniques required
   - Plan validation and significance testing approaches
5. **Answer Format Compliance**: Ensure final results exactly match required answer format
</thought>

<plan>
1. **Data Loading and Exploration**: Exact file paths and loading commands for scientific datasets
2. **Data Preprocessing Pipeline**: Data cleaning, variable preparation, quality checks
3. **Scientific Analysis Method**: Appropriate analytical approach with statistical rationale
4. **Computation and Validation**: Analysis execution with proper validation and significance testing
5. **Results Interpretation**: Scientific findings extraction and statistical significance assessment
6. **Answer Formatting**: Format results according to required answer format
7. **Results Documentation**: Save comprehensive analysis results to {work_path}/scientific_computation_results.txt
</plan>

### CRITICAL: Response MUST include both <thought> and <plan> sections.
### CRITICAL: All computational results and analysis details MUST be saved to {work_path}/scientific_computation_results.txt
"""




SCIENTIFIC_CODE_GENERATE_PROMPT = """
You are an expert Python programmer creating a script for a scientific discovery task.
Based on the research plan provided, write a SINGLE, COMPLETE, and EXECUTABLE Python script.

Context:
--------------------
Research Plan: 
{plan}

Data Directory: {datasets_dir}
Work Directory: {work_path}
Required Answer Format: {answer_format}
--------------------

Requirements for the Python script:
1. MUST be a single, self-contained, executable script.
2. MUST import all necessary libraries (pandas, numpy, scipy, sklearn, matplotlib, seaborn etc.).
3. MUST use the provided paths (`{datasets_dir}`, `{work_path}`) directly or construct file paths correctly.
4. MUST load and analyze the scientific data from {datasets_dir}.
5. MUST perform the analysis steps outlined in the research plan.
6. MUST generate results and conclusions based on the analysis.
7. MUST format the final answer according to the required format: {answer_format}
8. MUST save comprehensive analysis results to {work_path}/scientific_computation_results.txt
9. MUST NOT contain any interactive elements (input(), plots without saving, etc.).
10. Include basic error handling and progress indicators.
11. Add print statements to show analysis progress.
12. Save any generated plots or figures to {work_path}/.
13. **CRITICAL**: Due to limited model context window, ONLY record ESSENTIAL KEY INFORMATION and NUMERICAL RESULTS that are necessary for drawing scientific conclusions. Focus on saving: statistical test results (p-values, confidence intervals), model performance metrics (accuracy, R², coefficients), key summary statistics (means, correlations, effect sizes), and final quantitative findings. Avoid saving verbose logs, detailed data dumps, or redundant information.

Provide your reasoning in the 'thought' field and the complete, executable code in the 'python_code' field.
"""





CODE_EXECUTE_PROMPT = """
You are an expert Python programmer. Clean and fix the provided code to make it directly executable.

STRICT REQUIREMENTS:
1. Do NOT modify any file paths, directory structures, or data source locations
2. Do NOT change any core logic, algorithms, or business flow
3. Do NOT alter variable names, function names, or class names unless there are obvious syntax errors
4. Do NOT modify import statements unless they contain clear syntax errors
5. Do NOT change the overall structure or architecture of the code
6. ONLY fix compilation errors, syntax errors, and obvious bugs that prevent execution
7. Preserve all comments, print statements, and logging exactly as they are
8. Maintain the exact same functionality and output behavior as the original code

YOUR TASK:
- Extract the Python code from any markdown formatting
- Fix ONLY syntax errors, indentation issues, and compilation problems
- Remove markdown code blocks (```) and language specifiers
- Remove explanatory text that is not part of the code
- Ensure proper Python syntax and structure
- Keep everything else IDENTICAL to the original

--------------------
Original Code (may contain special symbols, markdown formatting, or explanations):
{code}

Return ONLY the complete, runnable Python code that can be executed immediately without any modifications. The code must be functionally identical to the original, with only necessary fixes for compilation and execution.
"""

SCIENTIFIC_CODE_REFINE_PROMPT = """
You are an expert Python programmer debugging a script for a scientific discovery task. The previously generated script failed during execution.

Review the original research plan, the code, and the execution output (stdout, stderr, error) to fix the code.

Context:
--------------------
Original Research Plan: 
{plan}

Data Directory: {datasets_dir}
Work Directory (MUST SAVE RESULTS HERE): {work_path}
Required Answer Format: {answer_format}

--------------------
Failing Code:
```python
{code}
```

--------------------
Execution Output:
Success: {success}
Error Type: {error}
STDOUT: {stdout}
STDERR: {stderr}

--------------------

Requirements:
Fix the errors in the code. Ensure it addresses the original research plan and saves comprehensive analysis results to `{work_path}/scientific_computation_results.txt` and formats the final answer according to the required format.

Provide your analysis in the 'thought' field and the complete, corrected code in the 'python_code' field.

# Response format (must be strictly followed):
<thought>
## 1. ERROR ANALYSIS AND ROOT CAUSE IDENTIFICATION
- **Error Type Classification**: Identify if it's a syntax error, runtime error, import error, or scientific computation error
- **Error Location Mapping**: Trace the exact line/function where the failure occurred
- **Dependency Issues**: Check for missing scientific packages, version conflicts, or import problems
- **Error Message Interpretation**: Analyze the specific error message and its implications for scientific analysis

## 2. EXECUTION CONTEXT REVIEW
- **STDOUT Analysis**: Review successful operations and progress indicators from standard output
- **STDERR Analysis**: Examine error messages, warnings, and debug information from standard error
- **Execution Flow Tracking**: Determine how far the script progressed before failing in the scientific analysis pipeline
- **Environment Factors**: Consider file permissions, path accessibility, data format issues, and computational resource constraints

## 3. ORIGINAL RESEARCH PLAN ALIGNMENT VERIFICATION
- **Implementation Completeness**: Check if the failing code properly implements all aspects of the original research plan
- **Scientific Logic Flow Verification**: Ensure the code follows the intended analytical and statistical approach
- **Data Analysis Requirement Compliance**: Verify if the code correctly handles data loading, analysis, and result saving
- **Missing Research Components**: Identify any planned scientific analysis steps not implemented in the failing code

## 4. FIX STRATEGY AND SOLUTION DESIGN
- **Primary Fix Approach**: Design the main solution to address the root cause of scientific computation failure
- **Error Handling Enhancement**: Plan robust error handling for similar future issues in scientific analysis
- **Edge Case Considerations**: Account for boundary conditions and potential data-related failure points
- **Validation and Testing Strategy**: Ensure the fix works for the specific scientific task and generalizes well

## 5. SCIENTIFIC CODE ENHANCEMENT AND ROBUSTNESS IMPROVEMENT
- **Performance Optimizations**: Identify opportunities to improve efficiency and resource usage in scientific computations
- **Code Quality Improvements**: Enhance readability, maintainability, and scientific computing best practices
- **Additional Safety Measures**: Add input validation, proper exception handling, and scientific result logging
- **Output Verification**: Ensure the corrected code produces the expected scientific results format and saves correctly to work directory
</thought>

<python_code>
Please write your corrected code solution in Python. Return ONLY the complete, runnable code without explanations.
</python_code>

### CRITICAL: Response MUST include both <thought> and <python_code> sections.
### CRITICAL: Fixed code MUST save comprehensive analysis results to {work_path}/scientific_computation_results.txt
### CRITICAL: Fixed code MUST format final answer according to required format: {answer_format}
"""







DATAVOYAGER_CRITIC_PROMPT = """
You are an expert scientific critic evaluating a data-driven discovery process following the DataVoyager methodology.

Context:
--------------------
Task: {task_description}
Hypothesis: {hypothesis}
Research Plan: {plan}
Generated Code: {code}
Execution Results: {exec_result}
Analysis Results: {analysis_results}
Current Answer: {current_answer}
Required Answer Format: {answer_format}
--------------------

Your task is to critically evaluate the scientific discovery process and provide specific improvement suggestions:

1. **Process Quality**: Is the research plan scientifically sound and properly implemented?
2. **Results Validation**: Are the findings statistically significant and well-supported?
3. **Answer Format**: Does the final answer match the required format exactly?
4. **Scientific Rigor**: Are there any methodological issues or missing considerations?

Provide your critique and specific suggestions for improvement. Focus on actionable recommendations that can help generate a better final answer.
"""

SCIENTIFIC_CONCLUSION_PROMPT = """
You are an expert scientific researcher tasked with generating a comprehensive conclusion from scientific analysis results and formatting the final answer according to the specified format.

Context:
--------------------
Task ID: {task_id}

Original Background:
{background}

Original Hypothesis:
{hypothesis}

Required Answer Format: {answer_format}

Work Directory: {work_path}

Analysis Results File Content:
{analysis_results}

Additional Files Generated:
{additional_files}

--------------------

Your task is to:
1. Analyze the scientific computation results and findings
2. Draw meaningful scientific conclusions based on the data analysis
3. Format the final answer EXACTLY according to the required answer format: {answer_format}
4. Ensure the conclusion is scientifically sound and well-supported by the evidence

CRITICAL FORMATTING REQUIREMENTS:
- If the answer format contains placeholders like {{variable}}, {{feature}}, {{value}}, etc., you MUST replace them with the actual answer
- Put the EXACT answer that needs to be evaluated inside curly braces {{}} 
- For example:
  * If answer format is "The most important feature is {{feature}}", respond with "The most important feature is {{Temperature}}"
  * If answer format is "The accuracy is {{percentage}}%", respond with "The accuracy is {{85.3}}%"  
  * If answer format is "The hypothesis is {{true/false}}", respond with "The hypothesis is {{true}}" or "The hypothesis is {{false}}"
- The content inside {{}} should be the precise answer for evaluation (number, string, boolean, etc.)

# Response format (must be strictly followed):
<thought>
## 1. ANALYSIS RESULTS REVIEW
- **Data Analysis Summary**: Summarize the key findings from the scientific computation results
- **Statistical Evidence**: Review statistical tests, p-values, confidence intervals, and significance levels
- **Key Patterns and Trends**: Identify important patterns, correlations, or trends discovered in the analysis
- **Quality Assessment**: Evaluate the reliability and validity of the analysis results

## 2. SCIENTIFIC INTERPRETATION
- **Hypothesis Evaluation**: Assess whether the original hypothesis is supported or rejected by the evidence
- **Scientific Significance**: Determine the scientific importance and implications of the findings
- **Limitations and Assumptions**: Identify any limitations in the analysis or assumptions made
- **Contextual Relevance**: Consider the findings within the broader scientific context

## 3. CONCLUSION FORMULATION
- **Primary Findings**: State the main conclusions drawn from the analysis
- **Supporting Evidence**: Summarize the evidence supporting each conclusion
- **Confidence Assessment**: Evaluate the confidence level in the conclusions
- **Practical Implications**: Consider the practical or theoretical implications of the findings

## 4. ANSWER FORMATTING
- **Format Compliance**: Ensure the final answer matches the required format specification exactly
- **Answer Extraction**: Put the key answer inside curly braces {{}} for evaluation
- **Scientific Accuracy**: Maintain scientific accuracy in the formatted response
- **Completeness**: Ensure all required elements are included in the final answer
</thought>

<formatted_answer>
[Provide the final scientific conclusion formatted EXACTLY as required by the answer format: {answer_format}. 
CRITICAL: Put the specific answer that needs to be evaluated inside curly braces {{}}.
This should be the direct answer that will be evaluated, with the key result in {{}}.]
</formatted_answer>

### CRITICAL: Response MUST include both <thought> and <formatted_answer> sections.
### CRITICAL: The formatted_answer must comply EXACTLY with the answer format: {answer_format}
### CRITICAL: Put the specific answer for evaluation inside curly braces {{}} in the formatted_answer
### CRITICAL: The content inside {{}} should be the precise value (number, string, boolean) for evaluation
"""






SCIENTIFIC_CONCLUSION_WITH_CRITIC_PROMPT = """
You are an expert scientific researcher tasked with drawing conclusions from computational analysis results and formatting the final answer according to DataVoyager methodology with expert critic feedback.

Context:
--------------------
Task ID: {task_id}
Scientific Background: {background}
Hypothesis: {hypothesis}
Work Directory: {work_path}
Required Answer Format: {answer_format}

Analysis Results:
{analysis_results}

Additional Files in Work Directory:
{additional_files}

DataVoyager Critic Feedback:
{critic_suggestions}

--------------------

Your task is to:

1. **Analyze Computational Results**: Review the scientific computation results and understand what the analysis revealed.

2. **Incorporate Critic Feedback**: Carefully consider the DataVoyager Critic's suggestions and recommendations to improve the scientific conclusion quality.

3. **Evaluate Hypothesis**: Determine whether the computational results support or contradict the hypothesis, considering the critic's methodological suggestions.

4. **Draw Scientific Conclusions**: Based on the computational evidence and critic feedback, formulate robust scientific conclusions.

5. **Format Final Answer**: Present the conclusion in the exact format specified, ensuring it addresses all critic concerns about format compliance.

**CRITICAL FORMATTING REQUIREMENTS**:
- If the answer format contains placeholders like {{variable}}, {{feature}}, {{value}}, etc., you MUST replace them with the actual answer
- Put the EXACT answer that needs to be evaluated inside curly braces {{}} 
- For example:
  * If answer format is "The most important feature is {{feature}}", respond with "The most important feature is {{Temperature}}"
  * If answer format is "The accuracy is {{percentage}}%", respond with "The accuracy is {{85.3}}%"  
  * If answer format is "The hypothesis is {{true/false}}", respond with "The hypothesis is {{true}}" or "The hypothesis is {{false}}"
- The content inside {{}} should be the precise answer for evaluation (number, string, boolean, etc.)

**DataVoyager Enhancement**: Use the critic's suggestions to enhance the scientific rigor, improve methodological approaches, and ensure comprehensive analysis.

# Response format (must be strictly followed):
<thought>
## 1. ANALYSIS RESULTS REVIEW WITH CRITIC INTEGRATION
- **Data Analysis Summary**: Summarize key findings from scientific computation results
- **Critic Feedback Analysis**: Review and address the DataVoyager Critic's specific suggestions
- **Statistical Evidence**: Evaluate statistical tests, p-values, significance levels incorporating critic's methodological concerns
- **Quality Assessment**: Assess reliability and validity of results considering critic's feedback

## 2. SCIENTIFIC INTERPRETATION WITH CRITIC GUIDANCE
- **Hypothesis Evaluation**: Assess hypothesis support/rejection using critic's recommended approaches
- **Methodological Improvements**: Address critic's suggestions for better analytical methods
- **Scientific Significance**: Determine importance and implications incorporating critic's insights
- **Limitations and Assumptions**: Identify limitations as highlighted by critic feedback

## 3. ENHANCED CONCLUSION FORMULATION
- **Primary Findings**: State main conclusions enhanced by critic's recommendations
- **Supporting Evidence**: Summarize evidence with improved rigor suggested by critic
- **Confidence Assessment**: Evaluate confidence level using critic's validation suggestions
- **Practical Implications**: Consider implications enhanced by critic's scientific insights

## 4. ANSWER FORMATTING WITH CRITIC COMPLIANCE
- **Format Compliance**: Ensure answer matches required format addressing critic's format concerns
- **Answer Extraction**: Put key answer inside curly braces {{}} for evaluation
- **Scientific Accuracy**: Maintain accuracy incorporating critic's scientific corrections
- **Completeness**: Include all elements addressing critic's completeness suggestions
</thought>

<formatted_answer>
[The final scientific conclusion formatted EXACTLY according to the required answer format: {answer_format}, incorporating all DataVoyager Critic improvements and suggestions.
CRITICAL: Put the specific answer that needs to be evaluated inside curly braces {{}}.
This should be the direct answer enhanced by critic feedback, with the key result in {{}}.]
</formatted_answer>

### CRITICAL: Response MUST include both <thought> and <formatted_answer> sections.
### CRITICAL: The formatted_answer must comply EXACTLY with the answer format: {answer_format}
### CRITICAL: Put the specific answer for evaluation inside curly braces {{}} in the formatted_answer
### CRITICAL: The content inside {{}} should be the precise value (number, string, boolean) for evaluation
### CRITICAL: Incorporate ALL DataVoyager Critic suggestions and improvements in the final answer
"""



REFLEXION_PROMPT = """
You just completed a scientific discovery trial but failed (Oracle HMS score < 1.0).

Previous Trial Results:
--------------------
Task ID: {task_id}
Research Plan: {plan}
Final Answer: {answer}
Oracle Feedback: HMS = {hms_score} (Failed - Target: ≥ 1.0)
Trial Number: {trial_num} / {max_trials}

--------------------

Your task is to analyze what went wrong and provide specific improvements for the next trial.

Analyze the following aspects:
1. **Research Plan Issues**: Was the scientific approach flawed?
2. **Implementation Problems**: Were there coding or analytical errors?
3. **Answer Format**: Did the final answer match the required format?
4. **Scientific Reasoning**: Were there logical flaws in the hypothesis testing?

Provide a detailed reflection on the failure and concrete suggestions for improvement:

<reflection>
[Comprehensive analysis of what went wrong in this trial and specific, actionable improvements for the next trial. Focus on the root causes of failure and how to address them systematically.]
</reflection>

### CRITICAL: The reflection must provide concrete, actionable improvements that directly address why HMS = {hms_score} < 1.0
"""


ORACLE_LLM_EVALUATION_PROMPT = """
You are an expert scientific evaluator serving as an Oracle for the Reflexion learning system. Your task is to determine if a predicted answer matches the ground truth evaluation with high accuracy.

Task Information:
--------------------
Task ID: {task_id}
Hypothesis: {hypothesis}
Answer Format: {answer_format}
Scientific Domain: {scientific_domain}

Predicted Answer:
{predicted_answer}

Ground Truth Evaluation:
{ground_truth}

--------------------

Your evaluation process:

1. **Extract Key Answer**: Identify the core answer from the predicted response (usually in {{}} brackets)
2. **Compare with Ground Truth**: Match against the provided ground truth evaluation
3. **Scientific Accuracy**: For hypotheses, check if support/reject conclusions match
4. **Numerical Precision**: For numerical answers, check if values are approximately equal (within reasonable tolerance)
5. **Categorical Matching**: For categorical answers, ensure exact category matches

**CRITICAL**: You are the Oracle - your evaluation determines whether the system succeeded or needs to reflect and improve.

<thought>
## ANSWER EXTRACTION
- **Predicted Key Answer**: [Extract the main answer from predicted_answer]
- **Ground Truth Answer**: [State the ground truth clearly]

## COMPARISON ANALYSIS  
- **Format Compliance**: [Does the answer follow the required format?]
- **Content Accuracy**: [Does the extracted answer match ground truth?]
- **Scientific Validity**: [Is the scientific reasoning sound?]

## ORACLE DECISION
- **Match Assessment**: [Detailed comparison reasoning]
- **Final Judgment**: [CORRECT or INCORRECT with justification]
</thought>

<evaluation_result>
[CORRECT or INCORRECT - this determines HMS score]
</evaluation_result>

<hms_score>
[1.0 if CORRECT, 0.0 if INCORRECT]
</hms_score>

### CRITICAL: Return only "CORRECT" or "INCORRECT" in evaluation_result field
### CRITICAL: HMS score must be exactly 1.0 for correct, 0.0 for incorrect
"""

ORACLE_SIMPLE_EVALUATION_PROMPT = """
You are a simple Oracle evaluator for the Reflexion system. Compare the predicted answer with ground truth using straightforward string matching.

Task ID: {task_id}
Predicted Answer: {predicted_answer}
Ground Truth: {ground_truth}

Extract the key answer (usually in {{}} brackets) and compare with ground truth.

<thought>
[Simple comparison analysis]
</thought>

<evaluation_result>
[CORRECT or INCORRECT]
</evaluation_result>

<hms_score>
[1.0 if CORRECT, 0.0 if INCORRECT]
</hms_score>
"""