# Denodo AI SDK MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with a Denodo AI SDK, enabling natural language database queries. Uses HTTP transport for containerized deployments and web services.

## Features

- 🔍 **Natural Language Database Queries**: Query your database using plain English
- 📊 **Data & Metadata Modes**: Support for both data queries and metadata exploration
- 🏥 **Health Monitoring**: Built-in health check functionality
- 🔒 **Secure Authentication**: Support for username/password authentication
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ⚡ **Async Support**: Fully asynchronous implementation for better performance
- 🌐 **HTTP Transport**: RESTful API with JSON-RPC 2.0 protocol support
- 🐳 **Docker Support**: Ready-to-deploy Docker containers

## Development

### Project Structure

```
denodo/
├── http_server.py              # MCP HTTP server implementation  
├── main.py                     # Entry point script
├── run_local.py                # Convenience script for local development
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose configuration (if present)
├── .venv/                      # Virtual environment (created during setup)
└── README.md                   # This file
```

## Installation

### Local Development Setup

1. **Clone the repository and navigate to the denodo directory:**
```bash
cd /path/to/denodo
```

2. **Create a virtual environment:**
```bash
python3 -m venv .venv
```

3. **Activate the virtual environment:**
```bash
# On macOS/Linux
source .venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Set up environment variables (optional):**
```bash
export DENODO_AI_SDK_ENDPOINT="http://localhost:8008"
export DENODO_AI_SDK_USER="admin"
export DENODO_AI_SDK_PASSWORD="admin"
export DENODO_AI_SDK_VERIFY_SSL="false"
export MCP_SERVER_PORT="8080"
export MCP_SERVER_HOST="0.0.0.0"
```

## Configuration

The server can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DENODO_AI_SDK_ENDPOINT` | `http://localhost:8008` | AI SDK endpoint URL |
| `DENODO_AI_SDK_USER` | `admin` | Authentication username |
| `DENODO_AI_SDK_PASSWORD` | `admin` | Authentication password |
| `DENODO_AI_SDK_VERIFY_SSL` | `false` | Whether to verify SSL certificates |

## Usage

### Local Deployment

**Quick Start:**
```bash
# Run mcp server
python3 main.py
```

### Testing the Server

Once the server is running, you can test it using curl or any HTTP client:

**1. Check server health:**
```bash
curl http://localhost:8080/health
```

**2. Get server information:**
```bash
curl http://localhost:8080/info
```

**3. Test MCP tool listing:**
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

**4. Test a database query:**
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "ask_database",
      "arguments": {
        "question": "How many data products do we have?",
        "mode": "data"
      }
    }
  }'
```

### Production Deployment

### Docker Deployment

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### HTTP Endpoints

When running with HTTP transport, the following endpoints are available:

- `POST /mcp` - Main MCP JSON-RPC endpoint
- `GET /health` - Health check endpoint
- `GET /info` - Server information
- `GET /` - Basic server information

Example MCP request:

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "ask_database",
      "arguments": {
        "question": "How many customers do we have?",
        "mode": "data"
      }
    }
  }'
```

### Available Tools

#### `ask_database(question, mode="data")`
Query the database in natural language.

**Parameters:**
- `question` (str): Natural language question about your data
- `mode` (str): Query mode - either "data" or "metadata"

**Examples:**
```python
# Data queries
ask_database("How many customers do we have?", mode="data")
ask_database("What were our total sales last month?", mode="data")

# Metadata queries  
ask_database("What columns are in the customers table?", mode="metadata")
ask_database("What is the data type of the customer_id column?", mode="metadata")
```

#### `health_check()`
Check the health and connectivity of the AI SDK.

#### `get_server_info()`
Get information about the MCP server configuration.

## Next Steps

### Adding New Tools

To add new tools to the MCP server:

1. Define a new async function in `http_server.py`
2. Add it to the `AVAILABLE_TOOLS` dictionary
3. Add the tool schema in the `tools/list` method
4. Implement proper error handling and logging

Example:
```python
async def new_tool(param: str) -> str:
    """Description of what this tool does.
    
    Args:
        param: Description of the parameter.
        
    Returns:
        str: Description of the return value.
    """
    logger.info(f"Executing new_tool with param: {param}")
    try:
        # Implementation here
        return "Result"
    except Exception as e:
        logger.error(f"Error in new_tool: {e}")
        return f"Error: {e}"

# Add to AVAILABLE_TOOLS
AVAILABLE_TOOLS = {
    "ask_database": ask_database,
    "health_check": health_check,
    "get_server_info": get_server_info,
    "new_tool": new_tool  # Add your new tool here
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
