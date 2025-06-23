#!/usr/bin/env python3
"""
Demo MCP HTTP Server

This server provides general purpose AI tools with synthetic data generation capabilities using Azure OpenAI
through the Model Context Protocol (MCP) using HTTP transport for containerized deployments.

Usage:
    python http_server.py [--port PORT] [--host HOST]

Environment Variables:
    AZURE_OPENAI_API_KEY: The Azure OpenAI API key for generating responses
    AZURE_OPENAI_ENDPOINT: The Azure OpenAI endpoint URL
    AZURE_OPENAI_DEPLOYMENT: The Azure OpenAI deployment name to use
    MCP_SERVER_PORT: Port to run the HTTP server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the HTTP server to (default: 0.0.0.0)
"""

import os
import sys
import json
import logging
import argparse
import traceback
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timedelta
import random

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

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, StreamingResponse, Response
from starlette.requests import Request
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# HTTP Server configuration
DEFAULT_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
DEFAULT_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")

# Azure OpenAI configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
if not AZURE_OPENAI_DEPLOYMENT:
    raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is required")
if not AZURE_OPENAI_API_VERSION:
    raise ValueError("AZURE_OPENAI_API_VERSION environment variable is required")

# Initialize Azure OpenAI client
openai_client = AsyncAzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

logger.info("Demo MCP HTTP Server initialized with Azure OpenAI integration")

# Synthetic data categories and types
SYNTHETIC_DATA_TYPES = {
    "people": {
        "description": "Generate synthetic person data",
        "fields": {
            "name": "Full name of the person",
            "age": "Age in years (18-100)",
            "email": "Email address",
            "phone": "Phone number",
            "address": "Physical address",
            "occupation": "Job title or profession",
            "salary": "Annual salary",
            "skills": "List of professional skills",
            "education": "Education level and institutions",
            "bio": "Short biographical description"
        }
    },
    "companies": {
        "description": "Generate synthetic company data",
        "fields": {
            "name": "Company name",
            "industry": "Industry sector",
            "size": "Number of employees",
            "revenue": "Annual revenue",
            "founded": "Year founded",
            "location": "Headquarters location",
            "description": "Company description",
            "website": "Website URL",
            "ceo": "CEO name",
            "products": "List of main products/services"
        }
    },
    "products": {
        "description": "Generate synthetic product data",
        "fields": {
            "name": "Product name",
            "category": "Product category",
            "price": "Price in USD",
            "description": "Product description",
            "features": "List of key features",
            "rating": "Customer rating (1-5)",
            "reviews": "Number of reviews",
            "brand": "Brand name",
            "availability": "Stock status",
            "specifications": "Technical specifications"
        }
    },
    "events": {
        "description": "Generate synthetic event data",
        "fields": {
            "name": "Event name",
            "type": "Event type (conference, workshop, meeting, etc.)",
            "date": "Event date and time",
            "location": "Event location",
            "attendees": "Number of attendees",
            "organizer": "Event organizer",
            "description": "Event description",
            "agenda": "Event agenda or schedule",
            "registration_fee": "Registration cost",
            "duration": "Event duration"
        }
    },
    "sales": {
        "description": "Generate synthetic sales data",
        "fields": {
            "transaction_id": "Unique transaction identifier",
            "customer_name": "Customer name",
            "product": "Product name",
            "quantity": "Quantity sold",
            "unit_price": "Price per unit",
            "total_amount": "Total transaction amount",
            "date": "Sale date",
            "sales_rep": "Sales representative",
            "region": "Sales region",
            "discount": "Discount applied"
        }
    },
    "surveys": {
        "description": "Generate synthetic survey data",
        "fields": {
            "respondent_id": "Unique respondent identifier",
            "age_group": "Age group category",
            "gender": "Gender identity",
            "location": "Geographic location",
            "responses": "Survey question responses",
            "satisfaction_score": "Overall satisfaction (1-10)",
            "completion_time": "Time to complete survey",
            "feedback": "Additional written feedback",
            "survey_date": "Date survey was taken",
            "survey_type": "Type of survey"
        }
    }
}

# Sample data patterns for realistic synthetic data generation
SAMPLE_DATA_PATTERNS = {
    "first_names": ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "James", "Jennifer", "Robert", "Ashley", "Christopher", "Amanda", "Matthew", "Jessica", "Joshua", "Michelle"],
    "last_names": ["Smith", "Johnson", "Brown", "Davis", "Wilson", "Anderson", "Miller", "Garcia", "Martinez", "Taylor", "Thomas", "White", "Harris", "Clark", "Lewis", "Robinson"],
    "cities": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus"],
    "industries": ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Consulting", "Media", "Transportation", "Energy", "Real Estate", "Food Service"],
    "job_titles": ["Software Engineer", "Marketing Manager", "Data Analyst", "Sales Representative", "Product Manager", "Designer", "Accountant", "Teacher", "Nurse", "Consultant"],
    "product_categories": ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Beauty", "Automotive", "Toys", "Health", "Food & Beverage"],
    "company_names": ["TechCorp", "InnovateLab", "DataDyne", "CloudNext", "SmartSystems", "FutureWorks", "DigitalEdge", "AlphaTech", "BetaSoft", "GammaSolutions"]
}

class QueryContext(BaseModel):
    query_type: str  # "generate", "analyze", "info"
    data_type: List[str] = []
    count: int = 1
    format: str = "json"
    specific_fields: List[str] = []

async def analyze_query_intent(question: str) -> QueryContext:
    """Analyze the user's question to understand intent and context"""
    
    question_lower = question.lower()
    
    # Determine query type
    if any(word in question_lower for word in ["generate", "create", "make", "produce", "synthetic"]):
        query_type = "generate"
    elif any(word in question_lower for word in ["analyze", "analysis", "insights", "trends", "patterns"]):
        query_type = "analyze"
    else:
        query_type = "info"
    
    # Identify data type focus
    data_type = []
    for data_category in SYNTHETIC_DATA_TYPES.keys():
        if data_category in question_lower or data_category[:-1] in question_lower:  # singular form
            data_type.append(data_category)
    
    # Extract count if specified
    count = 1
    import re
    count_match = re.search(r'\b(\d+)\b', question_lower)
    if count_match:
        count = min(int(count_match.group(1)), 100)  # Limit to 100 records
    
    # Determine format
    format_type = "json"
    if "csv" in question_lower:
        format_type = "csv"
    elif "table" in question_lower or "tabular" in question_lower:
        format_type = "table"
    
    return QueryContext(
        query_type=query_type,
        data_type=data_type,
        count=count,
        format=format_type
    )

async def generate_ai_response(question: str, context: QueryContext) -> str:
    """Generate a response using Azure OpenAI for general purpose AI queries"""
    
    # Build context for OpenAI
    system_prompt = f"""
You are a general purpose AI assistant with synthetic data generation capabilities.
You can generate realistic synthetic data for various types of entities and scenarios.

Available synthetic data types:
{json.dumps(SYNTHETIC_DATA_TYPES, indent=2)}

Sample data patterns available:
{json.dumps(SAMPLE_DATA_PATTERNS, indent=2)}

Guidelines for responses:
1. Generate realistic and diverse synthetic data that follows industry patterns
2. Use appropriate terminology and realistic values for each data type
3. Ensure data consistency and logical relationships between fields
4. For generation requests, create the requested number of records
5. For analysis requests, provide insights and patterns from synthetic scenarios
6. For info requests, explain capabilities and data types available
7. Always format responses clearly and professionally
8. Use JSON, CSV, or table format as requested
9. Include relevant context and explanations
10. Never generate real personal information - all data should be clearly synthetic

Current date context: {datetime.now().strftime('%Y-%m-%d')}
Data generation capabilities: People, Companies, Products, Events, Sales, Surveys, and more.
"""

    user_prompt = f"""
Query Type: {context.query_type}
Data Type Focus: {context.data_type}
Count Requested: {context.count}
Format: {context.format}

User Question: {question}

Please provide a helpful response. If this is a data generation request, create realistic synthetic data. 
If this is an analysis request, provide insights about synthetic data scenarios. 
If this is an info request, explain the available capabilities.
"""

    try:
        response = await openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"Error generating response: {str(e)}"

# Tool implementations
async def ask_ai(question: str, mode: str = "generate") -> str:
    """Ask the general purpose AI for information or to generate synthetic data.

    Accepts a mode parameter to specify the type of request:
    - generate: Generate synthetic data. For example, 'generate 5 people with names and ages'
    - analyze: Analyze patterns or provide insights. For example, 'analyze sales trends'
    - info: Get information about capabilities. For example, 'what data types can you generate?'

    Args:
        question: Natural language question or request (e.g. "generate 10 companies with revenue data")
        mode: The mode to use for the query. Can be "generate", "analyze", or "info".

    Returns:
        str: The AI response with generated data, analysis, or information.
    """
    if not question.strip():
        return "Error: Question cannot be empty"
    
    if mode not in ["generate", "analyze", "info"]:
        return "Error: Mode must be either 'generate', 'analyze', or 'info'"
    
    logger.info(f"Processing AI request in {mode} mode: {question[:100]}...")
    
    try:
        # Analyze the query to understand intent
        context = await analyze_query_intent(question)
        context.query_type = mode  # Override with specified mode
        
        # Handle info queries directly for faster response
        if mode == "info":
            question_lower = question.lower()
            
            # Check if asking about specific data type
            for data_type, data_info in SYNTHETIC_DATA_TYPES.items():
                if data_type in question_lower or data_type[:-1] in question_lower:
                    response = f"## {data_type.title()} Data Generation\n\n"
                    response += f"**Description:** {data_info['description']}\n\n"
                    response += "**Available Fields:**\n"
                    for field_name, field_desc in data_info['fields'].items():
                        response += f"- `{field_name}`: {field_desc}\n"
                    return response
            
            # General capabilities overview
            if any(word in question_lower for word in ["capabilities", "what", "types", "generate"]):
                response = "## AI Synthetic Data Generation Capabilities\n\n"
                response += "I can generate realistic synthetic data for the following categories:\n\n"
                for data_type, data_info in SYNTHETIC_DATA_TYPES.items():
                    response += f"### {data_type.title()}\n"
                    response += f"{data_info['description']}\n"
                    response += f"Fields available: {len(data_info['fields'])}\n\n"
                response += "\n**Usage Examples:**\n"
                response += "- Generate 5 people with names and emails\n"
                response += "- Create 10 companies in the technology industry\n"
                response += "- Generate product data with pricing information\n"
                response += "- Create sales data for Q1 analysis\n"
                return response
        
        # Generate response using OpenAI for generate and analyze queries
        response = await generate_ai_response(question, context)
        
        logger.info("Successfully processed AI request")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        traceback.print_exc()
        return f"Error processing query: {str(e)}"

async def health_check() -> str:
    """Check the health of the demo AI system.
    
    Returns:
        str: Health status of the demo MCP server
    """
    try:
        # Test Azure OpenAI connection
        test_response = await openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        return "✅ Demo MCP Server is healthy\n✅ Azure OpenAI API connection successful\n✅ Synthetic data generation ready"
    except Exception as e:
        return f"⚠️ Health check issues detected:\n❌ Azure OpenAI API error: {str(e)}"

async def get_server_info() -> str:
    """Get information about the demo MCP server.
    
    Returns:
        str: Server configuration and capabilities
    """
    info = {
        "server_name": "Demo MCP Server",
        "version": "1.0.0",
        "description": "General purpose AI with synthetic data generation capabilities using Azure OpenAI",
        "data_types": list(SYNTHETIC_DATA_TYPES.keys()),
        "supported_modes": ["generate", "analyze", "info"],
        "ai_model": f"Azure OpenAI ({AZURE_OPENAI_DEPLOYMENT})",
        "capabilities": ["Synthetic data generation", "Natural language processing", "Data analysis", "General AI assistance"]
    }
    
    info_str = "# Demo MCP Server Information\n\n"
    for key, value in info.items():
        if isinstance(value, list):
            info_str += f"**{key.replace('_', ' ').title()}:**\n"
            for item in value:
                info_str += f"- {item}\n"
            info_str += "\n"
        else:
            info_str += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
    
    return info_str

# Available tools mapping
AVAILABLE_TOOLS = {
    "ask_ai": ask_ai,
    "health_check": health_check,
    "get_server_info": get_server_info
}

class MCPHTTPServer:
    def __init__(self):
        self.tools = AVAILABLE_TOOLS
        logger.info("Initialized Demo MCP HTTP Server")

    async def handle_mcp_request(self, request: Request) -> JSONResponse | StreamingResponse:
        """Handle MCP requests over HTTP transport"""
        try:
            if request.method == "OPTIONS":
                # Handle CORS preflight requests
                return JSONResponse(
                    {"message": "CORS preflight"},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                        "Access-Control-Max-Age": "86400"
                    }
                )
                
            elif request.method == "POST":
                # Handle JSON-RPC request
                body = await request.body()
                if not body:
                    return JSONResponse(
                        {"error": {"code": -32600, "message": "Invalid Request - Empty body"}},
                        status_code=400
                    )

                try:
                    request_data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError as e:
                    return JSONResponse(
                        {"error": {"code": -32700, "message": f"Parse error: {str(e)}"}},
                        status_code=400
                    )

                # Process the MCP request
                response = await self._process_mcp_request(request_data)
                
                # Handle notifications (which don't get responses)
                if response is None:
                    return Response(status_code=204, headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization"
                    })
                
                # Check if streaming is needed (for large responses or tool results)
                if self._needs_streaming(response):
                    return await self._create_sse_response(response)
                else:
                    # Add CORS headers to regular JSON responses
                    return JSONResponse(response, headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization"
                    })

            elif request.method == "GET":
                # Handle server info requests or health checks
                return await self._handle_get_request(request)

            else:
                return JSONResponse(
                    {"error": {"code": -32601, "message": "Method not allowed"}},
                    status_code=405
                )

        except Exception as e:
            logger.error(f"Error handling MCP request: {str(e)}")
            return JSONResponse(
                {"error": {"code": -32603, "message": f"Internal error: {str(e)}"}},
                status_code=500
            )

    async def _process_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Process the MCP JSON-RPC request"""
        try:
            # Extract method and params from JSON-RPC request
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")

            logger.info(f"Processing MCP method: {method}")

            # Handle notifications (requests without an 'id' field)
            is_notification = request_id is None

            if method == "tools/list":
                # Return available tools with proper schemas
                tools = [
                    {
                        "name": "ask_ai",
                        "description": "Ask the general purpose AI for information or to generate synthetic data with support for multiple modes",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "Natural language question or request to the AI"
                                },
                                "mode": {
                                    "type": "string",
                                    "enum": ["generate", "analyze", "info"],
                                    "default": "generate",
                                    "description": "Request mode: 'generate' for synthetic data, 'analyze' for insights, 'info' for capabilities"
                                }
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "health_check",
                        "description": "Check the health status of the demo MCP server and OpenAI connection",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "get_server_info",
                        "description": "Get information about the demo MCP server configuration and capabilities",
                        "inputSchema": {
                            "type": "object", 
                            "properties": {},
                            "required": []
                        }
                    }
                ]

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }

            elif method == "tools/call":
                # Call a specific tool
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})

                if tool_name not in self.tools:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                    }

                # Execute the tool
                tool_func = self.tools[tool_name]
                try:
                    # Handle different tools with their specific parameters
                    if tool_name == "ask_ai":
                        question = tool_arguments.get("question", "")
                        mode = tool_arguments.get("mode", "generate")
                        result = await tool_func(question, mode)
                    elif tool_name in ["health_check", "get_server_info"]:
                        result = await tool_func()
                    else:
                        # Generic parameter passing for other tools
                        result = await tool_func(**tool_arguments)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(result)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    logger.error(f"Tool execution error for {tool_name}: {str(e)}")
                    traceback.print_exc()
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"}
                    }

            elif method == "initialize":
                # Initialize the MCP session with proper capabilities
                client_info = params.get("clientInfo", {})
                protocol_version = params.get("protocolVersion", "2024-11-05")
                
                logger.info(f"Initializing MCP session with client: {client_info.get('name', 'unknown')}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": protocol_version,
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "demo",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "notifications/initialized":
                # Handle the initialized notification (no response needed for notifications)
                logger.info("MCP session initialized successfully")
                # Notifications don't get responses, so return None to indicate success
                return None

            else:
                # For notifications, we shouldn't return an error
                if is_notification:
                    logger.warning(f"Unknown notification method: {method}")
                    return None
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

        except Exception as e:
            logger.error(f"Error processing MCP request: {str(e)}")
            # For notifications, don't return an error response
            if request_data.get("id") is None:
                return None
            
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }

    def _needs_streaming(self, response: Dict[str, Any]) -> bool:
        """Determine if the response needs streaming"""
        # Stream if the response is large or contains certain types of content
        response_str = json.dumps(response)
        return len(response_str) > 8192  # Stream responses larger than 8KB

    async def _create_sse_response(self, response: Dict[str, Any]) -> StreamingResponse:
        """Create a Server-Sent Events response for streaming"""
        async def generate():
            # Send the response as SSE
            yield f"data: {json.dumps(response)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    async def _handle_get_request(self, request: Request) -> JSONResponse:
        """Handle GET requests for server info and health checks"""
        path = request.url.path
        
        cors_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
        
        if path.endswith("/health"):
            return JSONResponse({"status": "healthy", "server": "demo_mcp_ai"}, headers=cors_headers)
        
        elif path.endswith("/info"):
            return JSONResponse({
                "server": "Demo MCP Server",
                "version": "1.0.0",
                "transport": "http",
                "capabilities": ["tools"],
                "endpoints": ["/mcp", "/health", "/info"]
            }, headers=cors_headers)
        
        else:
            return JSONResponse({
                "message": "Demo MCP Server",
                "description": "General purpose AI with synthetic data generation capabilities using Azure OpenAI",
                "endpoints": {
                    "POST /mcp": "MCP JSON-RPC requests",
                    "GET /health": "Health check",
                    "GET /info": "Server information"
                }
            }, headers=cors_headers)

# Create the HTTP server instance
http_server = MCPHTTPServer()

# Create Starlette application
app = Starlette(
    routes=[
        Route("/mcp", endpoint=http_server.handle_mcp_request, methods=["POST", "GET", "OPTIONS"]),
        Route("/health", endpoint=http_server.handle_mcp_request, methods=["GET", "OPTIONS"]),
        Route("/info", endpoint=http_server.handle_mcp_request, methods=["GET", "OPTIONS"]),
        Route("/", endpoint=http_server.handle_mcp_request, methods=["GET", "OPTIONS"]),
    ]
)

def main():
    """Main entry point for the HTTP server"""
    parser = argparse.ArgumentParser(description="Demo MCP HTTP Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Log level")
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    logger.info(f"Starting Demo MCP HTTP Server on {args.host}:{args.port}")
    logger.info(f"MCP endpoint will be available at: http://{args.host}:{args.port}/mcp")
    
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
