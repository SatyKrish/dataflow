#!/usr/bin/env python3
"""
Denodo AI SDK MCP HTTP Server

This server provides tools to interact with a Denodo AI SDK through the Model Context Protocol (MCP)
using HTTP transport for containerized deployments.

Usage:
    python http_server.py [--port PORT] [--host HOST]

Environment Variables:
    DENODO_AI_SDK_ENDPOINT: The endpoint URL for the AI SDK (default: http://localhost:8008)
    DENODO_AI_SDK_USER: Username for authentication (default: admin)
    DENODO_AI_SDK_PASSWORD: Password for authentication (default: admin)
    DENODO_AI_SDK_VERIFY_SSL: Whether to verify SSL certificates (default: false)
    MCP_SERVER_PORT: Port to run the HTTP server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the HTTP server to (default: 0.0.0.0)
"""

import os
import sys
import json
import logging
import argparse
import httpx
import traceback
from pathlib import Path
from typing import Any, Dict

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, StreamingResponse
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# HTTP Server configuration
DEFAULT_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
DEFAULT_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")

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

logger.info(f"Denodo AI SDK MCP HTTP Server initialized with endpoint: {AI_SDK_ENDPOINT}")

# Tool implementations
async def ask_database(question: str, mode: str = "data") -> str:
    """Query the user's database in natural language.

    Accepts a mode parameter to specify the mode to use for the query:
    - data: Query the data in the database. For example, 'how many new customers did we get last month?'
    - metadata: Query the metadata in the database. For example, 'what is the type of the column 'customer_id' in the customers table?'

    Args:
        question: Natural language question (e.g. "how many new customers did we get last month?")
        mode: The mode to use for the query. Can be "data" or "metadata".

    Returns:
        str: The response from the Denodo AI SDK or an error message.
    """
    if not question.strip():
        return "Error: Question cannot be empty"
    
    if mode not in ["data", "metadata"]:
        return "Error: Mode must be either 'data' or 'metadata'"
    
    logger.info(f"Processing question in {mode} mode: {question[:100]}...")
    
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
            
            if mode == "data":
                result = data.get('execution_result', 'The Denodo AI SDK did not return a result.')
            else:
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
        logger.error(f"Unexpected error: {str(e)}")
        traceback.print_exc(file=sys.stderr) 
        return f"Error fetching response: {str(e)}"

async def health_check() -> str:
    """Check the health of the Denodo AI SDK connection.
    
    Returns:
        str: Health status of the Denodo AI SDK endpoint.
    """
    try:
        async with httpx.AsyncClient(verify=AI_SDK_VERIFY_SSL, timeout=30.0) as client:
            response = await client.get(
                f"{AI_SDK_ENDPOINT}/health",
                auth=(AI_SDK_USER, AI_SDK_PASSWORD)
            )
            if response.status_code == 200:
                return "✅ Denodo AI SDK is healthy and reachable"
            else:
                return f"⚠️ Denodo AI SDK returned status code: {response.status_code}"
    except httpx.ConnectError:
        return f"❌ Cannot connect to Denodo AI SDK at {AI_SDK_ENDPOINT}"
    except Exception as e:
        return f"❌ Health check failed: {str(e)}"

async def get_server_info() -> str:
    """Get information about the MCP server configuration.
    
    Returns:
        str: Server configuration information.
    """
    info = {
        "server_name": "Denodo AI SDK MCP HTTP Server",
        "endpoint": AI_SDK_ENDPOINT,
        "user": AI_SDK_USER,
        "ssl_verification": AI_SDK_VERIFY_SSL,
        "available_modes": ["data", "metadata"]
    }
    
    info_str = "**MCP Server Information**\n\n"
    for key, value in info.items():
        info_str += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    return info_str

# Available tools mapping
AVAILABLE_TOOLS = {
    "ask_database": ask_database,
    "health_check": health_check,
    "get_server_info": get_server_info
}

class MCPHTTPServer:
    def __init__(self):
        self.tools = AVAILABLE_TOOLS
        logger.info("Initialized MCP HTTP Server")

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
                    return JSONResponse(None, status_code=204, headers={
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
                        "name": "ask_database",
                        "description": "Query the user's database in natural language with support for data and metadata modes",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "Natural language question to ask the database"
                                },
                                "mode": {
                                    "type": "string",
                                    "enum": ["data", "metadata"],
                                    "default": "data",
                                    "description": "Query mode: 'data' for querying data, 'metadata' for schema information"
                                }
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "health_check",
                        "description": "Check the health status of the Denodo AI SDK connection",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "get_server_info",
                        "description": "Get information about the MCP server configuration and capabilities",
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
                    if tool_name == "ask_database":
                        question = tool_arguments.get("question", "")
                        mode = tool_arguments.get("mode", "data")
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
                            "name": "denodo_aisdk",
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
            return JSONResponse({"status": "healthy", "server": "denodo_aisdk_mcp"}, headers=cors_headers)
        
        elif path.endswith("/info"):
            return JSONResponse({
                "server": "Denodo AI SDK MCP Server",
                "version": "1.0.0",
                "transport": "http",
                "capabilities": ["tools"],
                "endpoints": ["/mcp", "/health", "/info"]
            }, headers=cors_headers)
        
        else:
            return JSONResponse({
                "message": "Denodo AI SDK MCP Server",
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
    parser = argparse.ArgumentParser(description="Denodo AI SDK MCP HTTP Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Log level")
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    logger.info(f"Starting Denodo AI SDK MCP HTTP Server on {args.host}:{args.port}")
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
