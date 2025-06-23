#!/usr/bin/env python3
"""
Demo MCP HTTP Server

This server provides general purpose AI tools with synthetic data generation capabilities using Azure OpenAI 
through the Model Context Protocol (MCP) using HTTP transport for containerized deployments.

Usage:
    python main.py [--port PORT] [--host HOST]

Environment Variables:
    AZURE_OPENAI_API_KEY: The Azure OpenAI API key for generating responses
    AZURE_OPENAI_ENDPOINT: The Azure OpenAI endpoint URL
    AZURE_OPENAI_DEPLOYMENT: The Azure OpenAI deployment name to use
    MCP_SERVER_PORT: Port to run the HTTP server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the HTTP server to (default: 0.0.0.0)
"""

import os
import sys
import argparse
import logging
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

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))
print(f"Python path: {sys.path}")
print(f"Looking for uvicorn in path")
try:
    import uvicorn
    print("Uvicorn imported successfully in debug")
except ImportError as e:
    print(f"Failed to import uvicorn: {e}")

def main():
    """Main entry point for the HTTP server"""
    parser = argparse.ArgumentParser(description="Demo MCP HTTP Server")
    parser.add_argument("--host", default=os.getenv("MCP_SERVER_HOST", "0.0.0.0"), help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_SERVER_PORT", "8080")), help="Port to bind to (default: 8080)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Log level")
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    # HTTP transport for containerized usage
    import uvicorn
    from http_server import app, logger
    
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
