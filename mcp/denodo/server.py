#!/usr/bin/env python3
"""
Denodo FastMCP Server

A FastMCP server providing tools to retrieve data from the Data Platform for production use.

This replaces the custom HTTP server implementation with FastMCP's streamlined approach.

Usage:
    python fastmcp_server.py

Environment Variables:
    DENODO_AI_SDK_ENDPOINT: The endpoint URL for the AI SDK (default: http://localhost:8008)
    DENODO_AI_SDK_USER: Username for authentication (default: admin)
    DENODO_AI_SDK_PASSWORD: Password for authentication (default: admin)
    DENODO_AI_SDK_VERIFY_SSL: Whether to verify SSL certificates (default: false)
    MCP_SERVER_PORT: Port to run the server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the server to (default: 0.0.0.0)
"""

import os
import logging
import httpx
from typing import Literal
from pathlib import Path

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Denodo AI SDK configuration
AI_SDK_ENDPOINT = os.getenv("DENODO_AI_SDK_ENDPOINT", "http://localhost:8008").rstrip('/')
AI_SDK_USER = os.getenv("DENODO_AI_SDK_USER", "admin")
AI_SDK_PASSWORD = os.getenv("DENODO_AI_SDK_PASSWORD", "admin")
AI_SDK_VERIFY_SSL = os.getenv("DENODO_AI_SDK_VERIFY_SSL", "false").lower() == "true"

# Validate required configuration
if not AI_SDK_ENDPOINT:
    raise ValueError("DENODO_AI_SDK_ENDPOINT is required")
if not AI_SDK_USER:
    raise ValueError("DENODO_AI_SDK_USER is required")
if not AI_SDK_PASSWORD:
    raise ValueError("DENODO_AI_SDK_PASSWORD is required")

# Create FastMCP server
mcp = FastMCP(
    name="denodo",
    instructions=f"""
    Denodo Data Platform Interface providing tools to retrieve data from the Data Platform for production use.
    
    This server provides access to your production data through natural language queries
    using the Denodo AI SDK at {AI_SDK_ENDPOINT}.
    
    Available capabilities:
    - Query production database data using natural language
    - Get database metadata and schema information
    - Ask questions about table structures, column types, and relationships
    - Generate insights from your production data
    
    Use 'data' mode for querying actual data (e.g., "how many customers do we have?")
    Use 'metadata' mode for schema questions (e.g., "what columns are in the users table?")
    """
)

logger.info(f"Denodo FastMCP Server initialized with endpoint: {AI_SDK_ENDPOINT}")

@mcp.tool
async def ask_database(
    question: str, 
    mode: Literal["data", "metadata"] = "data"
) -> str:
    """Query the user's database in natural language.

    Use this tool to ask questions about your database in plain English. The Denodo AI SDK
    will translate your question into appropriate SQL queries and return the results.

    Args:
        question: Natural language question about your database 
                 (e.g., "how many new customers did we get last month?" or 
                       "what is the type of the column 'customer_id' in the customers table?")
        mode: The query mode to use:
            - 'data': Query the actual data in the database (default)
            - 'metadata': Query database schema, table structures, and column information

    Returns:
        The response from the Denodo AI SDK with query results or an error message
    """
    if not question.strip():
        return "Error: Question cannot be empty"
    
    logger.info(f"Processing database question in '{mode}' mode: {question[:100]}...")
    
    # Prepare request parameters for Denodo AI SDK
    params = {
        "question": question,
        "mode": mode,
        "verbose": False,
        "markdown_response": True
    }

    try:
        async with httpx.AsyncClient(verify=AI_SDK_VERIFY_SSL, timeout=120.0) as client:
            response = await client.post(
                f"{AI_SDK_ENDPOINT}/answerQuestion", 
                json=params, 
                auth=(AI_SDK_USER, AI_SDK_PASSWORD)
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract appropriate result based on mode
            if mode == "data":
                result = data.get('execution_result', 'The Denodo AI SDK did not return a result.')
            else:  # metadata mode
                result = data.get('answer', 'The Denodo AI SDK did not return a result.')
            
            logger.info("Successfully processed database query")
            return result
            
    except httpx.TimeoutException:
        error_msg = "Request timed out while connecting to the Denodo AI SDK"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except httpx.ConnectError:
        error_msg = f"Could not connect to Denodo AI SDK at {AI_SDK_ENDPOINT}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        logger.error(f"Unexpected error querying database: {str(e)}")
        return f"Error processing database query: {str(e)}"

@mcp.tool
async def health_check() -> dict:
    """Check the health of the Denodo AI SDK connection.
    
    Tests connectivity to the Denodo AI SDK endpoint and returns status information.
    
    Returns:
        Health status information including connectivity and configuration details
    """
    logger.info("Performing Denodo AI SDK health check")
    
    health_status = {
        "server_status": "healthy",
        "server_name": "Denodo FastMCP Server", 
        "version": "2.0.0-fastmcp",
        "denodo_endpoint": AI_SDK_ENDPOINT,
        "ssl_verification": AI_SDK_VERIFY_SSL
    }
    
    try:
        async with httpx.AsyncClient(verify=AI_SDK_VERIFY_SSL, timeout=30.0) as client:
            response = await client.get(
                f"{AI_SDK_ENDPOINT}/health",
                auth=(AI_SDK_USER, AI_SDK_PASSWORD)
            )
            
            if response.status_code == 200:
                health_status["denodo_status"] = "connected"
                health_status["denodo_response_time_ms"] = response.elapsed.total_seconds() * 1000
            else:
                health_status["denodo_status"] = f"http_error_{response.status_code}"
                
    except httpx.ConnectError:
        health_status["denodo_status"] = "connection_failed"
        logger.warning(f"Cannot connect to Denodo AI SDK at {AI_SDK_ENDPOINT}")
    except httpx.TimeoutException:
        health_status["denodo_status"] = "timeout"
        logger.warning("Denodo AI SDK health check timed out")
    except Exception as e:
        health_status["denodo_status"] = f"error_{type(e).__name__}"
        logger.warning(f"Denodo AI SDK health check failed: {str(e)}")
    
    return health_status

@mcp.tool
async def get_server_info() -> dict:
    """Get information about the Denodo MCP server configuration and capabilities.
    
    Returns:
        Server configuration, capabilities, and connection information
    """
    return {
        "server_name": "Denodo FastMCP Server",
        "version": "2.0.0-fastmcp", 
        "framework": "FastMCP 2.9+",
        "description": "Tools to retrieve data from the Data Platform for production use",
        "denodo_ai_sdk": {
            "endpoint": AI_SDK_ENDPOINT,
            "user": AI_SDK_USER,
            "ssl_verification": AI_SDK_VERIFY_SSL
        },
        "capabilities": [
            "Natural language database queries",
            "Database metadata exploration", 
            "Schema information retrieval",
            "SQL generation and execution",
            "Health monitoring"
        ],
        "query_modes": {
            "data": "Query actual data in the database",
            "metadata": "Query database schema and structure information"
        },
        "examples": {
            "data_queries": [
                "How many customers do we have?",
                "What was our total revenue last month?",
                "Show me the top 10 products by sales"
            ],
            "metadata_queries": [
                "What tables are available in the database?",
                "What columns are in the customers table?",
                "What is the data type of the customer_id column?"
            ]
        }
    }

if __name__ == "__main__":
    # Get server configuration from environment
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))
    
    logger.info(f"Starting Denodo FastMCP Server on {host}:{port}")
    logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
    logger.info(f"Denodo AI SDK: {AI_SDK_ENDPOINT}")
    logger.info("FastMCP handles all protocol details automatically!")
    
    # Run with HTTP transport - FastMCP handles everything else
    mcp.run(transport="http", host=host, port=port)
