import os
import json
import logging
import asyncio
from typing import List, TypedDict, Annotated, Union
import operator
from uuid import uuid4

from langchain_core.messages import BaseMessage, AnyMessage, ToolMessage, HumanMessage, SystemMessage, AIMessage
#from langchain_ollama.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
#from langgraph.prebuilt import ToolExecutor

from .tools import discover_available_specialists, delegate_task_to_agent
from services.agents.utils import report_activity

logger = logging.getLogger(__name__)

# --- 1. Define the Tools and State ---
tools = [discover_available_specialists, delegate_task_to_agent]
tool_map = {tool.name: tool for tool in tools}

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    session_id: str

# --- 2. Define the LLM ---
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)# Bind the tools to the LLM so it knows their signatures
llm_with_tools = llm.bind_tools(tools)

def _fix_delegation_args(args: dict, state: AgentState) -> dict:
    """
    Helper function to find and inject missing service_name or url
    into a delegate_task_to_agent tool call.
    """
    service_name = args.get("target_service_name")
    agent_url = args.get("target_agent_url")

    # If both are present or neither is, we can't fix it.
    if (agent_url and service_name) or (not agent_url and not service_name):
        return args

    # Scan history for the agent list
    agent_list = []
    for msg in reversed(state["messages"]):
        if isinstance(msg, ToolMessage) and msg.name == "discover_available_specialists":
            try:
                agent_list = json.loads(msg.content)
                break
            except (json.JSONDecodeError, TypeError):
                continue # Ignore malformed history
    
    if not agent_list:
        return args # Can't fix it

    for agent_card in agent_list:
        # Case 1: We have the URL, need the service_name
        if agent_url and agent_card.get("url") == agent_url:
            found_name = agent_card.get("service_name")
            if found_name:
                logger.warning(f"Parser: Injected missing 'target_service_name': {found_name}")
                args["target_service_name"] = found_name
                break
        
        # Case 2: We have the service_name, need the URL
        if service_name and agent_card.get("service_name") == service_name:
            found_url = agent_card.get("url")
            if found_url:
                logger.warning(f"Parser: Injected missing 'target_agent_url': {found_url}")
                args["target_agent_url"] = found_url
                break
                
    return args

# --- 3. Define the Nodes of the Graph ---

async def agent_node(state: AgentState):
    """The primary node that decides the next action based on the conversation history."""

    session_id = state.get("session_id", "")

    # This ensures the user's own message appears on their graph
    if session_id and state["messages"] and isinstance(state["messages"][-1], HumanMessage):
        report_activity(
            session_id=session_id,
            source="frontend", # The user's interface
            target="coord-a2a",
            content=state["messages"][-1].content,
            msg_type="communication"
        )

    system_message = """
    You are a master delegator, a central coordinator in a multi-agent system. Your primary goal is to solve the user's request by intelligently discovering and delegating tasks to specialist agents.

    ---
    ## Communication Style:

    -   **Be a Doer, Not a Talker**: Your primary job is to execute your plan, not to talk about your plan.
    -   **Execute Tool Calls Silently**: When you decide to use a tool, your entire output should ONLY be the JSON for that tool call. Do not add any conversational text.
    -   **Speak to the User Only When Necessary**: Only generate conversational text for the user in three situations:
        1.  You have the **final answer** and are presenting the complete result.
        2.  You have encountered an error and need to **inform the user of your recovery plan**.
        3.  **A specialist agent has asked a clarifying question you don't know the answer to**. In this case, your ONLY job is to relay that exact question to the user and wait for their response. Do not invent answers.

    ---
    ## Your Strict Process:

    1.  **Initial Analysis**: Understand the user's core request.
    2.  **Discover**: Your first step is ALWAYS to call the `discover_available_specialists` tool to get a fresh list of online agents.
    3.  **Select the Best Agent**:
        -   Carefully read the `description` and `skills` of EACH agent in the list.
        -   Compare the user's request directly against these descriptions to find the most relevant match.
    4.  **Delegate**:
        -   Once you have chosen the best agent, call the `delegate_task_to_agent` tool.
        -   `target_service_name`: The `service_name` from the agent card (e.g., "travel-acp").
        -   `target_agent_url`: The `url` from the agent card (e.g., "http://travel-acp:10000").
        -   `task_query`: A clear, natural language instruction for the specialist.
    5.  **Synthesize**: Once the specialist provides a successful result, present that information clearly to the user.

    ---
    ## How to Handle Errors:

    Do not give up easily.

    -   **If `delegate_task_to_agent` returns an error:**
        1.  **Analyze the Error**: Read the error message carefully.
        2.  **Re-Plan**: The error likely means you chose the WRONG agent.
        3.  **Try Again**: Go back to Step 2. Call `discover_available_specialists` AGAIN and choose a DIFFERENT agent.
        4.  **Inform the User**: Tell the user what went wrong and your new plan (e.g., "The Booking Agent couldn't help with that. I will now try the Flight Search Agent instead.").

    -   **If you have tried all relevant agents and none have worked:**
        -   Only then should you inform the user that you are unable to complete the request.

    ## ABSOLUTE NON-NEGOTIABLE RULES:

    1. Never invent or guess missing values.
    2. Never insert placeholders like "{origin}" or "{date}".
    3. If a specialist asks a clarifying question and you don't know the answer, relay it to the user.
    4. If you do not know the answer to the question, don't answer it.
    """
    messages_for_llm = [SystemMessage(content=system_message)] + state["messages"]
    
    # The brain logging we added is still very useful here.
    log_messages = "\n".join([f"  - {type(m).__name__}: {m.content[:250]}" for m in messages_for_llm])
    logger.info(f"--- BRAIN INPUT ---\n{log_messages}\n-------------------")
    
    response = await llm_with_tools.ainvoke(messages_for_llm)

    logger.info(f"--- BRAIN OUTPUT ---\n{response}\n--------------------")
    return {"messages": [response]}


async def parser_node(state: AgentState):
    """
    This new node's only job is to parse and validate the AI's output.
    It checks for malformed tool calls and fixes them.
    """
    last_message = state["messages"][-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        try:
            for tool_call in last_message.tool_calls:
                if tool_call.get("name") == "delegate_task_to_agent":
                    # --- CLEANUP: Call the helper function ---
                    tool_call["args"] = _fix_delegation_args(tool_call.get("args", {}), state)
        except Exception as e:
            logger.error(f"Error in smart parser: {e}")
        
        return # It's a valid (or fixed) tool call

    try:
        content_json = json.loads(last_message.content)
        if isinstance(content_json, dict) and "name" in content_json:
            logger.warning("Parser Node: Correcting malformed tool call from text.")
            
            raw_params = content_json.get("parameters", {})
            corrected_args = {}

            arg_map = {
                "target_service_name": ["agent_name", "target_service_name", "service_name"],
                "target_agent_url": ["agent", "agent_id", "agent_url", "target_agent_url", "url"],
                "task_query": ["task", "task_description", "query", "task_query"]
            }

            for real_arg, hallucinated_names in arg_map.items():
                for h_name in hallucinated_names:
                    if h_name in raw_params:
                        value = raw_params[h_name]
                        if isinstance(value, dict) and "value" in value:
                            corrected_args[real_arg] = value["value"]
                        else:
                            corrected_args[real_arg] = value
                        break 
            
            # --- CLEANUP: Call the helper function ---
            if content_json.get("name") == "delegate_task_to_agent":
                 corrected_args = _fix_delegation_args(corrected_args, state)
            
            corrected_message = AIMessage(
                content="",
                tool_calls=[{
                    "name": content_json.get("name"),
                    "args": corrected_args,
                    "id": f"call_{uuid4()}"
                }]
            )
            state["messages"][-1] = corrected_message

    except (json.JSONDecodeError, TypeError):
        pass


async def tool_node(state: AgentState):
    """This node executes the tool chosen by the agent_node."""
    last_message = state["messages"][-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        # This should not be hit if the graph is wired correctly.
        return {"messages": [ToolMessage(content="Error: Tool node reached without a valid tool call.", tool_call_id="error")]}

    tool_calls = last_message.tool_calls
    tool_messages = []
    session_id = state.get("session_id")
    for tool_call in tool_calls:
        tool_name, tool_args, tool_call_id = tool_call.get("name"), tool_call.get("args", {}), tool_call.get("id")
        
        #Inject correct session ID to all tools, agent can't be trusted to remember this
        tool_args["session_id"] = session_id

        logger.info(f"Executing tool: '{tool_name}' with args: {tool_args}")
        if tool_name in tool_map:
            try:
                tool_to_run = tool_map[tool_name]
                output = await tool_to_run.ainvoke(tool_args)
                tool_messages.append(ToolMessage(content=str(output), tool_call_id=tool_call_id))
            except Exception as e:
                tool_messages.append(ToolMessage(content=f"ERROR EXECUTING TOOL: {e}", tool_call_id=tool_call_id))
        else:
            tool_messages.append(ToolMessage(content=f"Error: Non-existent tool '{tool_name}' called.", tool_call_id=tool_call_id))
    return {"messages": tool_messages}

# --- 4. Define the Edges (Conditional Logic) ---

def should_continue(state: AgentState):
    """Decides whether to continue calling tools or to finish."""
    last_message = state["messages"][-1]
    # The parser node ensures tool_calls is populated if a tool call was intended.
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    
    # Report the final answer to the frontend
    # If it's not a tool call, it's the end of the line.
    session_id = state.get("session_id")
    if session_id and isinstance(last_message, AIMessage) and last_message.content:
        report_activity(
            session_id=session_id,
            source="coord-a2a",
            target="frontend", # The user's interface
            content=last_message.content,
            msg_type="communication"
        )
    return "end"

# --- 5. Assemble the Graph ---

def create_coordinator_graph() -> StateGraph:
    """Builds and returns the LangGraph for the coordinator agent."""
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("parser", parser_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    
    # New wiring: Agent -> Parser -> Router
    graph.add_edge("agent", "parser")
    graph.add_edge("tools", "agent")

    graph.add_conditional_edges(
        "parser", # The routing decision now happens AFTER the parser has cleaned the message.
        should_continue,
        {"tools": "tools", "end": END},
    )
    return graph.compile()

# We create a single, compiled graph instance to be used by the server.
coordinator_graph = create_coordinator_graph()