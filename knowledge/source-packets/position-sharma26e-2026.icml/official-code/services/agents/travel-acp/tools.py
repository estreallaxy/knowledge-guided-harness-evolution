# /app/acp_travel_agent/tools.py

import os
import json
import uuid
import logging
import httpx
import asyncio
import time

import threading
from datetime import datetime, date as date_obj, timedelta

from typing import Annotated, Dict, Any
from typing import Optional
from urllib.parse import urlparse

# --- CrewAI & LangChain Imports ---
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from crewai.tools import tool
from crewai.crews.crew_output import CrewOutput

# --- ACP Imports ---
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart, Session

# --- Local Imports ---# The key will be the context_id, the value will be a list of messages.
from services.registry.mysql_agent_registry import AgentRegistry
from services.agents.utils import report_activity

logger = logging.getLogger(__name__)
AGENT_CARD_TTL_SECONDS = 30

# This dictionary will store agent cards and TTL, using the agent's id as the key.
AGENT_CARD_CACHE: dict[str, tuple[dict, float]] = {}
AGENT_CARD_CACHE_LOCK = threading.Lock()

# Agent name to pass into the mysql server to note down who made discovery request
AGENT_NAME = "travel-acp" 

# --- Helper Functions ---
# (These are internal to the tools module and not exposed to the agent)

def _list_agents_from_registry(session_id: str) -> list:
    registry = None
    db_config = {'host': os.getenv('DB_HOST'), 'user': os.getenv('DB_USER'), 'password': os.getenv('DB_PASSWORD'), 'database': os.getenv('DB_NAME')}
    try:
        registry = AgentRegistry(db_config=db_config)
        agents = registry.read_from_registry(source_agent=AGENT_NAME, session_id=session_id)
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
    card_url_well_known = f"{agent_url.rstrip('/')}/.well-known/agent"
    try:

        report_activity( # Report the handshake attempt
            session_id=session_id,
            source=AGENT_NAME,
            target=service_name, # Use the clean service name
            content=f"Requesting agent card from {card_url_well_known}",
            msg_type="handshake"
        )

        response = httpx.get(card_url_well_known, timeout=20)
        response.raise_for_status()
        response_dict = response.json() # Parse the JSON content into a dict
        response_json_string = json.dumps(response_dict) # Create a string for logging
        # The other side does not know about handshake, report result
        report_activity( # Report the handshake attempt
            session_id=session_id,
            source=service_name,
            target=AGENT_NAME, # Use the clean service name
            content=response_json_string,
            msg_type="handshake"
        )
        
        return response_dict
    except httpx.TimeoutException:
        logger.error(f"Timeout while fetching agent card from {agent_url}")
        return {"error": f"Request to {agent_url} timed out."}
    except Exception as e:
        logger.error(f"Could not fetch agent card from {agent_url}: {e}")
        return {"error": f"Could not fetch card from {agent_url}"}

def _resolve_agent_url(agent_info: dict) -> Optional[str]:
    """Resolves the most efficient URL (internal Docker > public) for communication."""
    my_public_url = os.getenv("PUBLIC_URL")
    
    # Standardize on these keys, which come from the database
    public_url = agent_info.get("ip_address")
    internal_url = agent_info.get("docker_address")

    if not public_url or (my_public_url and public_url == my_public_url):
        return None

    if internal_url:
        return internal_url
    
    return public_url


def get_amadeus_token() -> str:
    """Gets an authentication token from the Amadeus API."""
    client_id = os.getenv("AMADEUS_API_KEY")
    client_secret = os.getenv("AMADEUS_API_SECRET")
    
    if not client_id or not client_secret:
        return None

    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    
    try:
        response = httpx.post(url, headers=headers, content=payload)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        logger.error(f"Failed to get Amadeus token: {e}")
        return None

# ----------------------------
# Amadeus Fallback Generator
# ----------------------------

def _fallback_fake_flight(origin: str, destination: str, departure_date: str, passengers: int) -> str:
    """
    Generates fake but plausible flight data using the local LLM.
    """
    logger.warning("Amadeus sandbox failed. Generating fake flight data via LLM fallback.")

    model_name = f"openai/{os.getenv('OPENAI_MODEL_NAME')}"
    llm = ChatOpenAI(
        model=model_name,
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    prompt = f"""
    Generate a plausible flight offer in JSON format.
    Requirements:
    - Price in CHF (reasonable, e.g., 80-300 for EU flights).
    - Origin: {origin}
    - Destination: {destination}
    - Departure date: {departure_date}
    - Include departure_time and arrival_time (ISO8601 format).
    - Include airline code and name (e.g., LX for SWISS).
    - Include a flight number.
    - Include a fake booking_link (use google.com/flights).
    - The JSON must have keys: price_chf, origin, destination,
      departure_time, arrival_time, airline, flight_number, booking_link, disclaimer.
    """

    try:
        ai_message_output  = llm.invoke(prompt)
        fake_json_str = ai_message_output.content
        fake_data = json.loads(fake_json_str)
    except Exception as e:
        logger.error(f"LLM fallback failed, returning hardcoded fake flight: {e}")
        fake_data = {
            "price_chf": 120.50,
            "origin": origin,
            "destination": destination,
            "departure_time": f"{departure_date}T08:30:00",
            "arrival_time": f"{departure_date}T10:10:00",
            "airline": "LX",
            "flight_number": "LX123",
            "booking_link": f"https://www.google.com/flights?q=Flights%20from%20{origin}%20to%20{destination}%20on%20{departure_date}",
            "disclaimer": "Amadeus sandbox failed. This is fake demo data."
        }

    # Always append disclaimer
    fake_data["disclaimer"] = (
        fake_data.get("disclaimer", "")
        + " (Note: Amadeus sandbox returned no results, so this is AI-generated demo data.)"
    )

    return json.dumps(fake_data, indent=2)

# ----------------------------
# --- CrewAI Tools ---
# ----------------------------

@tool("Find Flight Information")
#@report_tool_call(tool_name="Amadeus_API", agent_name=AGENT_NAME)
def find_flights(
    origin_iata: Annotated[str, "The IATA code for the origin airport, e.g., 'GVA'."],
    destination_iata: Annotated[str, "The IATA code for the destination airport, e.g., 'BER'."],
    date: Annotated[Optional[str], "The date for the flight, e.g., '2025-10-20'."] = None,
    nr_passengers: Annotated[Optional[int], "Number of adult passangers e.g. 1"] = 1,
    **kwargs
) -> str:
    """
    Finds flight information using the Amadeus API for a given origin and destination.
    Returns JSON with price in CHF, cities, and requires a date. If no nr passangers given assume 1
    """
    session_id = kwargs.get("session_id")

    logger.info(f"[{session_id}] AMADEUS TOOL 'find_flights' called for {origin_iata} -> {destination_iata}, date {date} for number of passangers {nr_passengers}")
    
    report_content = json.dumps({
        "origin_iata": origin_iata, "destination_iata": destination_iata,
        "date": date, "nr_passengers": nr_passengers
    })

    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target="Amadeus_API", # This is a tool
        content=report_content,
        msg_type="tool_call"
    )

    token = get_amadeus_token()
    if not token:
        return "Error: Could not authenticate with Amadeus. Check API credentials."

    departure_date = None
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            today = date_obj.today()
            if parsed_date < today:
                # Roll forward by whole years until it's in the future
                while parsed_date < today:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 1)
                departure_date = parsed_date.isoformat()
                logger.info(f"Provided date '{date}' was in the past. Using next available same-day future date '{departure_date}'.")
            else:
                departure_date = parsed_date.isoformat()
        except (ValueError, TypeError):
            logger.warning(f"Invalid date format '{date}'. Defaulting to 30 days from now.")
            departure_date = (date_obj.today() + timedelta(days=30)).isoformat()
    else:
        # No date provided, use 30 days from now
        departure_date = (date_obj.today() + timedelta(days=30)).isoformat()
        logger.info(f"No date provided, using default future date '{departure_date}'.")

    # Handle argument nr passangers
    passengers_to_use = 1 # Start with a safe default
    if nr_passengers is not None:
        try:
            # Try converting to an integer, which handles cases like the LLM sending "1"
            passengers_to_use = int(nr_passengers)
            if passengers_to_use <= 0:
                logger.warning(f"Received non-positive passenger count ({nr_passengers}). Defaulting to 1.")
                passengers_to_use = 1
        except (ValueError, TypeError):
            # This will catch None, 'null', empty strings, or other non-numeric text
            logger.warning(f"Received invalid value for passengers ('{nr_passengers}'). Defaulting to 1.")
            passengers_to_use = 1

    params = {
        "originLocationCode": origin_iata.upper(),
        "destinationLocationCode": destination_iata.upper(),
        "departureDate": departure_date,
        "adults": passengers_to_use,
        "nonStop": "true",
        "currencyCode": "CHF", # Request price in CHF
        "max": 1 # We only need the top result
    }

    headers = {"Authorization": f"Bearer {token}"}
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def _fallback_handler():
        """ Return standard answer if Amadeus API fails """
        error_result = _fallback_fake_flight(origin_iata, destination_iata, departure_date, passengers_to_use)
        report_activity(
            session_id=session_id,
            source="Amadeus_API",
            target=AGENT_NAME,
            content=error_result,
            msg_type="tool_call"
        )
        return error_result

    try:
        # Find flight
        response = httpx.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            logger.warning(f"Amadeus API found no flights for route {origin_iata}->{destination_iata} on {departure_date}.")
            return _fallback_fake_flight(origin_iata, destination_iata, departure_date, passengers_to_use)

        flight = data["data"][0]
        itinerary = flight['itineraries'][0]['segments'][0]

        # Fetch priced offer
        pricing_url = "https://test.api.amadeus.com/v1/shopping/flight-offers/pricing"
        pricing_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        pricing_payload = {
            "data": {
                "type": "flight-offers-pricing",
                "flightOffers": [flight]
            }
        }

        pricing_response = httpx.post(pricing_url, headers=pricing_headers, json=pricing_payload, timeout=20)
        pricing_response.raise_for_status()
        priced_offer = pricing_response.json()["data"]["flightOffers"][0]

        result_data = {
            "price_chf": float(priced_offer["price"]["total"]),
            "origin": itinerary['departure']['iataCode'],
            "destination": itinerary['arrival']['iataCode'],
            "departure_time": itinerary['departure']['at'],
            "arrival_time": itinerary['arrival']['at'],
            "airline": itinerary['carrierCode'],
            "flight_number": f"{itinerary['carrierCode']}{itinerary['number']}",
            "booking_link": f"https://www.google.com/flights?q=Flights%20from%20{origin_iata}%20to%20{destination_iata}%20on%20{departure_date}",
            "disclaimer": (
                "Price is sourced from Amadeus API (validated via pricing endpoint). "
                "Actual booking price may vary on airline or OTA websites and may exclude extras."
            )
        
        }
        result = json.dumps(result_data, indent=2)
        report_activity(
            session_id=session_id,
            source="Amadeus_API",
            target=AGENT_NAME,
            content=result,
            msg_type="tool_call"
        )
        return result
    except httpx.TimeoutException:
        logger.error(f"Timeout while fetching flight info from Amadeus")
        return {"error": f"Request to either {url} or {pricing_url} timed out."}
    except httpx.HTTPStatusError as e:
        logger.error(f"Amadeus API error: {e}")
        return _fallback_handler()

    except Exception as e:
        logger.error(f"Unexpected error in find_flights: {e}", exc_info=True)
        return _fallback_handler()

@tool("Find Specialist Agent")
def find_specialist_agent(
    task_description: Annotated[str, "A clear description of the task needing a specialist, e.g., 'Convert a currency amount'."],
    **kwargs
) -> str:
    """
    Finds the best specialist agent for a given task by searching the registry
    and reasoning about their capabilities. Returns the agent's full JSON card.
    """
    session_id = kwargs.get("session_id")
    logger.info(f"[{session_id}] Executing tool 'find_specialist_agent' for task: '{task_description}'")
    
    online_agents = _list_agents_from_registry(session_id)
    if not online_agents: return "Error: Could not find any online agents."

    agent_capabilities = []
    with AGENT_CARD_CACHE_LOCK: #Access agent cards cache with lock
        for agent_info in online_agents:
            agent_id = agent_info.get("agent_id")
            public_url = agent_info.get("ip_address") 
            internal_url = agent_info.get("docker_address")

            if not agent_id or not public_url or public_url == os.getenv('PUBLIC_URL'):
                continue

            url_for_discovery = _resolve_agent_url(agent_info)
            if not url_for_discovery:
                continue

            service_name = urlparse(internal_url).hostname if internal_url else agent_info.get("agent_name")
            card = None
            cache_key = f"{session_id}__{agent_id}"
            if cache_key in AGENT_CARD_CACHE:
                cached_card, timestamp = AGENT_CARD_CACHE[cache_key]
                if time.time() - timestamp < AGENT_CARD_TTL_SECONDS:
                    logger.info(f"Cache HIT (fresh) for agent {agent_id} in session {session_id}")
                    card = cached_card
            
            if card is None:
                logger.info(f"Cache MISS for agent {agent_id} in session {session_id}. Fetching...")
                fetched_card = _get_agent_card_from_url(url_for_discovery, session_id, service_name)
                if "error" not in fetched_card:
                    card = fetched_card
                    AGENT_CARD_CACHE[cache_key] = (card, time.time())
                else:
                    continue
            
            # Add the database keys to the card for the next step. This is crucial.
            card_to_return = card.copy()
            card_to_return['ip_address'] = public_url
            card_to_return['docker_address'] = internal_url
            card_to_return['service_name'] = service_name
            agent_capabilities.append(card_to_return)

    if not agent_capabilities: return "Error: Could not retrieve capability cards from any other online agents."

    model_name = f"openai/{os.getenv('OPENAI_MODEL_NAME')}"
    llm = ChatOpenAI(
        model=model_name,
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    chooser_agent = Agent(
        role='Agent Selector',
        goal='Select the single best agent from a list to perform a specific task.',
        backstory='You are a ruthlessly efficient dispatcher.',
        llm=llm,
        verbose=False
    )
    
    chooser_task = Task(
        description=f"""
        Analyze the task description and the list of available agents.
        Task Description: "{task_description}"
        Available Agents JSON: {json.dumps(agent_capabilities, indent=2)}
        Your final answer MUST be ONLY the full JSON object for the single best agent.
        """,
        expected_output="The full JSON object of the chosen agent, and nothing else.",
        agent=chooser_agent
    )
    
    reasoning_crew = Crew(agents=[chooser_agent], tasks=[chooser_task], verbose=False)
    crew_output  = reasoning_crew.kickoff()
    
    chosen_agent_info = None
    if isinstance(crew_output, CrewOutput):
        chosen_agent_info = crew_output.raw
    else:
        chosen_agent_info = crew_output

    logger.info(f"Internal crew chose agent: {chosen_agent_info}")
    return chosen_agent_info if isinstance(chosen_agent_info, str) else json.dumps(chosen_agent_info)


@tool("Delegate Task via ACP")
def delegate_task_via_acp(
    target_agent_card: Annotated[Dict[str, Any], "The URL of the agent to delegate the task to."],
    task_payload: Annotated[str, "A clear, simple, natural language string describing the task for the other agent. Example: 'Convert 130.8 CHF to USD'"],
    **kwargs
) -> str:
    """
    Sends a task to another agent using the ACP client.
    The task_payload MUST be a simple, natural language string, NOT a JSON object.
    """
    session_id = kwargs.get("session_id")

    from .agent import main_event_loop
    
    url_to_use = _resolve_agent_url(target_agent_card)
    if not url_to_use:
        return "Error: Could not determine a valid URL for the target agent."
    
    service_name = target_agent_card.get("service_name", urlparse(url_to_use).hostname)

    logger.info(f"[{session_id}] Delegating task via ACP to {service_name} with payload: '{task_payload}'")
    async def _async_delegate():
        try:
            message_input = Message(parts=[MessagePart(content=task_payload)])
            client_session_id = session_id or str(uuid.uuid4())

            report_activity(
                session_id=session_id,
                source=AGENT_NAME,
                target=service_name,
                content=task_payload,
                msg_type="communication"
            )
            
            timeout = httpx.Timeout(30.0, connect=10.0)
            async with Client(base_url=url_to_use, timeout=timeout).session(Session(id=session_id)) as client:
                run_response = await client.run_sync(agent=None, input=[message_input])
                if run_response.output and run_response.output[0].parts:
                    return run_response.output[0].parts[0].content
                return "Error: Delegated agent returned an empty response."
        except httpx.TimeoutException:
            logger.error(f"Timeout while delegating task to {url_to_use}")
            return f"Error: Request to the delegated agent at {url_to_use} timed out."
        except Exception as e:
            logger.error(f"ACP client failed to delegate task: {e}", exc_info=True)
            return f"Error: ACP client failed to delegate task: {e}"

    # This is the crucial part for calling async code from a sync function (the tool)
    if not main_event_loop:
        return "Error: Main application event loop is not available. Cannot delegate async task."

    # Schedule the async function on the main loop and wait for its result.
    future = asyncio.run_coroutine_threadsafe(_async_delegate(), main_event_loop)
    raw_response = future.result() # This blocks until the async function is done.

    # --- Parse the response to make it cleaner for the agent's memory ---
    try:
        # The currency agent returns a JSON string. We parse it.
        data = json.loads(raw_response)
        # Now, create a clean, human-readable summary of the result.
        from_amount = data.get('original_amount')
        from_curr = data.get('from_currency')
        to_amount = data.get('converted_amount')
        to_curr = data.get('to_currency')
        
        # This clean sentence is what the agent will see as the "Observation".
        return f"Successfully converted {from_amount} {from_curr} to {to_amount} {to_curr}."
    except (json.JSONDecodeError, TypeError, AttributeError):
        # If the response wasn't the JSON we expected (e.g., it was an error message),
        # return it as is.
        return raw_response