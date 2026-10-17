# /app/travel_experiment/acp_agent/acp_agent.py

import os
import sys
import click
import logging
from dotenv import load_dotenv

# Import the server instance from our logic file
from .agent import server

# Import this to ensure tools are registered with CrewAI
from . import tools

from services.registry.mysql_agent_registry import AgentRegistry

# Load environment variables from a .env file
load_dotenv()

# Basic logging setup
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MissingConfigError(Exception):
    """Custom exception for missing configuration."""


@click.command()
@click.option('--host', default='0.0.0.0', help='The host to bind the server to.')
@click.option('--port', default=10000, type=int, help='The port for the server.')
def main(host, port):
    """Starts the ACP Travel Specialist Agent server."""

    # Handle logging
    root_logger = logging.getLogger()
    if root_logger.hasHandlers(): #If handlers already exist, clear them.
        root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO) # Set the level for the root logger.
    handler = logging.StreamHandler(sys.stdout) # Create the handler to send logs to the console

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format) # Create a formatter to define the log message's structure

    handler.setFormatter(formatter) # Set the formatter for the handler
    root_logger.addHandler(handler) # Add the handler to the root logger

    registry = None
    public_url = os.getenv('PUBLIC_URL')
    internal_url = os.getenv('INTERNAL_URL')
    agent_id = public_url

    try:
        
        if not all([os.getenv('OPENAI_API_BASE'), os.getenv('OPENAI_API_KEY'), os.getenv('OPENAI_MODEL_NAME')]):
            raise MissingConfigError('OPENAI_API_BASE, OPENAI_API_KEY, or OPENAI_MODEL_NAME environment variable not set.')
        if not os.getenv('AMADEUS_API_KEY'):
            logger.warning('AMADEUS_API_KEY environment variable not set. Flight searches will likely fail.')

        db_config = {
            'host': os.getenv('DB_HOST'), 'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'), 'database': os.getenv('DB_NAME')
        }
        if all(db_config.values()) and agent_id:
            try:
                registry = AgentRegistry(db_config=db_config)
                agent_name = "ACPTravelSpecialist_CrewAI"
                logger.info(f"Registering agent '{agent_name}' ({agent_id}) with the discovery service...")
                registry.write_to_registry(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    ip_address=public_url,
                    docker_address=internal_url
                )
            except Exception as reg_err:
                logger.error(f"Could not connect to or write to the agent registry: {reg_err}")
        else:
            logger.warning("Database environment variables not fully set or OWN_URL is missing. Skipping registration.")

        logger.info(f"Starting ACP Travel Specialist Agent on http://{host}:{port}")
        # The server object is imported from agent.py and already has the agent registered on it.
        server.run(host=host, port=port)

    except Exception as e:
        logger.error(f"An unexpected error occurred during server startup: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if registry:
            logger.info("Server shutting down. Closing registry connection.")
            registry.close_connection()

if __name__ == '__main__':
    main()