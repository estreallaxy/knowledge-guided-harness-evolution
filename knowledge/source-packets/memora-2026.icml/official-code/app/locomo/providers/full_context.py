# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
import time
from collections import defaultdict

from jinja2 import Template
from omegaconf import DictConfig
from tqdm import tqdm

from utils import load_data
from memora.utils.llm import get_aoai_chat_completion_client

# Using the same prompt template as Mem0/Memora for fair comparison
PROMPT = """
    You are an intelligent memory assistant that answers questions based on conversation history.

    # CONTEXT:
    You have access to the full conversation history between two speakers. The conversation contains timestamped information that may be relevant to answering the question.

    # INSTRUCTIONS:
    1. Carefully analyze the conversation history
    2. Pay special attention to the timestamps to determine the answer
    3. If the question asks about a specific event or fact, look for direct evidence in the conversation
    4. If the conversation contains contradictory information, prioritize the most recent information in terms of timestamp
    5. If there is a question about time references (like "last year", "two months ago", etc.), calculate the actual date based on the conversation timestamp. For example, if a conversation from 4 May 2022 mentions "went to India last year," then the trip occurred in 2021.
    6. Always convert relative time references to specific dates, months, or years. For example, convert "last year" to "2022" or "two months ago" to "March 2023" based on the conversation timestamp. Ignore the reference while answering the question.
    7. Focus only on the content of the conversation. Do not confuse character names mentioned in conversation with the actual speakers.
    8. The answer should be less than 5-6 words.


    # APPROACH (Think step by step):
    1. First, examine all parts of the conversation that contain information related to the question
    2. Examine the timestamps and content carefully
    3. Look for explicit mentions of dates, times, locations, or events that answer the question
    4. If the answer requires calculation (e.g., converting relative time references), show your work
    5. Formulate a precise, concise answer based solely on the evidence in the conversation
    6. Double-check that your answer directly addresses the question asked
    7. Ensure your final answer is specific and avoids vague time references

    Conversation History:

    {{CONTEXT}}

    Question: {{QUESTION}}

    Answer:
    """


class FullContextManager:
    """
    Full context baseline that uses the entire conversation history as context
    without any memory extraction or retrieval.
    """

    def __init__(self, cfg: DictConfig, data_path: str):
        self.cfg = cfg
        self.model = cfg.llm.model  # gpt-4.1-mini for generation
        self.llm_client = get_aoai_chat_completion_client(cfg)
        self.data_path = data_path

    def generate_response(self, question, context):
        """Generate response using full conversation context."""
        template = Template(PROMPT)
        prompt = template.render(CONTEXT=context, QUESTION=question)

        max_retries = 3
        retries = 0

        while retries <= max_retries:
            try:
                t1 = time.time()
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that can answer questions based on the provided context."
                        ,
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                )
                t2 = time.time()
                return response.choices[0].message.content.strip(), t2 - t1
            except Exception as e:
                retries += 1
                if retries > max_retries:
                    raise e
                time.sleep(1)  # Wait before retrying

    def clean_chat_history(self, chat_history):
        """Format chat history as a readable string."""
        cleaned_chat_history = ""
        for chat in chat_history:
            timestamp = chat.get("timestamp", "")
            speaker = chat.get("speaker", "")
            text = chat.get("text", "")
            cleaned_chat_history += f"{timestamp} | {speaker}: {text}\n"
        return cleaned_chat_history

    def process_all_conversations(self, output_file_path):
        """Process all conversations using full context."""
        data = load_data(self.data_path)

        FINAL_RESULTS = {}
        for idx, item in tqdm(enumerate(data), desc="Processing conversations", total=len(data)):
            # Get conversation ID from sample_id if available, otherwise use index
            key = item.get("sample_id", f"conversation_{idx}")

            # Extract all chat sessions and flatten them into a single chat history
            conversation = item["conversation"]
            chat_history = []

            # Iterate through all sessions
            session_idx = 1
            while f"session_{session_idx}" in conversation:
                session_chats = conversation[f"session_{session_idx}"]
                session_datetime = conversation.get(f"session_{session_idx}_date_time", "")

                # Add each chat in the session
                for chat in session_chats:
                    chat_with_timestamp = chat.copy()
                    if session_datetime and "timestamp" not in chat_with_timestamp:
                        chat_with_timestamp["timestamp"] = session_datetime
                    chat_history.append(chat_with_timestamp)

                session_idx += 1

            # Format the entire conversation as context
            full_context = self.clean_chat_history(chat_history)

            questions = item["qa"]

            FINAL_RESULTS[key] = []
            for qa_item in tqdm(questions, desc="Answering questions", leave=False):
                question = qa_item["question"]
                answer = qa_item.get("answer", "")
                category = str(qa_item["category"])

                # Use full conversation as context
                response, response_time = self.generate_response(question, full_context)

                FINAL_RESULTS[key].append(
                    {
                        "question": question,
                        "answer": answer,
                        "category": category,
                        "context": full_context,  # Store full context for reference
                        "response": response,
                        "response_time": response_time,
                    }
                )

            # Save after each conversation
            with open(output_file_path, "w+") as f:
                json.dump(FINAL_RESULTS, f, indent=4)

        # Final save
        with open(output_file_path, "w+") as f:
            json.dump(FINAL_RESULTS, f, indent=4)
