import argparse
import re
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
import requests
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image as AGImage
from PIL import Image
from MultiAgent import *
from Prompt import  *
import io
from typing import Callable, Sequence
import asyncio
from autogen_core import Image as AGImage
from Dataset import *
import sys
import time
import Evaluation

class ChatManagerAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Responsible for receiving user input.")
        self.output={}

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        pass

    async def on_messages_m(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        mathvista = messages[0]
        self.output['id'] = int(mathvista['pid'])-1

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")


        input_message = [prompt_interpreter, mathvista['image']]
        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            capcontext = (
                f"Question:\n{mathvista['question']}\n"
                f"Caption:\n{caption_content}\n"
                # f"Context:\n{mathvista['context']}\n"
                f"Choices:\n{mathvista['choices']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            search_input = (
                f"Question:\n{mathvista['question']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{mathvista['query']}\n"
                f"Choices:\n{mathvista['choices']}"
                f"Question_type:\n{mathvista['question_type']}\n"
                f"answer_type:\n{mathvista['answer_type']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, search_response, solution_response

        align_response, search_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        step_history = {
            "caption": caption_response.chat_message.content,
            "alignment": align_response.chat_message.content,
            "knowledge": search_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)
        critic_response = await critic_agent.on_messages(
            [str(step_history), mathvista['image'], mathvista['query']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)
        # print(eval_result)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "caption":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('caption', '')}\n"
                )
                new_caption = await interpreter_agent.on_messages(
                    [[feedback, mathvista['image']]],
                    cancellation_token
                )
                self.output["InterpreterAgent_Feedback"] = new_caption.chat_message.content

                align_response, search_response, solution_response = await execute_pipeline(
                    new_caption.chat_message.content, 0)

            elif worst_step == "alignment":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('alignment', '')}\n"
                )
                align_input = (
                    f"Question:\n{mathvista['question']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    # f"Context:\n{mathvista['context']}\n"
                    f"Choices:\n{mathvista['choices']}\n"
                )
                new_align = await aligner_agent.on_messages(
                    [feedback, align_input],
                    cancellation_token
                )
                self.output["AlignerAgent_Feedback"] = new_align.chat_message.content

                search_input = (
                    f"Question:\n{mathvista['question']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                )
                search_response = await scholar_agent.on_messages([search_input], cancellation_token)
                self.output['ScholarAgent_Feedback'] = search_response.chat_message.content

                solution_input = (
                    f"Question:\n{mathvista['query']}\n"
                    f"Choices:\n{mathvista['choices']}"
                    f"Question_type:\n{mathvista['question_type']}\n"
                    f"answer_type:\n{mathvista['answer_type']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                    f"Knowledge:\n{search_response.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "knowledge":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('knowledge', '')}\n"
                )
                search_input = (
                    f"Question:\n{mathvista['question']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                )
                new_knowledge = await scholar_agent.on_messages(
                    [feedback, search_input],
                    cancellation_token
                )
                self.output['ScholarAgent_Feedback'] = new_knowledge.chat_message.content

                solution_input = (
                    f"Question:\n{mathvista['query']}\n"
                    f"Choices:\n{mathvista['choices']}"
                    f"Question_type:\n{mathvista['question_type']}\n"
                    f"answer_type:\n{mathvista['answer_type']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{new_knowledge.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content


            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{mathvista['query']}\n"
                    f"Choices:\n{mathvista['choices']}"
                    f"Question_type:\n{mathvista['question_type']}\n"
                    f"answer_type:\n{mathvista['answer_type']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{step_history['knowledge']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = mathvista['answer']

        await self.save_output(mathvista_agent_result)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_oly_full(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        olympiad = messages[0]
        self.output['id'] = int(olympiad['id'])

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")

        input_message = [prompt_interpreter]
        for i in range(olympiad['num_img']):
            input_message.append(olympiad[f"image_{i + 1}"])

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            capcontext = (
                f"Question:\n{olympiad['question']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{olympiad['context']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            search_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Subfield:\n{olympiad['subfield']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Answer_type:\n{olympiad['answer_type']}\n"
                f"Unit:\n{olympiad['unit']}\n"
                f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, search_response, solution_response

        align_response, search_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        step_history = {
            "caption": caption_response.chat_message.content,
            "alignment": align_response.chat_message.content,
            "knowledge": search_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)

        critic_response = await critic_agent.on_messages(
            [str(step_history), input_message[1:], olympiad['question']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)
        # print(eval_result)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "caption":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('caption', '')}\n"
                )
                input_c = [feedback]
                for j in range(olympiad['num_img']):
                    input_c.append(olympiad[f"image_{j + 1}"])

                new_caption = await interpreter_agent.on_messages(
                    [input_c],
                    cancellation_token
                )
                self.output["InterpreterAgent_Feedback"] = new_caption.chat_message.content

                align_response, search_response, solution_response = await execute_pipeline(
                    new_caption.chat_message.content, 0)

            elif worst_step == "alignment":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('alignment', '')}\n"
                )
                align_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{olympiad['context']}\n"
                )
                new_align = await aligner_agent.on_messages(
                    [feedback, align_input],
                    cancellation_token
                )
                self.output["AlignerAgent_Feedback"] = new_align.chat_message.content

                search_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Subfield:\n{olympiad['subfield']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                )
                search_response = await scholar_agent.on_messages([search_input], cancellation_token)
                self.output['ScholarAgent_Feedback'] = search_response.chat_message.content

                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                    f"Knowledge:\n{search_response.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "knowledge":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('knowledge', '')}\n"
                )
                search_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Subfield:\n{olympiad['subfield']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                )
                new_knowledge = await scholar_agent.on_messages(
                    [feedback, search_input],
                    cancellation_token
                )
                self.output['ScholarAgent_Feedback'] = new_knowledge.chat_message.content

                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{new_knowledge.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{step_history['knowledge']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = olympiad['answer'][0]

        await self.save_output(olympiad_result_full)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_oly_wo_interpreter(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        olympiad = messages[0]
        self.output['id'] = int(olympiad['id'])

        input_agent = UserProxyAgent("input_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")

        input_message = [prompt_interpreter]

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]

        async def execute_pipeline(flag):
            capcontext = (
                f"Question:\n{olympiad['question']}\n"
                f"Context:\n{olympiad['context']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            search_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Subfield:\n{olympiad['subfield']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Answer_type:\n{olympiad['answer_type']}\n"
                f"Unit:\n{olympiad['unit']}\n"
                f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, search_response, solution_response

        align_response, search_response, solution_response = await execute_pipeline(1)

        step_history = {
            "alignment": align_response.chat_message.content,
            "knowledge": search_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)

        critic_response = await critic_agent.on_messages(
            [str(step_history), input_message[1:], olympiad['question']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)
        # print(eval_result)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "alignment":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('alignment', '')}\n"
                )
                align_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Context:\n{olympiad['context']}\n"
                )
                new_align = await aligner_agent.on_messages(
                    [feedback, align_input],
                    cancellation_token
                )
                self.output["AlignerAgent_Feedback"] = new_align.chat_message.content

                search_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Subfield:\n{olympiad['subfield']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                )
                search_response = await scholar_agent.on_messages([search_input], cancellation_token)
                self.output['ScholarAgent_Feedback'] = search_response.chat_message.content

                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                    f"Knowledge:\n{search_response.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "knowledge":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('knowledge', '')}\n"
                )
                search_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Subfield:\n{olympiad['subfield']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                )
                new_knowledge = await scholar_agent.on_messages(
                    [feedback, search_input],
                    cancellation_token
                )
                self.output['ScholarAgent_Feedback'] = new_knowledge.chat_message.content

                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{new_knowledge.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{step_history['knowledge']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = olympiad['answer'][0]

        await self.save_output(olympiad_result_wo_interpreter)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_oly_wo_aligner(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        olympiad = messages[0]
        self.output['id'] = int(olympiad['id'])

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")

        input_message = [prompt_interpreter]
        for i in range(olympiad['num_img']):
            input_message.append(olympiad[f"image_{i + 1}"])

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            search_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Subfield:\n{olympiad['subfield']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{olympiad['context']}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Answer_type:\n{olympiad['answer_type']}\n"
                f"Unit:\n{olympiad['unit']}\n"
                f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{olympiad['context']}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return search_response, solution_response

        search_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        step_history = {
            "caption": caption_response.chat_message.content,
            "knowledge": search_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)

        critic_response = await critic_agent.on_messages(
            [str(step_history), input_message[1:], olympiad['question']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "caption":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('caption', '')}\n"
                )
                input_c = [feedback]
                for j in range(olympiad['num_img']):
                    input_c.append(olympiad[f"image_{j + 1}"])

                new_caption = await interpreter_agent.on_messages(
                    [input_c],
                    cancellation_token
                )
                self.output["InterpreterAgent_Feedback"] = new_caption.chat_message.content

                search_response, solution_response = await execute_pipeline(
                    new_caption.chat_message.content, 0)

            elif worst_step == "knowledge":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('knowledge', '')}\n"
                )
                search_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Subfield:\n{olympiad['subfield']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{olympiad['context']}\n"
                )
                new_knowledge = await scholar_agent.on_messages(
                    [feedback, search_input],
                    cancellation_token
                )
                self.output['ScholarAgent_Feedback'] = new_knowledge.chat_message.content

                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{olympiad['context']}\n"
                    f"Knowledge:\n{new_knowledge.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{olympiad['context']}\n"
                    f"Knowledge:\n{step_history['knowledge']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = olympiad['answer'][0]

        await self.save_output(olympiad_result_wo_aligner)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_oly_wo_scholar(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        olympiad = messages[0]
        self.output['id'] = int(olympiad['id'])

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")

        input_message = [prompt_interpreter]
        for i in range(olympiad['num_img']):
            input_message.append(olympiad[f"image_{i + 1}"])

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            capcontext = (
                f"Question:\n{olympiad['question']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{olympiad['context']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            solution_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Answer_type:\n{olympiad['answer_type']}\n"
                f"Unit:\n{olympiad['unit']}\n"
                f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, solution_response

        align_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        step_history = {
            "caption": caption_response.chat_message.content,
            "alignment": align_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)

        critic_response = await critic_agent.on_messages(
            [str(step_history), input_message[1:], olympiad['question']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)
        # print(eval_result)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "caption":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('caption', '')}\n"
                )
                input_c = [feedback]
                for j in range(olympiad['num_img']):
                    input_c.append(olympiad[f"image_{j + 1}"])

                new_caption = await interpreter_agent.on_messages(
                    [input_c],
                    cancellation_token
                )
                self.output["InterpreterAgent_Feedback"] = new_caption.chat_message.content

                align_response, solution_response = await execute_pipeline(
                    new_caption.chat_message.content, 0)

            elif worst_step == "alignment":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('alignment', '')}\n"
                )
                align_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{olympiad['context']}\n"
                )
                new_align = await aligner_agent.on_messages(
                    [feedback, align_input],
                    cancellation_token
                )
                self.output["AlignerAgent_Feedback"] = new_align.chat_message.content


                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{olympiad['question']}\n"
                    f"Answer_type:\n{olympiad['answer_type']}\n"
                    f"Unit:\n{olympiad['unit']}\n"
                    f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = olympiad['answer'][0]

        await self.save_output(olympiad_result_wo_scholar)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_oly_wo_critic(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        olympiad = messages[0]
        self.output['id'] = int(olympiad['id'])

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")

        input_message = [prompt_interpreter]
        for i in range(olympiad['num_img']):
            input_message.append(olympiad[f"image_{i + 1}"])

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            capcontext = (
                f"Question:\n{olympiad['question']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{olympiad['context']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            search_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Subfield:\n{olympiad['subfield']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{olympiad['question']}\n"
                f"Answer_type:\n{olympiad['answer_type']}\n"
                f"Unit:\n{olympiad['unit']}\n"
                f"Is_multiple_answer:\n{olympiad['is_multiple_answer']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, search_response, solution_response

        align_response, search_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = olympiad['answer'][0]

        await self.save_output(olympiad_result_wo_critic)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_e(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        emma = messages[0]
        self.output['id'] = emma['pid']

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")

        input_message = [prompt_interpreter, emma['image']]

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            capcontext = (
                f"Question:\n{emma['question']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{emma['context']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            search_input = (
                f"Question:\n{emma['question']}\n"
                f"Category:\n{emma['category']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{emma['question']}\n"
                f"Options:\n{emma['options']}\n"
                f"Type:\n{emma['type']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, search_response, solution_response

        align_response, search_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        step_history = {
            "caption": caption_response.chat_message.content,
            "alignment": align_response.chat_message.content,
            "knowledge": search_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)

        critic_response = await critic_agent.on_messages(
            [str(step_history), input_message[1:], emma['question']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)
        # print(eval_result)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "caption":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('caption', '')}\n"
                )
                new_caption = await interpreter_agent.on_messages(
                    [feedback, emma['image']],
                    cancellation_token
                )
                self.output["InterpreterAgent_Feedback"] = new_caption.chat_message.content

                align_response, search_response, solution_response = await execute_pipeline(
                    new_caption.chat_message.content, 0)

            elif worst_step == "alignment":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('alignment', '')}\n"
                )
                align_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{emma['context']}\n"
                )
                new_align = await aligner_agent.on_messages(
                    [feedback, align_input],
                    cancellation_token
                )
                self.output["AlignerAgent_Feedback"] = new_align.chat_message.content

                search_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Category:\n{emma['category']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                )
                search_response = await scholar_agent.on_messages([search_input], cancellation_token)
                self.output['ScholarAgent_Feedback'] = search_response.chat_message.content

                solution_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Options:\n{emma['options']}\n"
                    f"Type:\n{emma['type']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                    f"Knowledge:\n{search_response.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "knowledge":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('knowledge', '')}\n"
                )
                search_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Category:\n{emma['category']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                )
                new_knowledge = await scholar_agent.on_messages(
                    [feedback, search_input],
                    cancellation_token
                )
                self.output['ScholarAgent_Feedback'] = new_knowledge.chat_message.content

                solution_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Type:\n{emma['type']}\n"
                    f"Options:\n{emma['options']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{new_knowledge.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Options:\n{emma['options']}\n"
                    f"Type:\n{emma['type']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{step_history['knowledge']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = emma['answer']

        # await self.save_output(emma_agent_result)

        return Response(chat_message=solution_response.chat_message.content)

    async def on_messages_s(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        self.output = {}
        emma = messages[0]
        self.output['id'] = emma['pid']

        input_agent = UserProxyAgent("input_agent")
        interpreter_agent = InterpreterAgent("interpreter_agent")
        aligner_agent = AlignerAgent("aligner_agent")
        scholar_agent = ScholarAgent("scholar_agent")
        solver_agent = SolverAgent("solver_agent")
        critic_agent = CriticAgent("critic_agent")

        input_message = [prompt_interpreter, emma['image_1'], emma['image_2'], emma['image_3'], emma['image_4'], emma['image_5']]
        # input_message = [prompt_interpreter, emma['image_1'], emma['image_2'], emma['image_3'], emma['image_4']]

        input_response = await input_agent.on_messages(input_message, cancellation_token)
        self.output["UserProxyAgent"] = input_response.chat_message[0]
        caption_response = await interpreter_agent.on_messages([input_response.chat_message], cancellation_token)
        self.output["InterpreterAgent"] = caption_response.chat_message.content

        async def execute_pipeline(caption_content, flag):
            capcontext = (
                f"Question:\n{emma['question']}\n"
                f"Caption:\n{caption_content}\n"
                f"Context:\n{emma['context']}\n"
            )
            align_response = await aligner_agent.on_messages([capcontext], cancellation_token)
            if flag:
                self.output["AlignerAgent"] = align_response.chat_message.content
            else:
                self.output["AlignerAgent_Feedback"] = align_response.chat_message.content

            search_input = (
                f"Question:\n{emma['question']}\n"
                f"Category:\n{emma['category']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
            )
            search_response = await scholar_agent.on_messages([search_input], cancellation_token)
            if flag:
                self.output["ScholarAgent"] = search_response.chat_message.content
            else:
                self.output["ScholarAgent_Feedback"] = search_response.chat_message.content

            solution_input = (
                f"Question:\n{emma['question']}\n"
                f"Options:\n{emma['options']}\n"
                f"Type:\n{emma['type']}\n"
                f"Caption&Context:\n{align_response.chat_message.content}\n"
                f"Knowledge:\n{search_response.chat_message.content}\n"
            )
            solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
            if flag:
                self.output["SolverAgent"] = solution_response.chat_message.content
            else:
                self.output["SolverAgent_Feedback"] = solution_response.chat_message.content

            return align_response, search_response, solution_response

        align_response, search_response, solution_response = await execute_pipeline(
            caption_response.chat_message.content, 1)

        step_history = {
            "caption": caption_response.chat_message.content,
            "alignment": align_response.chat_message.content,
            "knowledge": search_response.chat_message.content,
            "solution": solution_response.chat_message.content
        }
        # print(step_history)

        critic_response = await critic_agent.on_messages(
            [str(step_history), input_message[1:], emma['question']],
            cancellation_token
        )
        self.output["CriticAgent"] = critic_response.chat_message.content

        eval_result = eval(critic_response.chat_message.content)
        # print(eval_result)

        if eval_result.get("need_feedback", False):
            feedback_data = eval_result.get("feedback", {})
            worst_step = eval_result["worst_step"]

            if worst_step == "caption":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('caption', '')}\n"
                )
                new_caption = await interpreter_agent.on_messages(
                    [feedback, emma['image_1'], emma['image_2'], emma['image_3'], emma['image_4'], emma['image_5']],
                    cancellation_token
                )
                self.output["InterpreterAgent_Feedback"] = new_caption.chat_message.content

                align_response, search_response, solution_response = await execute_pipeline(
                    new_caption.chat_message.content, 0)

            elif worst_step == "alignment":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('alignment', '')}\n"
                )
                align_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Caption:\n{step_history['caption']}\n"
                    f"Context:\n{emma['context']}\n"
                )
                new_align = await aligner_agent.on_messages(
                    [feedback, align_input],
                    cancellation_token
                )
                self.output["AlignerAgent_Feedback"] = new_align.chat_message.content

                search_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Category:\n{emma['category']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                )
                search_response = await scholar_agent.on_messages([search_input], cancellation_token)
                self.output['ScholarAgent_Feedback'] = search_response.chat_message.content

                solution_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Options:\n{emma['options']}\n"
                    f"Type:\n{emma['type']}\n"
                    f"Caption&Context:\n{new_align.chat_message.content}\n"
                    f"Knowledge:\n{search_response.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "knowledge":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('knowledge', '')}\n"
                )
                search_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Category:\n{emma['category']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                )
                new_knowledge = await scholar_agent.on_messages(
                    [feedback, search_input],
                    cancellation_token
                )
                self.output['ScholarAgent_Feedback'] = new_knowledge.chat_message.content

                solution_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Type:\n{emma['type']}\n"
                    f"Options:\n{emma['options']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{new_knowledge.chat_message.content}\n"
                )
                solution_response = await solver_agent.on_messages([solution_input], cancellation_token)
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

            elif worst_step == "solution":
                feedback = (
                    f"Improve the description based on the following feedback:{feedback_data.get('solution', '')}\n"
                )
                solution_input = (
                    f"Question:\n{emma['question']}\n"
                    f"Options:\n{emma['options']}\n"
                    f"Type:\n{emma['type']}\n"
                    f"Caption&Context:\n{step_history['alignment']}\n"
                    f"Knowledge:\n{step_history['knowledge']}\n"
                )
                solution_response = await solver_agent.on_messages(
                    [feedback, solution_input],
                    cancellation_token
                )
                self.output['SolverAgent_Feedback'] = solution_response.chat_message.content

        self.output['final_answer'] = json.loads(solution_response.chat_message.content)['final_answer']
        self.output['true_answer'] = emma['answer']

        await self.save_output("Output/EMMA/Chemistry/agent_output.json")

        return Response(chat_message=solution_response.chat_message.content)

    async def save_output(self, outfile):
        try:
            with open(outfile, 'r', encoding='utf-8') as file:
                data_list = json.load(file)
        except FileNotFoundError:
            data_list = []

        data_list.append(self.output)

        with open(outfile, 'w', encoding='utf-8') as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)

        print("Updated!")

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

async def run_agents(dataname, ablation):
    chat_manager_agent = ChatManagerAgent("chat_manager")

    if dataname == "mathvista":
        dataset = MathVista(MathVista_PATH)
    elif dataname == "olympiad":
        if OLYFILEPATH == PZCE or OLYFILEPATH == MZCE:
            dataset = OlympiadBench(Olympiad_PATH, 300, f"Output/OlympiadBench/{OLYFILEPATH}/sample_ids.json")
        else:
            dataset = OlympiadBench(Olympiad_PATH)
    elif dataname == "emma":
        dataset = EMMA(EMMA_PATH)
    else:
        raise ValueError(f"Unknown Dataset: {dataname}")
    while True:
        entry = dataset.current_entry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if dataname == "mathvista":
                    response = await chat_manager_agent.on_messages_m([entry], CancellationToken())
                elif dataname == "olympiad":
                    method_name = f"on_messages_oly_{ablation}"
                    response = await getattr(chat_manager_agent, method_name)([entry], CancellationToken())
                elif dataname == "emma":
                    response = await chat_manager_agent.on_messages_e([entry], CancellationToken())
                break
            except Exception as e:
                if attempt == max_retries - 1: 
                    raise
                print(f"Attempt {attempt + 1} failed, retrying... (Error: {str(e)})")

        if not dataset.move_next():
            break


async def process_special():
    chat_manager_agent = ChatManagerAgent("chat_manager")
    dataset = EMMASpecial("Dataset/EMMA/PhysicsMini.parquet")
    # dataset = EMMASpecial("Dataset/EMMA/ChemistryMini.parquet")
    for i in range(1):
        while True:
            entry = dataset.current_entry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    chat_manager_response = await chat_manager_agent.on_messages_s([entry], CancellationToken())
                    break 
                except Exception as e:
                    if attempt == max_retries - 1: 
                        raise
                    print(f"Attempt {attempt + 1} failed, retrying... (Error: {str(e)})")
            if not dataset.move_next():
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["mathvista", "olympiad", "emma"], required=True)
    parser.add_argument("--ablation", choices=["full", "wo_interpreter", "wo_aligner", "wo_scholar", "wo_critic"],
                        default="full")
    args = parser.parse_args()

    asyncio.run(run_agents(args.dataset, args.ablation))