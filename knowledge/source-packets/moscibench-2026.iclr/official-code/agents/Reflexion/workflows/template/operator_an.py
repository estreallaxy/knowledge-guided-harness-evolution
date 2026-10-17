# -*- coding: utf-8 -*-
# @Desc    : action nodes for MLE operator

from pydantic import BaseModel, Field


class GenerateOp(BaseModel):
    """General purpose text generation."""
    response: str = Field(default="", description="Generated text response.")


class AnalysisOp(BaseModel):
    """For analyzing the ML problem and creating a plan."""
    thought: str = Field(default="", description="Analysis of the data, task, and metric.")
    plan: str = Field(default="", description="Step-by-step plan: data loading, preprocessing, feature engineering, model selection, training, prediction, submission format.")

class CodeGenerateOp(BaseModel):
    """For generating executable Python code."""
    thought: str = Field(default="", description="Reasoning behind the code structure and choices.")
    python_code: str = Field(default="", description="The executable python code to solve the problem and generate the submission file.")

class CodeRefineOp(BaseModel):
    """For refining and fixing executable Python code based on execution errors."""
    thought: str = Field(default="", description="Analysis of the execution error and reasoning behind the code fixes and improvements.")
    python_code: str = Field(default="", description="The corrected and refined executable python code that addresses the execution errors.")

class CodeExecuteOp(BaseModel):
    """For cleaning and fixing provided code to make it directly executable."""
    thought: str = Field(default="", description="Analysis of the original code structure, identified issues, and reasoning behind the cleaning and fixing process.")
    python_code: str = Field(default="", description="The cleaned and corrected executable Python code with all formatting issues, special symbols, and non-code content removed.")

class ReflexionOp(BaseModel):
    """For generating reflections based on oracle feedback to improve scientific discovery process."""
    reflection: str = Field(default="", description="Detailed reflection on what went wrong and how to improve for the next trial.")


class OracleOp(BaseModel):
    """For evaluating predicted answers against ground truth using Oracle feedback."""
    thought: str = Field(default="", description="Analysis of the predicted answer against ground truth.")
    evaluation_result: str = Field(default="", description="CORRECT or INCORRECT based on comparison.")
    hms_score: float = Field(default=0.0, description="HMS score: 1.0 for correct, 0.0 for incorrect.")

class CriticOp(BaseModel):
    """For critiquing and evaluating scientific discovery results and providing improvement suggestions."""
    thought: str = Field(default="", description="Critical analysis of the discovery process and specific improvement suggestions.")
    suggestions: str = Field(default="", description="Specific actionable suggestions for improving the scientific conclusion and answer format.")

class ScientificConclusionOp(BaseModel):
    """For generating scientific conclusions and formatting the final answer."""
    thought: str = Field(default="", description="Comprehensive analysis of scientific results: reviewing findings, interpreting statistical evidence, evaluating hypothesis, formulating conclusions, and ensuring answer format compliance.")
    formatted_answer: str = Field(default="", description="The final scientific conclusion formatted exactly according to the required answer format specification for evaluation submission.")