import os
import json
import logging
import sys
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urlunparse
import pathlib
import asyncio
import httpx

import click
from dotenv import load_dotenv

import agora
from agora.receiver.server import ReceiverServer
from agora.receiver.core import Receiver
from agora.common.toolformers.openai import OpenAIToolformer
from agora.receiver.agent_card import AgentCard
from agora.common.toolformers.base import Tool

from services.registry.mysql_agent_registry import AgentRegistry
from services.agents.utils import report_activity

# --- Global Agent Components ---
AGENT_TOOLFORMER: OpenAIToolformer = None
# Overpass API endpoint. It's a public, free service.
OVERPASS_API_URL = "http://overpass-api.de/api/interpreter"
OVERPASS_TOOL_TARGET_NAME = "OverpassAPI"

SESSIONS_DIR = pathlib.Path("/tmp/agora_sessions")

# Agent name to pass into the mysql server to note down who made discovery request
AGENT_NAME = "location-agora" 

# --- Memory management ---
def _ensure_sessions_dir():
    """Ensures the session storage directory exists."""
    SESSIONS_DIR.mkdir(exist_ok=True)

def save_to_session(session_id: str, data: dict):
    """Saves a dictionary of context to a session file."""
    _ensure_sessions_dir()
    session_file = SESSIONS_DIR / f"{session_id}.json"
    try:
        with open(session_file, 'w') as f:
            json.dump(data, f)
        logging.info(f"Saved context for session {session_id}: {data}")
    except IOError as e:
        logging.error(f"Failed to save session data for {session_id}: {e}", exc_info=True)

def load_from_session(session_id: str) -> Optional[dict]:
    """Loads context from a session file."""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        return None
    try:
        with open(session_file, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Failed to load or parse session data for {session_id}: {e}", exc_info=True)
        return None
    
def _get_interest_query_part(interest: str) -> str:
    """
    Helper function to build the efficient Overpass query *part* for a given interest.
    
    Args:
        interest (str): The interest category (e.g., "food", "art_and_history").
        
    Returns:
        str: A string snippet for the Overpass query.
    """
    # Define the specific, efficient tags for each interest
    interest_map = {
        "art_and_history": (
            'node["tourism"~"museum|gallery|artwork"](area.searchArea);'
            'way["tourism"~"museum|gallery|artwork"](area.searchArea);'
            'relation["tourism"~"museum|gallery|artwork"](area.searchArea);'
            'node["historic"](area.searchArea);'
            'way["historic"](area.searchArea);'
            'relation["historic"](area.searchArea);'
        ),
        "modern_architecture": (
            'node["building"~"office|commercial|public|university|modern"](area.searchArea);'
            'way["building"~"office|commercial|public|university|modern"](area.searchArea);'
            'relation["building"~"office|commercial|public|university|modern"](area.searchArea);'
            'node["architecture"~"modern|contemporary"](area.searchArea);'
            'way["architecture"~"modern|contemporary"](area.searchArea);'
            'relation["architecture"~"modern|contemporary"](area.searchArea);'
        ),
        "food": (
            'node["amenity"~"restaurant|cafe|bar|pub|fast_food|food_court"](area.searchArea);'
            'way["amenity"~"restaurant|cafe|bar|pub|fast_food|food_court"](area.searchArea);'
            'relation["amenity"~"restaurant|cafe|bar|pub|fast_food|food_court"](area.searchArea);'
        ),
        "nature": (
            'node["leisure"~"park|nature_reserve|garden|common"](area.searchArea);'
            'way["leisure"~"park|nature_reserve|garden|common"](area.searchArea);'
            'relation["leisure"~"park|nature_reserve|garden|common"](area.searchArea);'
            'node["natural"~"wood|tree|grassland|water"](area.searchArea);'
            'way["natural"~"wood|tree|grassland|water"](area.searchArea);'
            'relation["natural"~"wood|tree|grassland|water"](area.searchArea);'
        )
    }

    # Get the specific query part for the interest
    query_part = interest_map.get(interest.lower())

    # Fallback to the original slow query if the interest is not recognized
    if not query_part:
        logging.warning(f"No specific tags found for interest '{interest}'. Using slow regex search.")
        # Sanitize interest for regex
        sanitized_interest = interest.replace('"', '\\"').replace("'", "\\'")
        query_part = (
            f'node["name"~".*{sanitized_interest}.*"](area.searchArea);'
            f'way["name"~".*{sanitized_interest}.*"](area.searchArea);'
            f'relation["name"~".*{sanitized_interest}.*"](area.searchArea);'
            f'node["amenity"~".*{sanitized_interest}.*"](area.searchArea);'
            f'way["amenity"~".*{sanitized_interest}.*"](area.searchArea);'
            f'relation["amenity"~".*{sanitized_interest}.*"](area.searchArea);'
        )
    
    return query_part

def evaluate_city_for_interest(session_id: str, city_name: str, interest: str) -> str:
    """
    Evaluates how well a city matches a given interest by counting relevant points of interest.

    Args:
        session_id (str): The unique ID for the user's conversation session.
        city_name (str): The name of the city to evaluate (e.g., "Berlin").
        interest (str): The interest category. Supported interests are: art_and_history, modern_architecture, food, nature.
    """
    logging.info(f"Tool 'evaluate_city_for_interest' selected for city: '{city_name}', interest: '{interest}'")

    save_to_session(session_id, {"last_city_evaluated": city_name, "last_interest": interest})
    
    # Sanitize city name
    sanitized_city = city_name.replace('"', '\\"').replace("'", "\\'")
    
    # Get the new, efficient query part
    query_part = _get_interest_query_part(interest)

    # Build the full query for *counting*
    query = f"""
    [out:json][timeout:60];
    area[name="{sanitized_city}"]->.searchArea;
    (
      {query_part}
    );
    out count;
    """

    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target=OVERPASS_TOOL_TARGET_NAME,
        content=query,
        msg_type="tool_call"
    )

    try:
        response = httpx.post(OVERPASS_API_URL, data={'data': query}, timeout=60)
        response.raise_for_status()
        data = response.json()
        # The count is available in the 'total' field of the 'tags' object
        count = int(data.get("elements", [{}])[0].get("tags", {}).get("total", 0))

        # A simple scoring heuristic. More results = higher score. Capped at 10.
        score = min(10, count // 10) 
        
        result = {"city": city_name, "interest": interest, "poi_count": count, "score": score}
        result_str = json.dumps(result)
        logging.info(f"Evaluation result: {result}")
        
        report_activity(
            session_id=session_id,
            source=OVERPASS_TOOL_TARGET_NAME,
            target=AGENT_NAME,
            content=result_str,
            msg_type="tool_call"
        )
        return result_str

    except Exception as e:
        error_str = f"Error: Could not retrieve or parse data for {city_name}. Reason: {e}"
        logging.error(f"Tool 'evaluate_city_for_interest' failed: {e}")
        
        report_activity(
            session_id=session_id,
            source=OVERPASS_TOOL_TARGET_NAME,
            target=AGENT_NAME,
            content=error_str,
            msg_type="tool_call"
        )
        return error_str


def create_itinerary(session_id: str, budget: float, city_name: Optional[str] = None, interest: Optional[str] = None) -> str:
    """
    Creates a simple 2-day itinerary. If city_name or interest are not provided, it uses the last evaluated ones from memory.

    Args:
        session_id (str): The unique ID for the user's conversation session.
        budget (float): The budget for activities.
        city_name (Optional[str]): The name of the city. Tries to load from memory if not given.
        interest (Optional[str]): The interest category. Tries to load from memory if not given.
    """
    logging.info(f"Tool 'create_itinerary' selected for city: '{city_name}', budget: {budget}")

    try:
        budget = float(budget)
    except (ValueError, TypeError):
        return "Error: The provided budget is not a valid number. Please provide a number like 400 or 250.50."

    if city_name is None or city_name.lower() == 'none' or interest is None or interest.lower() == 'none':
        logging.info("City or interest not provided, attempting to load from session memory...")
        session_data = load_from_session(session_id)
        if not session_data:
            return "Error: I don't have a city in memory. Please evaluate a city first."
        
        # Only overwrite if the original value was None or 'none'
        if city_name is None or city_name.lower() == 'none':
            city_name = session_data.get("last_city_evaluated")
        if interest is None or interest.lower() == 'none':
            interest = session_data.get("last_interest")
        
        if not city_name or not interest:
            return "Error: Could not find city or interest in memory. Please be more specific."
    
    # Sanitize city name
    sanitized_city = city_name.replace('"', '\\"').replace("'", "\\'")

    # Get the new, efficient query part
    query_part = _get_interest_query_part(interest)

    # Build the full query for *getting locations*
    query = f"""
    [out:json][timeout:60];
    area[name="{sanitized_city}"]->.searchArea;
    (
      {query_part}
    );
    out body 5;
    """

    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target=OVERPASS_TOOL_TARGET_NAME,
        content=query,
        msg_type="tool_call"
    )

    try:
        response = httpx.post(OVERPASS_API_URL, data={'data': query}, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        locations = sorted(list(set(el.get("tags", {}).get("name") for el in data.get("elements", []) if el.get("tags", {}).get("name"))))
        
        if not locations:
            return f"I couldn't find any specific locations for '{interest}' in {city_name}."
        locations_list_str = "\n".join([f"- {loc}" for loc in locations])
        
        final_message = f"Here are some places to consider for '{interest}' in {city_name}:\n\n{locations_list_str}"

        report_activity(
            session_id=session_id,
            source=OVERPASS_TOOL_TARGET_NAME,
            target=AGENT_NAME,
            content=final_message,
            msg_type="tool_call"
        )

        return final_message

    except Exception as e:
        error_str = f"Error: Could not retrieve itinerary data for {city_name}. Reason: {e}"
        logging.error(f"API request failed for itinerary in '{city_name}': {e}")
        report_activity(
            session_id=session_id,
            source=OVERPASS_TOOL_TARGET_NAME,
            target=AGENT_NAME,
            content=error_str,
            msg_type="tool_call"
        )
        return error_str
    

# --- Server Startup Logic ---
@click.command()
@click.option('--host', default='0.0.0.0', help='Host to run the agent on.')
@click.option('--port', type=int, required=True, help='Port to run the agent on.')
def main(host, port):
    """Starts the Agora Atlas (Local Guru) Agent server."""
    global AGENT_TOOLFORMER
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    registry = None
    public_url = os.getenv('PUBLIC_URL')
    internal_url = os.getenv('INTERNAL_URL')
    agent_id = public_url

    try:
        openai_api_base = os.getenv('OPENAI_API_BASE')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        openai_model_name = os.getenv('OPENAI_MODEL_NAME')
        
        if not all([openai_api_base, openai_api_key, openai_model_name]):
            logging.error("OPENAI_API_BASE, OPENAI_API_KEY, or OPENAI_MODEL_NAME not set.")
            return
        
        AGENT_TOOLFORMER = OpenAIToolformer(
            model=openai_model_name,
            api_key=openai_api_key,
            base_url=openai_api_base
        )

        raw_tools = [evaluate_city_for_interest, create_itinerary]

        agora_tools = [Tool.from_toollike(t) for t in raw_tools]

        # Continue as before, using the wrapped 'tools' list.
        card = AgentCard(
            name=AGENT_NAME,
            description="An agent that knows about local events, attractions, and points of interest. It can evaluate cities based on interests and create simple travel itineraries.\n\nUses Agora for agent to agent messaging but no agentic framework",
            tools=agora_tools, # Pass the wrapped tools
            version="1.0.0",
            url=public_url
        )
        
        # Subclass for Agora Receiver that does reporting
        receiver = Receiver.make_default(
            toolformer=AGENT_TOOLFORMER,
            tools=agora_tools, # Pass the wrapped tools
            agent_card=card
        )
        
        server = ReceiverServer(receiver)

        # Database registration logic 
        db_connection_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
        }
        
        if all(db_connection_config.values()) and agent_id:
            try:
                registry = AgentRegistry(db_config=db_connection_config)
                logging.info(f"Registering agent '{card.name}' ({agent_id}) with the discovery service...")
                registry.write_to_registry(
                    agent_id=agent_id,
                    agent_name=card.name,
                    ip_address=public_url,
                    docker_address=internal_url
                )
            except Exception as reg_err:
                logging.error(f"Could not connect to or write to the agent registry: {reg_err}")
        else:
            logging.warning("Database environment variables not fully set or OWN_URL is missing. Skipping registration.")

        logging.info(f"Starting {AGENT_NAME} Agent on http://{host}:{port}")
        server.run(host=host, port=port)

    except Exception as e:
        logging.error(f"An unexpected error occurred during server startup: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if registry:
            logging.info("Server shutting down. Closing registry connection.")
            registry.close_connection()

if __name__ == '__main__':
    main()