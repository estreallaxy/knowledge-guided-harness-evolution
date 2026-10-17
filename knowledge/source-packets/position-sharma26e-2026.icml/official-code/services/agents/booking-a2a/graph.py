import os
import json
import logging
import random
import string
from typing import List, TypedDict, Annotated
import operator
from dateutil.parser import parse as parse_date

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END

from services.agents.utils import report_activity #For reporting tool calls to demo

logger = logging.getLogger(__name__)
# Get the directory where this script (graph.py) is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Join that directory with the filename to create a full, reliable path
BOOKINGS_FILE = os.path.join(SCRIPT_DIR, "flight_bookings.json")
MAX_BOOKING_RECORDS = 5000
EVICTION_BATCH_SIZE = 100

AGENT_NAME = "booking-a2a"
TOOL_TARGET_NAME = "Flight_Bookings_DB"


CITY_TO_IATA = {
    "GENEVA": "GVA", "AMSTERDAM": "AMS", "PARIS": "CDG", "NEW YORK": "JFK",
    "LONDON": "LHR", "DUBAI": "DXB", "BERLIN": "BER", "SAN FRANCISCO": "SFO",
    "LOS ANGELES": "LAX",
}

def _standardize_airport_code(location: str) -> str:
    """Converts a location name to its IATA code if possible."""
    # If the input is already a 3-letter IATA code, assume it's correct.
    if isinstance(location, str) and len(location) == 3 and location.isupper():
        return location
    # Otherwise, look it up in our map.
    return CITY_TO_IATA.get(location.upper(), location)

def _standardize_date(date_string: str) -> str:
    """Converts various date strings to YYYY-MM-DD format."""
    try:
        # The fuzzy=True flag helps parse strings like "the 20th of August"
        parsed_dt = parse_date(date_string, fuzzy=True)
        return parsed_dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        # If parsing fails, return the original string for the agent to handle.
        logging.warning(f"Could not parse date string: {date_string}")
        return date_string

# --- 1. Tools for Booking Management ---

def _read_bookings():
    """Helper function to read the JSON database. Generates the file if missing."""
    # 1. If the file doesn't exist, create it with an empty list
    if not os.path.exists(BOOKINGS_FILE):
        try:
            logger.info(f"Bookings file not found. Creating a new one at {BOOKINGS_FILE}")
            _write_bookings([])
            return []
        except Exception as e:
            logger.error(f"Failed to initialize bookings file: {e}")
            return []

    # 2. Try to read the existing file
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file exists but contains corrupted/malformed JSON, reset it safely
        logger.warning(f"Malformed JSON in {BOOKINGS_FILE}. Resetting database.")
        _write_bookings([])
        return []
    except Exception as e:
        logger.error(f"Error reading bookings file: {e}")
        return []

def _write_bookings(data):
    """Helper function to write to the JSON database."""
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def _generate_booking_id(length=6):
    """Generates a random alphanumeric booking ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@tool
def make_booking(first_name: str, last_name: str, origin: str, destination: str, flight_date: str, **kwargs) -> str:
    """
    Creates a new flight booking and saves it to the database.
    Requires the user's first and last name, and the flight's origin, destination, and date.
    """

    session_id = kwargs.get("session_id")
    report_content = json.dumps({
        "first_name": first_name, "last_name": last_name, "origin": origin,
        "destination": destination, "flight_date": flight_date
    })
    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target=TOOL_TARGET_NAME,
        content=report_content,
        msg_type="tool_call"
    )

    logging.info(f"Tool 'make_booking' called with raw inputs: {origin}, {destination}, {flight_date}")
    
    std_origin = _standardize_airport_code(origin)
    std_destination = _standardize_airport_code(destination)
    std_flight_date = _standardize_date(flight_date)

    logging.info(f"Standardized inputs to: {std_origin}, {std_destination}, {std_flight_date}")

    if len(std_origin) != 3 or len(std_destination) != 3:
        logger.warning(f"Either the origin or destination airport was not given as correct 3-letter code")

    bookings = _read_bookings()

    # FIFO logic for existing bookings. Evict the oldest records when full
    if len(bookings) >= MAX_BOOKING_RECORDS:
        # Calculate how many to remove. We take the oldest records from the start of the list.
        records_to_remove = EVICTION_BATCH_SIZE
        logger.warning(
            f"Booking limit ({MAX_BOOKING_RECORDS}) reached. Evicting {records_to_remove} oldest records."
        )
        # This keeps all records *except* for the first EVICTION_BATCH_SIZE items
        bookings = bookings[records_to_remove:]


    new_booking = {
        "booking_id": _generate_booking_id(),
        "last_name": last_name,
        "first_name": first_name,
        "origin": std_origin,
        "destination": std_destination,
        "flight_date": std_flight_date,
        "status": "CONFIRMED"
    }
    
    bookings.append(new_booking)
    _write_bookings(bookings)
    
    response_content = f"Success! A new booking has been created with Booking ID: {new_booking['booking_id']}. Please save this ID for your records."
    report_activity(
        session_id=session_id,
        source=TOOL_TARGET_NAME,
        target=AGENT_NAME,
        content=response_content,
        msg_type="tool_call"
    )
    return response_content


@tool
def get_booking_status(last_name: str, booking_id: str, **kwargs) -> str:
    """
    Finds a specific flight booking by last name and booking ID to check its status.
    """
    session_id = kwargs.get("session_id")
    report_content = json.dumps({"last_name": last_name, "booking_id": booking_id})
    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target=TOOL_TARGET_NAME,
        content=report_content,
        msg_type="tool_call"
    )

    logger.info(f"Tool 'get_booking_status' called for {last_name}, {booking_id}")
    bookings = _read_bookings()
    booking_id = booking_id.upper()

    response_content = "Error: No matching booking was found. Please check the last name and booking ID."
    for booking in bookings:
        if booking.get("last_name").lower() == last_name.lower() and booking.get("booking_id").upper() == booking_id:
            response_content = json.dumps(booking)
            break
            
    report_activity(
        session_id=session_id,
        source=TOOL_TARGET_NAME,
        target=AGENT_NAME,
        content=response_content,
        msg_type="tool_call"
    )
    return response_content


@tool
def cancel_booking(booking_id: str, reason: str, **kwargs) -> str:
    """
    Marks a booking as 'CANCELLED' in the database after a valid reason is given.
    Requires the booking_id and the reason for cancellation.
    """
    session_id = kwargs.get("session_id")
    report_content = json.dumps({"booking_id": booking_id, "reason": reason})
    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target=TOOL_TARGET_NAME,
        content=report_content,
        msg_type="tool_call"
    )

    logger.info(f"Tool 'cancel_booking' called for {booking_id} due to '{reason}'")
    bookings = _read_bookings()
    booking_id = booking_id.upper()
    booking_found = False

    response_content = f"Error: Could not find booking {booking_id} to cancel."
    for booking in bookings:
        if booking.get("booking_id").upper() == booking_id:
            if booking.get("status") == "CANCELLED":
                response_content = f"Error: This booking ({booking_id}) has already been cancelled."
                booking_found = True # So we don't write to file
                break
            booking['status'] = 'CANCELLED'
            booking_found = True
            response_content = f"Success: Booking {booking_id} has been marked as cancelled."
            break
    
    if booking_found:
        _write_bookings(bookings)
    
    report_activity(
        session_id=session_id,
        source=TOOL_TARGET_NAME,
        target=AGENT_NAME,
        content=response_content,
        msg_type="tool_call"
    )
    return response_content


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    session_id: str
    caller_name: str

tools = [make_booking, get_booking_status, cancel_booking]
tool_map = {tool.name: tool for tool in tools}


async def agent_node(state: AgentState, llm):
    """The node that contains the agent's core logic and decides the next action."""
    session_id = state.get("session_id")
    system_message = """
    You are the "Booking Management Agent" for an airline. Your role is to manage the flight booking lifecycle: creating, checking status, and cancelling. You DO NOT search for flights.

    **General Rules:**
    - First, determine the user's intent (book, check status, or cancel).
    - Politely ask for any missing information required for the task. Do not proceed until you have all necessary details.

    **Workflow 1: Creating a New Booking**
    Your primary purpose for booking is to finalize a reservation using given flight details.
    1.  To create a booking, you need: `first_name`, `last_name`, `origin`, `destination`, and `flight_date`. These details are provided to you by the user.
    2.  Once you have all five pieces of information, your ONLY next action is to call the `make_booking` tool.
    3.  After the tool succeeds, present the confirmation message and the new booking ID to the user.

    **Workflow 2: Checking Booking Status**
    1.  To check a status, you need: `last_name` and `booking_id`.
    2.  Once you have both, your ONLY next action is to call the `get_booking_status` tool.
    3.  After the tool returns the booking details, summarize them for the user (e.g., "Your flight from GVA to AMS on 2025-09-15 is CONFIRMED.").

    **Workflow 3: Cancelling a Booking**
    1.  First, identify the booking. You need `last_name` and `booking_id`.
    2.  Once you have both, call the `get_booking_status` tool to verify the booking.
    3.  If the tool finds the booking and it is not already cancelled, you MUST then ask the user for the reason for the cancellation.
    4.  Evaluate the reason. VALID reasons are 'sickness', 'family emergency', 'death'. INVALID reasons are 'changed my mind', etc.
    5.  If the reason is VALID, your ONLY next action is to call the `cancel_booking` tool. Then, confirm the cancellation and refund to the user.
    6.  If the reason is INVALID, DO NOT call any tools. Politely decline the full refund, offer a travel voucher, and end the conversation.

    **Error Handling:**
    - If any tool returns an error, report that specific error to the user and stop.
    """
    messages_for_llm = [SystemMessage(content=system_message)] + state["messages"]
    response = await llm.ainvoke(messages_for_llm)
    return {"messages": [response]}

async def tool_node(state: AgentState):
    """This node executes the tools chosen by the agent."""
    last_message = state["messages"][-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": [ToolMessage(content="Error: Tool node reached without a valid tool call.", tool_call_id="error")]}
        
    tool_calls = last_message.tool_calls
    tool_messages = []
    session_id = state.get("session_id")
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")
        
        # Inject the session_id into the tool's arguments
        tool_args["session_id"] = session_id 

        if tool_name in tool_map:
            try:
                # Use .invoke() for synchronous tools
                output = tool_map[tool_name].invoke(tool_args)
                tool_messages.append(ToolMessage(content=str(output), tool_call_id=tool_call_id))
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                tool_messages.append(ToolMessage(content=f"ERROR EXECUTING TOOL: {e}", tool_call_id=tool_call_id))
        else:
            tool_messages.append(ToolMessage(content=f"Error: Non-existent tool '{tool_name}' called.", tool_call_id=tool_call_id))
    return {"messages": tool_messages}

def should_continue(state: AgentState):
    """Router: decides whether to continue calling tools or to finish."""
    last_message = state["messages"][-1]
    # If the last message is a ToolMessage, we should continue
    if isinstance(last_message, ToolMessage):
        return "agent"
    # If the last message is not a ToolMessage but has tool calls, we should continue
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # Otherwise, we're done
    session_id = state.get("session_id")
    if session_id and isinstance(last_message, AIMessage) and last_message.content:
        caller = state.get("caller_name", "coord-a2a") # Replies to the coordinator (I hope)
        report_activity(
            session_id=session_id,
            source=AGENT_NAME,
            target=caller, 
            content=last_message.content,
            msg_type="communication"
        )
    return "end"

def create_booking_agent_graph() -> StateGraph:
    """Builds and returns the LangGraph."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME"),
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    llm_with_tools = llm.bind_tools(tools)

    async def runnable_agent_node(state: AgentState):
        return await agent_node(state, llm_with_tools)
    
    graph = StateGraph(AgentState)
    # Add the new awaitable wrapper function as the node
    graph.add_node("agent", runnable_agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    
    return graph.compile()

booking_agent_graph = create_booking_agent_graph()