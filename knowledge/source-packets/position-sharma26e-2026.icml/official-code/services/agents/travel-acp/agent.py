# /app/travel_experiment/acp_agent/agent.py

import os
import asyncio
import logging
from typing import AsyncGenerator
from datetime import date
from collections import defaultdict
import functools
import json

# --- ACP Imports ---
from acp_sdk.server import Server, Context
from acp_sdk.models import Message, MessagePart

# --- CrewAI and LangChain Imports ---
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai.tools import BaseTool

# --- Import our custom tools ---
from .tools import find_flights, find_specialist_agent, delegate_task_via_acp

from services.agents.utils import SimpleMemoryCache, report_activity
from .tools import AGENT_NAME


logger = logging.getLogger(__name__)
server = Server()

session_memory = SimpleMemoryCache()
memory_lock = asyncio.Lock()

# This variable will hold the main event loop once the server is running.
main_event_loop = None

def _session_injector_wrapper(tool_object: BaseTool, session_id: str) -> BaseTool:
    """
    Wraps a CrewAI Tool object to inject the session_id into its kwargs.
    This does NOT do any reporting itself; it just provides the tool
    with the ID it needs to do its *own* reporting.
    """
    original_func = tool_object.func

    @functools.wraps(original_func)
    def wrapped_func(*args, **kwargs):
        # Inject the session_id
        kwargs['session_id'] = str(session_id)
        return original_func(*args, **kwargs)

    # Need to create deep copy for concurrent request
    new_tool = tool_object.model_copy(deep=True)
    new_tool.func = wrapped_func
    # And return the same object, now modified.
    return new_tool

@server.agent(
    name="travel_specialist_agent",
    description='A specialist agent that finds flight information and can orchestrate other agents for sub-tasks like currency conversion.\n\nUses ACP for agent to agent messaging and CrewAI as its agentic framework',
)
async def travel_specialist_agent(
    input: list[Message], context: Context
) -> AsyncGenerator[Message, None]:
    """The main logic for the ACP Travel Specialist, orchestrated by CrewAI."""

    # We capture the running event loop on the first request and store it
    # in the global variable so our tools can access it.
    global main_event_loop
    if main_event_loop is None:
        main_event_loop = asyncio.get_running_loop()

    session_id = context.session.id
    logger.info(f"ACP_AGENT: Request received for session ID: {session_id}")
    
    query = input[-1].parts[0].content if input and input[-1].parts else ""
    if not query:
        yield Message(parts=[MessagePart(content="Please provide a travel-related task.")])
        return

    history = await session_memory.get(session_id)
    history.append({"role": "User", "content": query})
    await session_memory.set(session_id, history)

    # Prepend the history to the new query to give the agent context.
    context_string = "\n".join([f"{item['role']}: {item['content']}" for item in history])
    full_query = f"{context_string}\nUser: {query}" # Combine context and current query

    # HACK: Pre-prefix the model name. crewai/litellm will strip the first
    # "openai/" prefix, leaving the correct "openai/gpt-oss-120b"
    # for the custom API endpoint.
    model_name = f"openai/{os.getenv('OPENAI_MODEL_NAME')}"

    llm = ChatOpenAI(
        model=model_name,
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    session_find_flights = _session_injector_wrapper(find_flights, session_id)
    session_find_specialist_agent = _session_injector_wrapper(find_specialist_agent, session_id)
    session_delegate_task_via_acp = _session_injector_wrapper(delegate_task_via_acp, session_id)

    specialist_agent = Agent(
        role='Travel Logistics Coordinator',
        goal='Fulfill all parts of the user travel requests by finding flights and delegating sub-tasks to other specialist agents.',
        backstory=(
            "You are a master coordinator who follows a plan step-by-step. "
            "Your memory is perfect. Once you have all necessary information, you provide the final answer. "
            "**You MUST strictly follow this format for your responses, with no extra text:**\n"
            "```\n"
            "Thought: I need to perform an action to achieve my goal. I will choose a tool and define its input.\n"
            "Action: [tool_name]\n"
            "Action Input: {\"key\": \"value\"}\n"
            "```\n"
            "After getting the result from a tool (the Observation), you will decide the next step."
            "Always make it clear that the prices come from the Amadeus API and may differ from final booking prices on airline or OTA websites."
        ),
        #tools=[find_flights, find_specialist_agent, delegate_task_via_acp],
        tools=[session_find_flights, session_find_specialist_agent, session_delegate_task_via_acp],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    today_str = date.today().strftime("%Y-%m-%d")

    travel_task = Task(
        description=f"""
        Fulfill ALL parts of the user's request: '{full_query}'.

        For your reference, the current date is {today_str}. If the user provides
        a partial date like "August 15th", assume they mean the upcoming one.

        Follow this strict plan:
        1. First, use the 'find_flights' tool to get the flight details. The price will be in CHF.
        2. If the tool returns an error, your final answer MUST be that error message.
        3. If the user specified a different currency, you MUST then perform the currency conversion by following steps 4 and 5.
        4. To convert the currency, first use 'find_specialist_agent' to locate the currency agent.
        5. Then, use 'delegate_task_via_acp' with a simple, natural language `task_payload`. For example: "Convert 130.8 CHF to USD".
        
        --- 
        **CRITICAL FINAL STEP:**
        6. After you have all the necessary information (either just the flight details, or the flight details AND the converted price), you MUST provide a final, comprehensive answer.
        **DO NOT USE ANY MORE TOOLS.** Synthesize all the information you have gathered into a clean, user-friendly summary.
        7. Add a disclamer to the final message depending on if the data generated is with amadeus or synthesized fake data.
        ---
        """,
        expected_output=(
            "A complete, final answer that includes the flight details. "
            "If a currency conversion was performed, the answer must also include the converted price. "
            "If any tool produced an error, the final answer should be ONLY that error message."
        ),
        agent=specialist_agent,
    )

    crew = Crew(agents=[specialist_agent], tasks=[travel_task], process=Process.sequential, verbose=True)

    final_answer = await asyncio.to_thread(crew.kickoff)
    async with memory_lock:
        current_history = await session_memory.get(session_id)
        current_history.append({"role": "Agent", "content": final_answer})
        await session_memory.set(session_id, current_history)

    #! NOTE: assumes message from "coord-a2a" in future perform reverse DNS
    report_activity(
        session_id=str(session_id),
        source=AGENT_NAME,
        target="coord-a2a", 
        content=str(final_answer),
        msg_type="communication"
    )
    
    yield Message(parts=[MessagePart(content=str(final_answer))])
