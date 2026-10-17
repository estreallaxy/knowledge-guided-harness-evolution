import os
import json
import click
import logging
import socket
import uvicorn
import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import asyncio
import httpx

from asgiref.wsgi import WsgiToAsgi

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser

from services.registry.mysql_agent_registry import AgentRegistry
from services.agents.utils import report_activity

# --- Agent's Core Knowledge & Logic ---

# For demo purposes, we use a hardcoded dictionary of exchange rates.
# This avoids the need for a live API key and ensures consistent, reliable results.
FIXED_RATES = {
    "CHF_TO_USD": 1.12,
    "CHF_TO_EUR": 1.03,
    "USD_TO_CHF": 0.89,
    "EUR_TO_CHF": 0.97,
    "USD_TO_EUR": 0.92,
    "EUR_TO_USD": 1.08,
}
AGENT_NAME = "currency-agent"
EXCHANGE_RATE_API_NAME = "ExchangeRateAPI"

async def get_live_rate(from_currency: str, to_currency: str, session_id: str) -> float | None:
    """
    Fetches a live exchange rate from an external API.
    Returns the rate or None if the call fails.
    """
    api_url = f"https://open.er-api.com/v6/latest/{from_currency}"
    report_activity(
        session_id=session_id,
        source=AGENT_NAME,
        target=EXCHANGE_RATE_API_NAME,
        content=f"GET {api_url}",
        msg_type="tool_call"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            if data.get("result") == "success" and to_currency in data.get("rates", {}):
                rate = data["rates"][to_currency]
                logger.info(f"Successfully fetched live rate from API: {from_currency} -> {to_currency} at {rate}")
                report_activity(
                    session_id=session_id,
                    source=EXCHANGE_RATE_API_NAME,
                    target=AGENT_NAME,
                    content=json.dumps({"rate": rate}),
                    msg_type="tool_call"
                )
                
                return rate
            else:
                logger.warning(f"API call was successful but did not contain a valid rate. Data: {data}")
                return None
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"Failed to fetch live exchange rate from API. Error: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during API call. Error: {e}", exc_info=True)
        return None

async def convert_currency(amount: float, from_currency: str, to_currency: str, session_id: str) -> str:
    """
    Converts an amount from one currency to another using the agent's fixed rate table.

    Args:
        amount (float): The amount of money to convert.
        from_currency (str): The currency to convert from (e.g., 'CHF').
        to_currency (str): The currency to convert to (e.g., 'USD').

    Returns:
        str: A JSON string containing the result or an error.
    """
    # Normalize currency codes to uppercase to match the keys in FIXED_RATES
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency == to_currency:
        rate = 1.0
    else:
        #Try and get live rate
        rate = await get_live_rate(from_currency, to_currency, session_id)

        #fallback to static
        if rate is None:
            key = f"{from_currency}_TO_{to_currency}"
            rate = FIXED_RATES.get(key)
            if rate is None:
                error_message = {"error": f"Conversion rate for {from_currency}_TO_{to_currency} not found."}
                logger.warning(f"Failed conversion attempt: {error_message}")
                return json.dumps(error_message)

    if rate is None:
        error_message = {"error": f"Conversion rate for {from_currency}_TO_{to_currency} not found."}
        logger.warning(f"Failed conversion attempt: {error_message}")
        return json.dumps(error_message)
    
    try:
        # Ensure the amount is a float before calculation
        converted_amount = float(amount) * rate
        result = {
            "original_amount": float(amount),
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": round(converted_amount, 2)
        }
        logger.info(f"Successfully converted {amount} {from_currency} to {result['converted_amount']} {to_currency}")
        return json.dumps(result)
    except (ValueError, TypeError) as e:
        error_message = {"error": "Invalid amount provided. Amount must be a number."}
        logger.error(f"Failed conversion due to invalid amount: {amount}. Error: {e}")
        return json.dumps(error_message)


# --- A2A Server Setup using Flask ---

# Basic configuration
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)

def _get_caller_name_from_request() -> str:
    """Finds the service name of the caller via reverse DNS on its IP."""
    default_name = "coord-a2a" # Fallback
    try:
        ip_address = request.remote_addr
        service_name, _, _ = socket.gethostbyaddr(ip_address)
        caller_name = service_name.split('.')[0]
        logging.info(f"Identified caller IP {ip_address} as service: {caller_name}")
        return caller_name
    except Exception as e:
        logging.warning(f"Could not perform reverse DNS on caller's IP: {e}. Defaulting to '{default_name}'")
    return default_name

@app.route("/.well-known/agent", methods=["GET"])
def agent_card():
    """Serves the agent's self-description card.
    This endpoint allows other agents to discover its capabilities.
    """
    card = {
        "name": "CurrencyConverter",
        "description": "A simple, specialist agent that converts currency amounts using a fixed rate table. Useful for converting travel prices.\n\nBuilt with no agentic messaging framework nor agentic framework",
        "tools": [{
            "name": "convert_currency",
            "description": "Converts an amount from one currency to another. It only supports CHF, USD, and EUR.",
            "parameters": {
                "amount": "float",
                "from_currency": "string. The currency to convert FROM. MUST be one of: 'CHF', 'USD', 'EUR'.",
                "to_currency": "string. The currency to convert TO. MUST be one of: 'CHF', 'USD', 'EUR'."
            }
        }]
    }
    return jsonify(card)


@app.route("/messages", methods=["POST"])
def handle_message():
    """
    Handles incoming messages. It uses an LLM to parse natural language
    into a structured tool call for the convert_currency function.
    """
    try:
        # Get caller and session info
        caller_name = _get_caller_name_from_request()
        session_id = request.cookies.get("context_id") or str(uuid.uuid4())
        logger.info(f"Handling request for session_id: {session_id}")

        # Step 1: Flexibly extract the user's query from the request
        if request.is_json:
            user_query = request.json.get("content", str(request.json))
        else:
            user_query = request.get_data(as_text=True)

        logger.info(f"Received natural language query: '{user_query}'")

        # Step 2: Set up the LLM, Prompt, and Parser
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME"),
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        prompt_template = """
        You are an expert at extracting parameters for a function call from a user's query.
        The user wants to call the 'convert_currency' function.
        Your job is to extract the 'amount', 'from_currency', and 'to_currency' from the following query.

        The ONLY supported currency codes are 'CHF', 'USD', and 'EUR'.

        User Query: "{query}"

        Respond with ONLY a JSON object containing the extracted parameters.
        Example: {{"amount": 150.0, "from_currency": "CHF", "to_currency": "USD"}}
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        parser = JsonOutputParser()
        
        # Step 3: Create and invoke the chain
        chain = prompt | llm | parser
        tool_args = chain.invoke({"query": user_query})
        
        logger.info(f"LLM parsed arguments: {tool_args}")

        # Inject session_id for logging
        tool_args["session_id"] = session_id

        # Step 4: Call the deterministic tool with the parsed arguments
        result_json_str = asyncio.run(convert_currency(**tool_args))

        report_activity(
            session_id=session_id,
            source=AGENT_NAME,
            target=caller_name,
            content=result_json_str,
            msg_type="communication"
        )
        
        return app.response_class(
            response=result_json_str,
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"An error occurred while handling a message: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@click.command()
@click.option('--host', default='0.0.0.0', help='The host to bind the server to.')
@click.option('--port', default=10000, type=int, help='The port for the server.')
def main(host, port):
    """Starts the Currency Converter agent server."""
    registry = None
    public_url = os.getenv('PUBLIC_URL')
    internal_url = os.getenv('INTERNAL_URL')
    agent_id = public_url
    agent_name = AGENT_NAME

    db_config = {
        'host': os.getenv('DB_HOST'), 'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'), 'database': os.getenv('DB_NAME')
    }

    if all(db_config.values()) and agent_id:
        try:
            registry = AgentRegistry(db_config=db_config)
            logger.info(f"Registering agent '{agent_name}' ({agent_id}) with the discovery service...")
            registry.write_to_registry(
                agent_id=agent_id,
                agent_name=agent_name,
                ip_address=public_url,
                docker_address=internal_url
            )
        except Exception as reg_err:
            logger.error(f"Could not connect to or write to the agent registry: {reg_err}")
        finally:
            if registry:
                registry.close_connection() # Close after writing
    else:
        logger.warning("Database environment variables not fully set or OWN_URL is missing. Skipping registration.")
    
    logger.info(f"Starting Currency Converter on http://{host}:{port}")
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, host=host, port=port)

if __name__ == '__main__':
    main()