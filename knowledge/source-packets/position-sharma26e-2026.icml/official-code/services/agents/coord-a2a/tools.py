# /app/travel_experiment/a2a_agent/tools.py

import os
import logging
import httpx
import asyncio
import time

#import ollama
from openai import AsyncOpenAI

from typing import Annotated, Union, Optional

from uuid import uuid4
from urllib.parse import urlparse, urlunparse

from langchain_core.tools import tool
#from langchain_ollama.chat_models import ChatOllama 

from services.registry.mysql_agent_registry import AgentRegistry

# --- A2A Imports ---
from a2a.client import A2AClient, A2ACardResolver
#from a2a.client.llm_adapters import OllamaAdapter
from a2a.client.llm_adapters import OpenAIAdapter
from a2a.types import Message, MessageSendParams, Part, Role, TextPart
import json
from services.agents.utils import report_activity

logger = logging.getLogger(__name__)

AGENT_CARD_TTL_SECONDS = 30
# This dictionary will store agent cards and TTL, using the agent's id as the key.
AGENT_CARD_CACHE: dict[str, tuple[dict, float]] = {}

# Agent name to pass into the mysql server to note down who made discovery request
AGENT_NAME = "coord-a2a" 

# --- Initialize LLM client at the module level, once. ---
#ollama_server_url = os.getenv('OLLAMA_SERVER_URL')
#ollama_model_name = os.getenv('OLLAMA_MODEL_NAME')
openai_api_base = os.getenv('OPENAI_API_BASE')
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_model_name = os.getenv('OPENAI_MODEL_NAME') # This is used later

llm_adapter = None
if openai_api_base and openai_model_name and openai_api_key:
    openai_client = AsyncOpenAI(
        base_url=openai_api_base,
        api_key=openai_api_key
    )
    llm_adapter = OpenAIAdapter(client=openai_client)
else:
    logger.info("LLM variables OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_MODEL_NAME not set...")

# --- Helper Functions (Internal to this module) ---

def _list_agents_from_registry(session_id: str) -> list:
    """Connects to the DB and gets a raw list of online agents."""
    registry = None
    db_config = {'host': os.getenv('DB_HOST'), 'user': os.getenv('DB_USER'), 'password': os.getenv('DB_PASSWORD'), 'database': os.getenv('DB_NAME')}
    try:
        registry = AgentRegistry(db_config=db_config)
        agents = registry.read_from_registry(source_agent=AGENT_NAME, session_id=session_id)
        # Convert datetime objects for JSON serialization
        for agent in agents:
            if hasattr(agent.get('last_seen'), 'isoformat'):
                agent['last_seen'] = agent['last_seen'].isoformat()
        return agents
    except Exception as e:
        logger.error(f"Failed to query agent registry: {e}")
        return []
    finally:
        if registry: registry.close_connection()

def _get_agent_card_from_url(agent_url: str, session_id: str, service_name: str) -> dict:
    """Fetches and parses an agent card from its standard endpoint."""
    # This function checks multiple known endpoints for agent cards for max compatibility.
    possible_endpoints = [
        f"{agent_url.rstrip('/')}/.well-known/agent",
    ]
    for endpoint in possible_endpoints:
        try:
            # Report the handshake attempt          
            report_activity(
                session_id=session_id,
                source=AGENT_NAME,
                target=service_name,
                content=f"Requesting agent card from {endpoint}",
                msg_type="handshake"
            )
            
            response = httpx.get(endpoint, timeout=10.0)
            
            if response.status_code == 200:
                response_dict = response.json()
                response_json_string = json.dumps(response_dict)
                report_activity(
                    session_id=session_id,
                    source=service_name,   # The agent who SENT the card
                    target=AGENT_NAME,     # You (coord-a2a)
                    content=response_json_string, # The card as a string
                    msg_type="handshake"
                )
                return response_dict
        except httpx.RequestError:
            continue
            
    logger.error(f"Could not fetch agent card from {agent_url} on any known endpoint.")
    return {"error": f"Could not fetch card from {agent_url}"}


def _resolve_agent_url(
    agent_info_or_url: Union[dict, str],
    my_public_url: Optional[str] = None,
) -> Optional[str]:
    """
    Resolves the best URL (internal if local, otherwise public) for communicating with an agent.
    - If given a dict from the registry, it uses ip_address + docker_address.
    - If given a raw URL (docker or public), it passes it through unchanged unless we can improve it.
    Skips self.
    """
    public_url = None
    internal_url = None

    if isinstance(agent_info_or_url, dict):
        public_url = agent_info_or_url.get("ip_address")
        internal_url = agent_info_or_url.get("docker_address")
    elif isinstance(agent_info_or_url, str):
        # Raw URL case
        public_url = agent_info_or_url
        internal_url = None
    else:
        return None

    if not public_url:
        return None

    # Skip talking to myself
    if my_public_url and public_url == my_public_url:
        return None

    # Natively prioritize internal Docker container networks
    if internal_url:
        return internal_url

    return public_url

# --- LangGraph Tools ---

@tool
def discover_available_specialists(session_id: Annotated[str, "The current session ID"]) -> str:
    """
    Searches the registry for all available online agents and returns a JSON list of their capabilities.
    This tool is used to find out who is available to delegate tasks to.
    """
    logger.info("Discovering all available specialist agents...")

    online_agents = _list_agents_from_registry(session_id)
    if not online_agents:
        return "Error: Could not find any online agents in the registry."

    my_public_url = os.getenv("PUBLIC_URL")

    agent_capabilities = []
    for agent_info in online_agents:
        agent_id = agent_info.get("agent_id")
        url_to_use = _resolve_agent_url(agent_info, my_public_url)
        if not url_to_use or not agent_id:
            continue

        service_name = None
        docker_address = agent_info.get("docker_address")
        if docker_address:
            service_name = urlparse(docker_address).hostname
        
        # Fallback if docker_address is missing (shouldn't happen in your setup)
        if not service_name:
            service_name = agent_info.get("agent_name") # Use friendly name as fallback

        card = None
        cache_key = f"{session_id}__{agent_id}" #Create a session-specific cache key
        # --- 2. Check cache before fetching ---
        if cache_key in AGENT_CARD_CACHE:
            cached_card, timestamp = AGENT_CARD_CACHE[cache_key]
            
            # Check if the cached card is still fresh
            if time.time() - timestamp < AGENT_CARD_TTL_SECONDS:
                logger.info(f"Cache HIT (fresh) for agent card: {agent_id} in session {session_id}")
                card = cached_card
            else:
                logger.info(f"Cache HIT (expired) for agent card: {agent_id}. Re-fetching...")
                # By leaving `card` as None, we trigger the fetch logic below
        if card is None:
            logger.info(f"Cache MISS for agent card: {agent_id} in session {session_id}. Fetching...")
            fetched_card = _get_agent_card_from_url(url_to_use, session_id, service_name)
            if "error" not in fetched_card:
                card = fetched_card
                # --- 3. Store the newly fetched card in the cache ---
                AGENT_CARD_CACHE[cache_key] = (card, time.time())
            else:
                # If fetching fails, skip this agent
                continue
     
        # Create a copy to avoid modifying the cached object
        card_to_return = card.copy()
        # Always set the 'url' to the most efficient one for the current context
        # The LLM will use 'name' for reporting and 'url' for execution
        card_to_return['url'] = url_to_use
        card_to_return['service_name'] = service_name
        card_to_return['friendly_name'] = agent_info.get("agent_name") #just in case

        agent_capabilities.append(card_to_return)

    if not agent_capabilities:
        return "Error: Could not retrieve capability cards from any other online agents."

    return json.dumps(agent_capabilities)

@tool
async def delegate_task_to_agent(
    target_service_name: Annotated[str, "The service name of the agent, e.g., 'travel-acp'"],
    target_agent_url: Annotated[str, "The URL of the agent to delegate the task to."],
    task_query: Annotated[str, "The specific, natural language query to send to the specialist agent."],
    session_id: Annotated[str, "The unique session ID for the current conversation."]
) -> str:
    """
    Sends a task to a specialist agent using the A2A client and waits for its final response.
    This demonstrates interoperability by using the A2A protocol to talk to any agent with a compatible text endpoint.
    """
    logger.info(f"Delegating task '{task_query}' to {target_agent_url} with session {session_id}")

    # --- Report the outgoing tool call ---
    report_content = json.dumps({"query": task_query}, indent=2)
    report_activity(
        session_id=session_id,
        source="coord-a2a",  # agent's name
        target=target_service_name,
        content=report_content,
        msg_type="communication" # Or "tool_call", your choice
    )

    my_public_url = os.getenv('PUBLIC_URL')
    chosen_message_url = _resolve_agent_url(target_agent_url, my_public_url)

    if not chosen_message_url:
        return f"Error: Could not resolve URL for {target_agent_url}"
    
    # The A2ACardResolver needs the base URL, not the full message path.
    # We'll strip common endpoint paths to find the base.
    parsed_url = urlparse(chosen_message_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Check if the last part of the path is a common API endpoint name
    if path_parts and path_parts[-1] in ['messages', 'run', 'invoke']:
        base_path = '/'.join(path_parts[:-1])
        card_discovery_url = parsed_url._replace(path=base_path).geturl()
    else:
        card_discovery_url = chosen_message_url.rstrip('/')
        
    logger.info(f"Using message endpoint: {chosen_message_url}")
    logger.info(f"Derived card discovery URL: {card_discovery_url}")

    # --- Execute the A2A Client Call ---
    try:
        async with httpx.AsyncClient(timeout=300) as client:

            # Use the derived base URL for the resolver
            resolver = A2ACardResolver(
                httpx_client=client, 
                base_url=card_discovery_url,
                llm_client=llm_adapter,
                llm_model_name=openai_model_name 
            )
            agent_card = await resolver.get_agent_card()

            if agent_card.url != chosen_message_url:
                logger.warning(f"Overwriting URL in agent card from '{agent_card.url}' to '{chosen_message_url}' for local efficiency.")
                agent_card.url = chosen_message_url
            
            # Initialize the client with the card, which contains the correct endpoints
            a2a_client = A2AClient(httpx_client=client, agent_card=agent_card)

            message_to_send = Message(
                role=Role.user,
                messageId=str(uuid4()),
                context_id=session_id,
                parts=[Part(root=TextPart(text=task_query))],
            )
            params = MessageSendParams(message=message_to_send, context_id=session_id)
            response_wrapper = await a2a_client.send_message(params)
            
            # ... (rest of your response handling logic)
            response_obj = response_wrapper.root
            if isinstance(response_obj, Message) and response_obj.parts:
                if isinstance(response_obj.parts[0].root, TextPart):
                    return response_obj.parts[0].root.text

            return "Error: Could not understand the agent's response."

    except Exception as e:
        logger.error(f"An exception occurred while talking to agent at {chosen_message_url}: {e}", exc_info=True)
        return f"Error: Failed to communicate with agent at {chosen_message_url}."