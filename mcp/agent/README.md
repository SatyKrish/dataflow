# Multi-Agent Research MCP Server

This is the FastMCP server that provides multi-agent research capabilities to the chat interface. It acts as the single point of interaction and coordinates with the langraph-based agents in the main `agent/` folder.

## Overview

The MCP server exposes the following tools:
- `multi_agent_research` - Execute research using specialized AI agents
- `get_research_session` - Retrieve session status and results
- `list_available_agents` - List available agents and capabilities  
- `health_check` - Check system health status
- `analyze_query_intent` - Analyze queries to determine research approach

## Architecture

```
Chat Interface
      ↓
MCP Agent Server (this component)
      ↓ HTTP calls
FastAPI Agent Server (agent/server.py)
      ↓
Langraph Orchestrator (agent/orchestrator.py)
      ↓
Specialized Subagents (agent/subagents.py)
      ↓
External MCP Servers (denodo/, demo/)
```

## Setup

### 1. Install Dependencies

```bash
cd mcp/agent
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment
AZURE_OPENAI_API_VERSION=2024-02-01

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dataflow_agents
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Agent Server Configuration
LANGRAPH_AGENTS_ENDPOINT=http://localhost:8001

# MCP Server Configuration
MCP_SERVER_PORT=8082
MCP_SERVER_HOST=0.0.0.0
```

### 3. Initialize Database

```bash
cd ../../data
python init_db.py
```

### 4. Start the Agent Server

First, start the FastAPI agent server:

```bash
cd ../../agent
python server.py
```

### 5. Start the MCP Server

In a separate terminal:

```bash
cd mcp/agent
python server.py
```

## Usage

### Basic Research

```python
# Call via MCP client
result = await mcp_client.call("multi_agent_research", {
    "query": "Show me sales data for Q4 2023",
    "research_mode": "data",
    "user_email": "user@example.com"
})
```

### Health Check

```python
health = await mcp_client.call("health_check")
print(health["overall_status"])  # "healthy" or "degraded"
```

### Query Intent Analysis

```python
intent = await mcp_client.call("analyze_query_intent", {
    "query": "What tables contain customer information?"
})
print(intent["recommended_mode"])  # "metadata"
```

## Research Modes

- **metadata**: Schema and structure discovery only
- **data**: Data retrieval with permission validation
- **analysis**: Full analysis with synthesis
- **full**: Complete multi-agent research (default)

## Error Handling

The server handles various error conditions:
- Agent server unavailable (connection errors)
- Database connection issues  
- Request timeouts (5 minute default)
- Invalid queries or parameters

Errors are returned with structured error information:

```json
{
    "status": "failed",
    "error": "Description of the error",
    "details": "Additional error context"
}
```

## Development

### Running Tests

```bash
# Test MCP server directly
python -c "
import asyncio
from server import mcp
result = asyncio.run(mcp.call('health_check'))
print(result)
"
```

### Debugging

Set log level to DEBUG:

```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import server
"
```

## Integration with Chat Interface

Add to `mcp_config.json`:

```json
{
  "servers": {
    "multi-agent-research": {
      "command": "python",
      "args": ["mcp/agent/server.py"],
      "env": {
        "LANGRAPH_AGENTS_ENDPOINT": "http://localhost:8001"
      }
    }
  }
}
```

## Monitoring

The health check endpoint provides status for:
- MCP server status
- Agent server connectivity  
- Database connection
- Overall system health

Use for monitoring and alerting in production deployments. 