import mysql.connector
from mysql.connector import errorcode
import os
import logging
from datetime import datetime, timezone
import requests
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Basic logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- REPORTING-TO-VISUALIZER ---
# Helper function to send database activity to the visualizer endpoint.
# This keeps the reporting logic separate and reusable.
VISUALIZER_ENDPOINT = os.getenv('VISUALIZER_ENDPOINT', "http://collector:8765/data")

def report_activity(source: str, target: str, content: str, msg_type: str = "discovery", session_id: Optional[str] = None):
    """Sends a standardized message to the visualizer endpoint."""
    # Only send reports that are part of a session
    if not session_id:
        logger.warning(f"report_activity called with no session_id. Dropping. Source: {source}")
        return

    data = {
        "session_id": session_id,
        "source": source,
        "target": target,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": msg_type
    }
    try:
        requests.post(VISUALIZER_ENDPOINT, json=data, timeout=20)
    except requests.exceptions.RequestException as e:
        # We log a warning but don't crash the main application if the visualizer is down.
        logger.warning(f"Could not report activity to visualizer: {e}")

class AgentRegistry:
    """
    Manages agent discoverability by writing to and reading from a MySQL database.
    
    This class handles the connection to the database and provides simple methods
    for registering agents and listing active agents.
    """

    def __init__(self, db_config: Dict[str, Any]):
        """
        Initializes the registry and connects to the MySQL database.

        Args:
            db_config (Dict[str, Any]): A dictionary with connection details,
                                        e.g., {'host': 'localhost', 'user': 'root', ...}
        """
        self.db_config = db_config
        self.connection = None
        try:
            # Establish the database connection
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info("Successfully connected to MySQL database.")
            # Ensure the necessary table exists for storing agent data
            self._create_table_if_not_exists()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error("Database does not exist")
            else:
                logger.error(f"Failed to connect to MySQL: {err}")
            # If connection fails, we can't proceed.
            raise

    def _create_table_if_not_exists(self):
        """
        Checks if the 'agents' table exists and creates it if it doesn't.
        This makes the class self-sufficient on first run.
        """
        if not self.connection:
            logger.error("Cannot create table, no database connection.")
            return

        cursor = self.connection.cursor()
        table_name = 'agents'
        try:
            logger.info(f"Checking if table '{table_name}' exists...")
            # This SQL statement creates the table.
            # - agent_id is the PRIMARY KEY, which must be unique.
            # - last_seen will automatically update to the current time whenever
            #   the row is modified. This is great for heartbeats.
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                agent_id VARCHAR(255) NOT NULL PRIMARY KEY,
                agent_name VARCHAR(255) NOT NULL,
                ip_address VARCHAR(255) NOT NULL,
                docker_address VARCHAR(255) NULL,
                last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            logger.info(f"Table '{table_name}' is ready.")
        except mysql.connector.Error as err:
            logger.error(f"Failed to create table '{table_name}': {err.msg}")
        finally:
            cursor.close()

    def write_to_registry(self, agent_id: str, agent_name: str, ip_address: str, docker_address: Optional[str] = None):
        """
        Registers an agent or updates its information if it already exists.

        This method performs an "upsert" operation. If the agent_id is new,
        it inserts a new row. If the agent_id already exists, it updates the
        name, IP address, and 'last_seen' timestamp.

        Args:
            agent_id (str): The unique identifier for the agent (e.g., a UUID).
            agent_name (str): The human-readable name of the agent.
            ip_address (str): The IP address where the agent can be reached.
        """
        if not self.connection:
            logger.error("Cannot write to registry, no database connection.")
            return

        cursor = self.connection.cursor()
        # This is an "INSERT ... ON DUPLICATE KEY UPDATE" statement.
        # It's a very efficient way to handle both creation and updates.
        # Using placeholders (%s) is crucial to prevent SQL injection attacks.
        upsert_query = """
        INSERT INTO agents (agent_id, agent_name, ip_address, docker_address, last_seen)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            agent_name = VALUES(agent_name),
            ip_address = VALUES(ip_address),
            docker_address = VALUES(docker_address),
            last_seen = VALUES(last_seen);
        """
        try:
            # The current time is passed for the 'last_seen' column.
            current_time = datetime.utcnow()
            
            #This event is not logged, as it is globally meaningful for all users
            #log_content = upsert_query % (agent_id, agent_name, ip_address, docker_address, str(current_time))
            #report_activity(
            #    source=agent_name,
            #    target="mysql-registry",
            #    content=log_content
            #)

            # The values are passed as a tuple to the execute method.
            cursor.execute(upsert_query, (agent_id, agent_name, ip_address, docker_address, current_time))
            self.connection.commit()
            logger.info(f"Successfully registered/updated agent '{agent_name}' ({agent_id}).")
        except mysql.connector.Error as err:
            logger.error(f"Failed to write to registry: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def read_from_registry(self, age_limit_seconds: Optional[int] = None, source_agent: str = "Application", session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Reads the list of all registered agents from the database.

        Args:
            age_limit_seconds (Optional[int]): If provided, only returns agents
                that have been seen within this many seconds. Defaults to None (all agents).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents a registered agent.
        """
        if not self.connection:
            logger.error("Cannot read from registry, no database connection.")
            return []

        # Using a dictionary cursor makes it easy to get results as dicts.
        cursor = self.connection.cursor(dictionary=True)
        
        query = "SELECT agent_id, agent_name, ip_address, docker_address, last_seen FROM agents"
        params = None

        if age_limit_seconds:
            # Add a WHERE clause to filter by the last_seen timestamp.
            query += " WHERE last_seen >= NOW() - INTERVAL %s SECOND"
            params = (age_limit_seconds,)

        try:
            # Report request
            log_content = query % params if params else query
            report_activity(
                source=source_agent,
                target="mysql-registry",
                content=log_content,
                session_id=session_id
            )

            cursor.execute(query, params)
            agents = cursor.fetchall()

            # Report response
            report_activity(
                source="mysql-registry",
                target=source_agent,
                content=f"Returned records about {len(agents)} agent(s).",
                session_id=session_id
            )

            logger.info(f"Successfully read {len(agents)} agent(s) from the registry.")
            return agents
        except mysql.connector.Error as err:
            logger.error(f"Failed to read from registry: {err}")
            return []
        finally:
            cursor.close()

    def close_connection(self):
        """Closes the database connection if it's open."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed.")

# --- Example Usage ---
# This block will only run when you execute this script directly.
# It demonstrates how to use the AgentRegistry class.
if __name__ == '__main__':
    # It's best practice to get credentials from environment variables
    # rather than hardcoding them in the source code.
    # Make sure you have a MySQL/MariaDB server running.
    # You can start one easily with Docker:
    # docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=agent_db -p 3306:3306 -d mysql:8
    
    db_connection_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'my-secret-pw'),
        'database': os.getenv('DB_NAME', 'agent_db'),
    }

    try:
        # Initialize the registry
        registry = AgentRegistry(db_config=db_connection_config)

        # --- Example: Write some agents to the registry ---
        logger.info("\n--- WRITING TO REGISTRY ---")
        registry.write_to_registry(
            agent_id="uuid-guesser-001",
            agent_name="GuesserAgent",
            ip_address="192.168.1.101"
        )
        registry.write_to_registry(
            agent_id="uuid-thinker-002",
            agent_name="ThinkerAgent",
            ip_address="192.168.1.102"
        )

        # --- Example: Read all agents from the registry ---
        logger.info("\n--- READING ALL AGENTS ---")
        all_agents = registry.read_from_registry()
        for agent in all_agents:
            print(agent)
            
        # --- Example: Read only recently active agents ---
        logger.info("\n--- READING AGENTS SEEN IN THE LAST 60 SECONDS ---")
        active_agents = registry.read_from_registry(age_limit_seconds=60)
        for agent in active_agents:
            print(agent)

        # Clean up the connection
        registry.close_connection()

    except Exception as e:
        logger.error(f"An error occurred during the example run: {e}")