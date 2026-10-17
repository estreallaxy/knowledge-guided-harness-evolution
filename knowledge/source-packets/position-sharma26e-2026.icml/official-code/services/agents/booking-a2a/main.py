import logging
import os
import uvicorn
import click
from dotenv import load_dotenv
from collections import deque
import asyncio
import socket
import sys

from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.apps.rest.fastapi_rest_app import A2ARESTAPI, a2a_server_error_handler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCard, AgentSkill, Part, TextPart, AgentCapabilities
from a2a.utils import new_task
from a2a.utils.errors import ServerError
from fastapi import FastAPI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from services.registry.mysql_agent_registry import AgentRegistry
from .graph import booking_agent_graph # Import our compiled graph
from services.agents.utils import SimpleMemoryCache

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_caller_name_from_request(context: RequestContext) -> str:
    """
    Finds the service name of the caller via reverse DNS on its IP.
    """
    default_name = "coord-a2a" # Fallback
    try:
        if hasattr(context, 'raw_request') and context.raw_request:
            # 1. Get the client's IP address from the request
            ip_address = context.raw_request.client.host
            
            # 2. Perform a reverse DNS lookup
            service_name, _, _ = socket.gethostbyaddr(ip_address)
            
            # The name might be fully qualified (e.g., "coord-a2a.my-network")
            # We just want the first part.
            caller_name = service_name.split('.')[0]
            
            logger.info(f"Identified caller IP {ip_address} as service: {caller_name}")
            return caller_name
            
    except Exception as e:
        logger.warning(f"Could not perform reverse DNS on caller's IP: {e}. Defaulting to '{default_name}'")
        
    return default_name

class BookingExecutor(AgentExecutor):
    """
    An AgentExecutor that uses our booking management LangGraph.
    """

    def __init__(self):
        super().__init__()
        # Initialize the in-memory cache for conversation history
        self.memory_cache = SimpleMemoryCache(
            max_size=int(os.getenv("MAX_MEMORIES", 5000)),
            max_conversation_length=int(os.getenv("MAX_CONVERSATION_LENGTH", 100))
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        if not query:
            return

        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            conversation_id = context.message.context_id
            if not conversation_id and hasattr(context, 'raw_request') and context.raw_request:
                 conversation_id = context.raw_request.cookies.get("context_id")

            caller_name = get_caller_name_from_request(context)

            if not conversation_id:
                logger.warning("No context_id found. Memory will not be used.")
                history = []
            else:
                logger.info(f"Using conversation ID for memory: {conversation_id}")
                history = await self.memory_cache.get(conversation_id)

            history.append(HumanMessage(content=query))
            
            initial_state = {"messages": history, "session_id": conversation_id, "caller_name": caller_name}
            final_state = await booking_agent_graph.ainvoke(initial_state)

            final_response_content = "Error: The agent did not produce a final response."
            for msg in reversed(final_state['messages']):
                if isinstance(msg, AIMessage) and msg.content:
                    final_response_content = msg.content
                    break

            if conversation_id:
                await self.memory_cache.set(conversation_id, final_state['messages'])
                logger.info(f"Saved {len(final_state['messages'])} messages for conversation ID: {conversation_id}")

            await updater.add_artifact([Part(root=TextPart(text=final_response_content))])

        except Exception as e:
            logger.error(f"Error executing booking graph: {e}", exc_info=True)
            await updater.add_artifact([Part(root=TextPart(text=f"An internal error occurred: {e}"))])
        finally:
            await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handles task cancellation requests."""
        logger.warning("Cancellation is not supported by this flight booking manager agent.")
        raise ServerError(error=UnsupportedOperationError())

def create_agent_card() -> AgentCard:
    """Creates the static AgentCard from environment variables."""
    public_url = os.getenv('PUBLIC_URL')
    if not public_url:
        logger.critical("PUBLIC_URL environment variable not set. Cannot start agent.")
        sys.exit(1)
        
    return AgentCard(
        name='booking-a2a',
        description='A specialist agent that can create new flight bookings, check the status of existing bookings, and handle cancellations.\n\nUses A2A for agent to agent messaging and Langgraph as its agentic framework',
        url=public_url,
        version='1.1.0',
        capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        skills=[
            AgentSkill(
                id='booking-creation',
                name='Create Flight Booking',
                description='Creates a new flight reservation using details (name, origin, destination, date) provided from a flight search.',
                tags=['booking', 'flights', 'creation', 'transaction'],
                examples=["Please book a flight for Jane Doe from SFO to LAX for 2025-12-25.", "Finalize this booking for John Smith."]
            ),
            AgentSkill(
                id='booking-status',
                name='Check Booking Status',
                description='Checks the status of an existing flight reservation using a last name and booking ID.',
                tags=['booking', 'flights', 'status'],
                examples=["What's the status of booking ID H5J8K2 for last name Doe?"]
            ),
            AgentSkill(
                id='booking-cancellation',
                name='Cancel Flight Booking',
                description='Cancels an existing flight reservation after verifying details and reason.',
                tags=['booking', 'flights', 'cancellation', 'negotiation'],
                examples=["I need to cancel booking H5J8K2 for Doe due to sickness."]
            )
        ]
    )

def register_with_db(agent_card: AgentCard, internal_url: str):
    """Attempts to register the agent with the central database."""
    db_config = {
        'host': os.getenv('DB_HOST'), 'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'), 'database': os.getenv('DB_NAME')
    }
    
    if not all(db_config.values()):
        logger.warning("DB variables not set. Skipping registration.")
        return

    registry = None
    try:
        registry = AgentRegistry(db_config=db_config)
        logger.info(f"Registering agent '{agent_card.name}' ({agent_card.url})")
        registry.write_to_registry(
            agent_id=agent_card.url, # agent_id is the public_url
            agent_name=agent_card.name,
            ip_address=agent_card.url,
            docker_address=internal_url
        )
    except Exception as e:
        logger.error(f"Could not write to agent registry: {e}")
    finally:
        if registry: registry.close_connection()

def create_app(agent_card: AgentCard, request_handler: DefaultRequestHandler) -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(title="A2A Booking Management Agent")
    rest_api = A2ARESTAPI(request_handler=request_handler, agent_card=agent_card)
    # Use the specific ServerError handler, not a generic Exception handler
    app.add_exception_handler(ServerError, a2a_server_error_handler)
    app.include_router(rest_api.router)
    return app

@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=10000, help="Port for the Booking Management Agent.")
def main(host, port):
    """Starts the A2A Booking Management Agent server."""

    # 1. Create Core Components
    agent_card = create_agent_card()
    agent_executor = BookingExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    # 2. Create FastAPI App
    app = create_app(agent_card, request_handler)

    # 3. Register (side-effect)
    register_with_db(agent_card, os.getenv('INTERNAL_URL'))
    
    # 4. Run Server
    logger.info(f"Starting A2A Booking Management Agent on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    main()