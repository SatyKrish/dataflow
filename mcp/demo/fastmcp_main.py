#!/usr/bin/env python3
"""
Demo FastMCP Server Entry Point

Main entry point for the FastMCP-based demo server with command line argument support.

Usage:
    python fastmcp_main.py [--port PORT] [--host HOST] [--transport TRANSPORT]

Environment Variables:
    AZURE_OPENAI_API_KEY: The Azure OpenAI API key for generating responses
    AZURE_OPENAI_ENDPOINT: The Azure OpenAI endpoint URL
    AZURE_OPENAI_DEPLOYMENT: The Azure OpenAI deployment name to use
    AZURE_OPENAI_API_VERSION: The Azure OpenAI API version to use
    MCP_SERVER_PORT: Port to run the server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the server to (default: 0.0.0.0)
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point for the FastMCP demo server"""
    parser = argparse.ArgumentParser(description="Demo FastMCP Server")
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
        "--transport",
        choices=["http", "stdio", "sse"],
        default="http",
        help="Transport protocol (default: http)"
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
    
    # Import the FastMCP server
    try:
        from fastmcp_server import mcp, logger
        
        logger.info(f"Starting Demo FastMCP Server on {args.host}:{args.port}")
        logger.info(f"Transport: {args.transport}")
        logger.info(f"MCP endpoint: http://{args.host}:{args.port}/mcp")
        
        # Run the server with specified transport
        if args.transport == "stdio":
            mcp.run(transport="stdio")
        elif args.transport == "sse":
            mcp.run(transport="sse", host=args.host, port=args.port)
        else:  # http
            mcp.run(transport="http", host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
