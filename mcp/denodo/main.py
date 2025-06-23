#!/usr/bin/env python3
"""
Denodo AI SDK MCP HTTP Server

This server provides tools to interact with a Denodo AI SDK through the Model Context Protocol (MCP)
using HTTP transport for containerized deployments.

Usage:
    python main.py [--port PORT] [--host HOST]

Environment Variables:
    DENODO_AI_SDK_ENDPOINT: The endpoint URL for the AI SDK (default: http://localhost:8008)
    DENODO_AI_SDK_USER: Username for authentication (default: admin)
    DENODO_AI_SDK_PASSWORD: Password for authentication (default: admin)
    DENODO_AI_SDK_VERIFY_SSL: Whether to verify SSL certificates (default: false)
    MCP_SERVER_PORT: Port for HTTP transport (default: 8080)
    MCP_SERVER_HOST: Host for HTTP transport (default: 0.0.0.0)
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point for the HTTP MCP server"""
    parser = argparse.ArgumentParser(description="Denodo AI SDK MCP HTTP Server")
    parser.add_argument(
        "--host", 
        default=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("MCP_SERVER_PORT", "8080")),
        help="Port to bind to (default: 8080)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    # HTTP transport for containerized usage
    import uvicorn
    from http_server import app, logger
    
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
