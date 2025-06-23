# Demo MCP Server

A Model Context Protocol (MCP) server that provides general purpose AI tools with synthetic data generation capabilities using Azure OpenAI. Uses HTTP transport for containerized deployments and web services.

## Features

- 🤖 **General Purpose AI**: Ask questions and get intelligent responses on any topic
- 📊 **Synthetic Data Generation**: Generate realistic synthetic data for testing and development
- � **Multiple Request Modes**: Support for generate, analyze, and info modes
- 🏥 **Health Monitoring**: Built-in health check functionality
- 🔒 **Secure Authentication**: Azure OpenAI API key based authentication
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ⚡ **Async Support**: Fully asynchronous implementation for better performance
- 🌐 **HTTP Transport**: RESTful API with JSON-RPC 2.0 protocol support
- 🐳 **Docker Support**: Ready-to-deploy Docker containers

## Synthetic Data Types

The AI can generate realistic synthetic data for:

- **People**: Names, ages, emails, addresses, occupations, and more
- **Companies**: Business information, revenue, industry sectors, locations
- **Products**: Product details, pricing, categories, specifications
- **Events**: Conferences, meetings, workshops with attendees and schedules
- **Sales**: Transaction data, customer information, sales metrics
- **Surveys**: Response data, demographics, satisfaction scores

## Development

### Project Structure

```
demo/
├── http_server.py              # MCP HTTP server implementation  
├── main.py                     # Entry point script
├── run_local.py                # Convenience script for local development
├── requirements.txt            # Python dependencies
├── .env.local                  # Environment variables template
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## Installation

### Local Development Setup

1. **Clone the repository and navigate to the demo directory:**
```bash
cd /path/to/demo
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

5. **Set up environment variables:**
```bash
# Copy the template and fill in your values
cp .env.local .env

# Edit .env and add your Azure OpenAI details
# AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
# AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint-here
# AZURE_OPENAI_DEPLOYMENT=your-azure-openai-deployment-name-here
# AZURE_OPENAI_API_VERSION=2024-02-01
```

## Configuration

The server can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_API_KEY` | Required | Azure OpenAI API key for generating responses |
| `AZURE_OPENAI_ENDPOINT` | Required | Azure OpenAI endpoint (e.g., https://<your-resource-name>.openai.azure.com) |
| `AZURE_OPENAI_DEPLOYMENT` | Required | Azure OpenAI deployment name |
| `AZURE_OPENAI_API_VERSION` | Required | Azure OpenAI API version (e.g., 2024-02-01) |
| `MCP_SERVER_PORT` | `8080` | Port to run the HTTP server on |
| `MCP_SERVER_HOST` | `0.0.0.0` | Host to bind the HTTP server to |

## Usage

### Local Deployment

**Quick Start:**
```bash
# Using the convenience script (loads .env automatically)
python3 run_local.py
```

**Or manually:**
```bash
# Run mcp server directly
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

**4. Test AI request:**
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "ask_ai",
      "arguments": {
        "question": "Generate 5 people with names and ages",
        "mode": "generate"
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

### Available Tools

#### `ask_ai(question, mode="generate")`
Ask the general purpose AI for information or to generate synthetic data.

**Parameters:**
- `question` (str): Natural language question or request
- `mode` (str): Request mode - "generate", "analyze", or "info"

**Examples:**

**Generate Mode:**
```python
# Generate synthetic data
ask_ai("Generate 10 people with names, ages, and emails", mode="generate")
ask_ai("Create 5 companies in the technology sector", mode="generate")
ask_ai("Generate product data with pricing information", mode="generate")
```

**Analyze Mode:**
```python
# Get insights and analysis
ask_ai("Analyze sales trends for e-commerce businesses", mode="analyze")
ask_ai("What factors affect customer satisfaction?", mode="analyze")
```

**Info Mode:**
```python
# Get information about capabilities
ask_ai("What data types can you generate?", mode="info")
ask_ai("Tell me about people data generation", mode="info")
```

#### `health_check()`
Check the health and connectivity of the Azure OpenAI API.

#### `get_server_info()`
Get information about the MCP server configuration and capabilities.

## Example Requests

### Generate Synthetic People Data
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "ask_ai",
      "arguments": {
        "question": "Generate 3 people with names, ages, occupations, and email addresses in JSON format",
        "mode": "generate"
      }
    }
  }'
```

### Generate Company Data
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "ask_ai",
      "arguments": {
        "question": "Create 5 technology companies with revenue and employee count",
        "mode": "generate"
      }
    }
  }'
```

### Get Analysis
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "ask_ai",
      "arguments": {
        "question": "Analyze the key factors that influence product pricing strategies",
        "mode": "analyze"
      }
    }
  }'
```

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
    "ask_ai": ask_ai,
    "health_check": health_check,
    "get_server_info": get_server_info,
    "new_tool": new_tool  # Add your new tool here
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.