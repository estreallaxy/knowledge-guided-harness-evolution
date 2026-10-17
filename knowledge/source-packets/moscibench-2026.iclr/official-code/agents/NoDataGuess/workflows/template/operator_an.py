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

class ScientificConclusionOp(BaseModel):
    """For generating scientific conclusions and formatting the final answer."""
    thought: str = Field(default="", description="Comprehensive analysis of scientific results: reviewing findings, interpreting statistical evidence, evaluating hypothesis, formulating conclusions, and ensuring answer format compliance.")
    formatted_answer: str = Field(default="", description="The final scientific conclusion formatted exactly according to the required answer format specification for evaluation submission.")


class NoDataGuessOp(BaseModel):
    """For guessing scientific conclusions without accessing actual data."""
    thought: str = Field(default="", description="Analysis of the task and reasoning for the guess based on domain knowledge and dataset description only.")
    hypothesis_guess: str = Field(default="", description="Educated guess about whether the hypothesis is supported or not based on domain knowledge.")
    formatted_answer: str = Field(default="", description="Final answer formatted according to the required format, based on the guess.")