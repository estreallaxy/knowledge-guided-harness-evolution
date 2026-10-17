# /app/travel_experiment/a2a_coordinator_agent/run_server.py

import logging
import os
import sys
import uvicorn
import click
from dotenv import load_dotenv
from collections import deque
import asyncio
import uuid

from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.utils.errors import ServerError
from a2a.server.apps.rest.fastapi_rest_app import A2ARESTAPI, a2a_server_error_handler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCard, AgentSkill, Part, TextPart, Task, AgentCapabilities, UnsupportedOperationError
from a2a.utils import new_task
from fastapi import FastAPI
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage

from services.registry.mysql_agent_registry import AgentRegistry
from .graph import coordinator_graph # Import our compiled LangGraph
from services.agents.utils import SimpleMemoryCache

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def summarize_conversation(messages: list[BaseMessage]) -> list[str]:
    """
    Converts a list of LangChain message objects into a simple, readable
    list of strings for display.
    """
    summary = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            summary.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage):
            # If the AI message has tool calls, we often care more about the final text content.
            # For now, we'll just show the text response.
            if msg.content:
                 summary.append(f"Agent: {msg.content}")
        elif isinstance(msg, ToolMessage):
            # Find the original tool call to get the tool's name
            tool_name = "Unknown Tool"
            for prev_msg in reversed(messages):
                if isinstance(prev_msg, AIMessage) and prev_msg.tool_calls:
                    for tool_call in prev_msg.tool_calls:
                        if tool_call.get("id") == msg.tool_call_id:
                            tool_name = tool_call.get("name")
                            break
                if tool_name != "Unknown Tool":
                    break
            summary.append(f"Tool ({tool_name}): {msg.content}")
    return summary

class CoordinatorExecutor(AgentExecutor):
    """
    An AgentExecutor that uses a compiled LangGraph to process requests.
    """
    def __init__(self):
        super().__init__()
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
            # --- MEMORY IMPLEMENTATION ---
            # Get the conversation ID from the request context.
            conversation_id = context.message.context_id
            if not conversation_id and hasattr(context, 'raw_request') and context.raw_request:
                conversation_id = str(uuid.uuid4())
                logger.warning(f"No context_id found. Created a new one: {conversation_id}")
            logger.info(f"Using conversation ID for memory: {conversation_id}")
            history = await self.memory_cache.get(conversation_id)

            # 2. Add the new user message to the history.
            history.append(HumanMessage(content=query))
            
            # 3. Invoke the graph with the FULL conversation history.
            initial_state = {"messages": history, "session_id": conversation_id}
            final_state = await coordinator_graph.ainvoke(initial_state)

            # The final response is the content of the last message in the graph's state.
            if final_state and 'messages' in final_state:
                last_message = final_state['messages'][-1]
                final_response_content = last_message.content
                if conversation_id:
                    await self.memory_cache.set(conversation_id, final_state['messages'])
                    logger.info(f"Saved {len(final_state['messages'])} messages for conversation ID: {conversation_id}")
            else:        
                final_response_content = "Error: The agent did not produce a final state."

            if final_response_content:
                await updater.add_artifact([Part(root=TextPart(text=final_response_content))])

        except Exception as e:
            logger.error(f"Error executing coordinator graph: {e}", exc_info=True)
            await updater.add_artifact([Part(root=TextPart(text=f"An internal error occurred: {e}"))])
        finally:
            await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handles task cancellation requests."""
        logger.warning("Cancellation is not supported by this coordinator agent.")
        raise ServerError(error=UnsupportedOperationError())

# --- Encapsulated Setup Functions ---

def create_agent_card() -> AgentCard:
    """Creates the static AgentCard from environment variables."""
    public_url = os.getenv('PUBLIC_URL')
    if not public_url:
        logger.critical("PUBLIC_URL environment variable not set. Cannot start agent.")
        sys.exit(1)
        
    return AgentCard(
        name='A2ACoordinatorAgent',
        description='A master agent that can discover agents and coordinate tasks with them',
        url=public_url,
        version='1.0.0',
        capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        skills=[
            AgentSkill(
                id='trip-planning',
                name='Full Trip Planning',
                description='Can handle complex user queries for trip planning by breaking them down and delegating to other agents.',
                tags=['planning', 'coordination', 'travel', 'multi-agent'],
                examples=["Plan a trip to Berlin for someone interested in art, and find me the cheapest flight from Geneva."]
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

    def summarize_conversation(messages: list[BaseMessage]) -> list[str]:
        """
        Converts a list of LangChain message objects into a simple, readable
        list of strings for display. (Helper for /memory endpoint)
        """
        summary = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                summary.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                if msg.content:
                    summary.append(f"Agent: {msg.content}")
            elif isinstance(msg, ToolMessage):
                tool_name = "Unknown Tool"
                for prev_msg in reversed(messages):
                    if isinstance(prev_msg, AIMessage) and prev_msg.tool_calls:
                        for tool_call in prev_msg.tool_calls:
                            if tool_call.get("id") == msg.tool_call_id:
                                tool_name = tool_call.get("name")
                                break
                        if tool_name != "Unknown Tool":
                            break
                summary.append(f"Tool ({tool_name}): {msg.content}")
        return summary
    
    app = FastAPI(title="A2A Coordinator Agent")
    rest_api = A2ARESTAPI(request_handler=request_handler, agent_card=agent_card)
    app.add_exception_handler(ServerError, a2a_server_error_handler)
    app.include_router(rest_api.router)

    # Debugging to view memory
    @app.get("/memory")
    async def get_memory():
        """Debug endpoint to view conversation memory."""
        # Access the memory cache from the request handler
        executor = request_handler.agent_executor
        readable_memory = {
            conv_id: summarize_conversation(messages)
            for conv_id, messages in executor.memory_cache.store.items()
        }
        return readable_memory
    
    return app

@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=10000)
def main(host, port):
    """Starts the A2A Coordinator Agent server."""
    # 1. Create Core Components
    agent_card = create_agent_card()
    agent_executor = CoordinatorExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    # 2. Create FastAPI App
    app = create_app(agent_card, request_handler)

    # 3. Register (side-effect)
    register_with_db(agent_card, os.getenv('INTERNAL_URL'))
    
    # 4. Run Server
    logger.info(f"Starting A2ACoordinatorAgent on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    main()