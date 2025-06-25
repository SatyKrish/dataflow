#!/usr/bin/env python3
"""
Demo FastMCP Server

A demonstration MCP server providing tools to use generic AI capabilities with 
synthetic data generation for demo purposes using Azure OpenAI through FastMCP.

This replaces the custom HTTP server implementation with FastMCP's streamlined approach.

Usage:
    python fastmcp_server.py

Environment Variables:
    AZURE_OPENAI_API_KEY: The Azure OpenAI API key for generating responses
    AZURE_OPENAI_ENDPOINT: The Azure OpenAI endpoint URL
    AZURE_OPENAI_DEPLOYMENT: The Azure OpenAI deployment name to use
    AZURE_OPENAI_API_VERSION: The Azure OpenAI API version to use
    MCP_SERVER_PORT: Port to run the server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the server to (default: 0.0.0.0)
"""

import os
import logging
from typing import Literal
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file if python-dotenv is not available
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from fastmcp import FastMCP, Context
from openai import AsyncAzureOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables
required_env_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT", 
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_API_VERSION"
]

for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"{var} environment variable is required")

# Initialize Azure OpenAI client
openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Create FastMCP server
mcp = FastMCP(
    name="demo",
    instructions="""
    Demo AI Assistant providing tools to use generic AI capabilities with synthetic data generation for demo purposes.
    
    Available capabilities:
    - Ask AI questions in different modes (generate, analyze, info)
    - Generate synthetic data for people, companies, products, events, sales, and surveys
    - Perform data analysis on synthetic scenarios
    - Get information about server capabilities
    - Health monitoring
    
    Use 'generate' mode for creating synthetic data, 'analyze' mode for insights, 
    and 'info' mode to learn about available data types and capabilities.
    """
)

# Synthetic data context for AI prompts
SYNTHETIC_DATA_CONTEXT = """
You are a synthetic data generation and analysis assistant. You can help with:

Data Types Available:
- People: names, demographics, contact info, employment, skills, education
- Companies: business info, industry data, financial metrics, locations
- Products: consumer goods, pricing, features, ratings, specifications  
- Events: conferences, meetings, workshops, dates, locations, attendees
- Sales: transactions, revenue, customers, products, dates, performance
- Surveys: responses, demographics, opinions, ratings, feedback

Guidelines:
1. Generate realistic and diverse synthetic data following industry patterns
2. Use appropriate terminology and realistic values for each data type
3. Ensure data consistency and logical relationships between fields
4. For generation requests, create the requested number of records
5. For analysis requests, provide insights and patterns from synthetic scenarios
6. For info requests, explain capabilities and data types available
7. Format responses clearly using JSON, CSV, or tables as appropriate
8. Include relevant context and explanations
9. Never generate real personal information - all data should be clearly synthetic
10. Current date context: {current_date}
"""

@mcp.tool
async def ask_ai(
    question: str, 
    mode: Literal["generate", "analyze", "info"] = "generate"
) -> str:
    """Ask the general purpose AI for information or to generate synthetic data.
    
    Args:
        question: Natural language question or request to the AI
        mode: Request mode:
            - 'generate': Create synthetic data (default)
            - 'analyze': Provide insights and analysis on synthetic scenarios  
            - 'info': Get information about capabilities and available data types
    
    Returns:
        AI-generated response with synthetic data, analysis, or information
    """
    if not question.strip():
        return "Error: Question cannot be empty"
    
    logger.info(f"Processing AI request in {mode} mode: {question[:100]}...")
    
    # Build context-aware system prompt
    system_prompt = SYNTHETIC_DATA_CONTEXT.format(
        current_date=datetime.now().strftime('%Y-%m-%d')
    )
    
    # Create mode-specific user prompt
    user_prompt = f"""
Query Type: {mode}
User Question: {question}

Please provide a helpful response based on the mode:
- If 'generate': Create realistic synthetic data
- If 'analyze': Provide insights about synthetic data scenarios  
- If 'info': Explain available capabilities and data types

Format the response clearly and professionally.
"""
    
    try:
        response = await openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        logger.info("Successfully processed AI request")
        return result
        
    except Exception as e:
        logger.error(f"Azure OpenAI API error: {str(e)}")
        return f"Error generating AI response: {str(e)}"

@mcp.tool
async def health_check() -> dict:
    """Check the health status of the demo MCP server and Azure OpenAI connection.
    
    Returns:
        Health status information including server status and OpenAI connectivity
    """
    logger.info("Performing health check")
    
    health_status = {
        "server_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_name": "Demo FastMCP Server",
        "version": "2.0.0-fastmcp"
    }
    
    # Test Azure OpenAI connection
    try:
        test_response = await openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        health_status["azure_openai_status"] = "connected"
        health_status["azure_openai_model"] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    except Exception as e:
        health_status["azure_openai_status"] = f"error: {str(e)}"
        logger.warning(f"Azure OpenAI health check failed: {e}")
    
    return health_status

@mcp.tool
async def get_server_info() -> dict:
    """Get information about the demo MCP server configuration and capabilities.
    
    Returns:
        Server configuration and capability information
    """
    return {
        "server_name": "Demo FastMCP Server",
        "version": "2.0.0-fastmcp",
        "framework": "FastMCP 2.9+",
        "description": "Tools to use generic AI capabilities with synthetic data generation for demo purposes",
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_openai_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "capabilities": [
            "Synthetic data generation",
            "Data analysis and insights", 
            "AI question answering",
            "Health monitoring",
            "Multiple response modes"
        ],
        "supported_data_types": [
            "people", "companies", "products", 
            "events", "sales", "surveys"
        ],
        "modes": {
            "generate": "Create synthetic data",
            "analyze": "Provide insights and analysis",
            "info": "Explain capabilities and data types"
        }
    }

if __name__ == "__main__":
    # Get server configuration from environment
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))
    
    logger.info(f"Starting Demo FastMCP Server on {host}:{port}")
    logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
    logger.info("FastMCP handles all protocol details automatically!")
    
    # Run with HTTP transport - FastMCP handles everything else
    mcp.run(transport="http", host=host, port=port)
