# Denodo MCP Server

FastMCP-powered database querying server providing natural language access to Denodo AI SDK for enterprise data virtualization. Features multiple transport options and production-ready deployment.

## Implementation Details

### FastMCP Integration
- **Framework**: FastMCP 2.9+ with automatic protocol handling
- **Transports**: HTTP, STDIO, SSE support  
- **Validation**: Automatic type-hint based parameter validation
- **Error Handling**: MCP-compliant error responses

### Features
- 🔍 **Natural language database queries** via Denodo AI SDK
- 📊 **Data & metadata exploration** with dual operation modes
- ⚡ **Async implementation** for optimal performance
- 🔒 **Secure authentication** with username/password support
- 📝 **Comprehensive logging** with structured output
- 🏥 **Health monitoring** with connection status reporting

## Available Tools

### denodo_query
```python
@mcp.tool
async def denodo_query(query: str, mode: str = "data") -> str:
    """
    Execute natural language queries against Denodo data sources
    
    Args:
        query: Natural language query or SQL statement
        mode: Query mode - 'data' for data queries, 'metadata' for schema exploration
    
    Returns:
        JSON string containing query results or metadata information
    """
```

**Modes**:
- `data`: Execute data queries and return results
  - Natural language: "Show me all customers from California"
  - SQL: "SELECT * FROM customers WHERE state = 'CA'"
- `metadata`: Explore database schema and structure
  - "What tables are available?"
  - "Describe the customers table schema"

## Setup & Configuration

### Installation
```bash
cd mcp/denodo
pip install -r requirements.txt
cp .env.template .env
```

### Environment Configuration
```env
# Denodo AI SDK Configuration
DENODO_AI_SDK_ENDPOINT=http://localhost:8008
DENODO_AI_SDK_USER=admin
DENODO_AI_SDK_PASSWORD=admin
DENODO_AI_SDK_VERIFY_SSL=false

# Server Configuration
LOG_LEVEL=INFO
PORT=8082
HOST=0.0.0.0
```

### Denodo AI SDK Setup

The server requires a running Denodo AI SDK instance:

```bash
# Start Denodo AI SDK (separate installation required)
# Follow Denodo AI SDK documentation for setup
denodo-ai-sdk start --port 8008
```

### Running the Server

**FastMCP Implementation**:
```bash
# HTTP transport (web services)
python fastmcp_main.py --transport http --port 8082

# STDIO transport (Claude Desktop)
python fastmcp_main.py --transport stdio

# SSE transport (streaming)
python fastmcp_main.py --transport sse --port 8082

# With custom configuration
python fastmcp_main.py --transport http --port 8083 --log-level DEBUG
```

**Legacy Implementation** (for comparison):
```bash
python main.py --port 8080
```

## API Reference

### HTTP Transport

**Endpoint**: `POST /mcp`
**Protocol**: JSON-RPC 2.0

**List available tools**:
```bash
curl -X POST http://localhost:8082/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Data query example**:
```bash
curl -X POST http://localhost:8082/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "denodo_query",
      "arguments": {
        "query": "Show me sales data for the last quarter",
        "mode": "data"
      }
    },
    "id": 2
  }'
```

**Metadata query example**:
```bash
curl -X POST http://localhost:8082/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "denodo_query",
      "arguments": {
        "query": "What tables are available in the sales database?",
        "mode": "metadata"
      }
    },
    "id": 3
  }'
```

### Health Check
```bash
curl http://localhost:8082/health

# Response:
{
  "status": "healthy",
  "server": "Denodo Server",
  "version": "2.9.0",
  "tools": 1,
  "denodo_connection": "connected",
  "uptime": "0:25:13"
}
```

## Implementation Architecture

### FastMCP Server (201 lines)
```python
from fastmcp import FastMCP
import asyncio
import json
import httpx

# Initialize FastMCP server
mcp = FastMCP("Denodo Server")

@mcp.tool
async def denodo_query(query: str, mode: str = "data") -> str:
    """Natural language database query via Denodo AI SDK"""
    
    # Get Denodo client configuration
    client_config = get_denodo_config()
    
    async with httpx.AsyncClient(
        base_url=client_config.endpoint,
        auth=(client_config.user, client_config.password),
        verify=client_config.verify_ssl
    ) as client:
        
        # Prepare request based on mode
        if mode == "data":
            endpoint = "/api/v1/query"
            payload = {
                "query": query,
                "format": "json",
                "natural_language": True
            }
        elif mode == "metadata":
            endpoint = "/api/v1/metadata"
            payload = {
                "query": query,
                "include_schema": True
            }
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Execute query
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()  # FastMCP handles everything else!
```

### Migration Benefits

**Code Reduction**: From 511 lines to 201 lines (61% reduction)

**Original Implementation Issues**:
- Manual JSON-RPC protocol handling (150+ lines)
- Custom parameter validation (40+ lines)
- Manual error formatting (25+ lines)
- CORS handling (20+ lines)
- Health check implementation (30+ lines)
- Connection management (50+ lines)

**FastMCP Automatic Features**:
- ✅ Protocol handling (JSON-RPC 2.0)
- ✅ Parameter validation (from type hints)
- ✅ Error formatting (MCP-compliant)
- ✅ CORS handling (configurable)
- ✅ Health checks (built-in)
- ✅ Multiple transports (HTTP/STDIO/SSE)
- ✅ Connection pooling (automatic)

## Development

### Project Structure
```
denodo/
├── fastmcp_server.py          # New FastMCP implementation (201 lines)
├── fastmcp_main.py            # FastMCP entry point with CLI
├── test_server.py             # Server functionality tests
├── Dockerfile.fastmcp         # FastMCP container config
├── requirements.txt           # Updated dependencies with FastMCP
├── .env.template              # Environment variables template
├── main.py                    # Legacy entry point
├── server.py                  # Legacy implementation (511 lines)
└── README.md                  # This file
```

### Denodo AI SDK Integration

**Connection Management**:
```python
from dataclasses import dataclass
import httpx

@dataclass
class DenodoConfig:
    endpoint: str
    user: str
    password: str
    verify_ssl: bool = True

async def test_denodo_connection(config: DenodoConfig) -> bool:
    """Test connectivity to Denodo AI SDK"""
    try:
        async with httpx.AsyncClient(
            base_url=config.endpoint,
            auth=(config.user, config.password),
            verify=config.verify_ssl,
            timeout=10.0
        ) as client:
            response = await client.get("/api/v1/health")
            return response.status_code == 200
    except Exception:
        return False
```

**Query Types**:
```python
# Natural language queries
"Show me all customers from California"
"What are the top 10 products by sales?"
"Find orders placed in the last 30 days"

# SQL queries (passed through)
"SELECT * FROM customers WHERE state = 'CA'"
"SELECT product_id, SUM(sales) FROM orders GROUP BY product_id"

# Metadata queries
"What tables are available?"
"Describe the schema for the customers table"
"Show me the relationships between tables"
```

### Testing

**Connection Testing**:
```bash
# Test Denodo AI SDK connectivity
python -c "
import asyncio
import os
from fastmcp_server import test_denodo_connection, DenodoConfig

config = DenodoConfig(
    endpoint=os.getenv('DENODO_AI_SDK_ENDPOINT'),
    user=os.getenv('DENODO_AI_SDK_USER'),
    password=os.getenv('DENODO_AI_SDK_PASSWORD'),
    verify_ssl=os.getenv('DENODO_AI_SDK_VERIFY_SSL', 'true').lower() == 'true'
)

connected = asyncio.run(test_denodo_connection(config))
print('Denodo connection:', 'OK' if connected else 'FAILED')
"
```

**Query Testing**:
```bash
# Test query functionality
python -c "
import asyncio
from fastmcp_server import denodo_query

# Test data query
result = asyncio.run(denodo_query('Show available tables', 'metadata'))
print('Metadata query result:', result)

# Test data query
result = asyncio.run(denodo_query('SELECT COUNT(*) FROM customers', 'data'))
print('Data query result:', result)
"
```

## Deployment

### Docker
```bash
# Build FastMCP container
docker build -f Dockerfile.fastmcp -t dataflow/denodo-mcp:fastmcp .

# Run with environment
docker run -p 8082:8082 \
  -e DENODO_AI_SDK_ENDPOINT=http://denodo-ai-sdk:8008 \
  -e DENODO_AI_SDK_USER=admin \
  -e DENODO_AI_SDK_PASSWORD=admin \
  dataflow/denodo-mcp:fastmcp

# Docker Compose with Denodo AI SDK
docker-compose --profile denodo up -d
```

### Production Configuration
```yaml
# docker-compose.yml
services:
  denodo-ai-sdk:
    image: denodo/ai-sdk:latest
    ports:
      - "8008:8008"
    environment:
      - DENODO_LICENSE_KEY=${DENODO_LICENSE_KEY}

  denodo-mcp-fastmcp:
    build:
      context: ./mcp/denodo
      dockerfile: Dockerfile.fastmcp
    environment:
      TRANSPORT: http
      PORT: 8082
      LOG_LEVEL: INFO
      DENODO_AI_SDK_ENDPOINT: http://denodo-ai-sdk:8008
      DENODO_AI_SDK_USER: ${DENODO_USER}
      DENODO_AI_SDK_PASSWORD: ${DENODO_PASSWORD}
    ports:
      - "8082:8082"
    depends_on:
      - denodo-ai-sdk
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Security Considerations

**Authentication**:
- Use environment variables for credentials
- Consider vault solutions for production
- Enable SSL/TLS for Denodo connections
- Implement connection timeout and retry logic

**Access Control**:
```python
# Optional: Add authentication middleware
@mcp.middleware
async def auth_middleware(request, call_next):
    # Verify API keys, tokens, etc.
    return await call_next(request)
```

## Troubleshooting

### Common Issues

**Connection Issues**:
```bash
# Test Denodo AI SDK connectivity
curl http://localhost:8008/api/v1/health

# Check network connectivity
ping denodo-ai-sdk-host

# Verify credentials
curl -u admin:admin http://localhost:8008/api/v1/health
```

**Query Issues**:
```bash
# Enable debug logging
LOG_LEVEL=DEBUG python fastmcp_main.py

# Test queries directly
python -c "
import asyncio
from fastmcp_server import denodo_query
result = asyncio.run(denodo_query('SHOW TABLES', 'metadata'))
print(result)
"
```

**FastMCP Issues**:
```bash
# Check FastMCP installation
python -c "import fastmcp; print(fastmcp.__version__)"

# Validate server configuration
python -c "
from fastmcp_server import mcp
print('Server name:', mcp.name)
print('Available tools:', [tool.name for tool in mcp.tools])
"
```

### Performance Optimization

- **Connection pooling**: Reuse HTTP connections to Denodo
- **Query caching**: Cache metadata queries for performance
- **Async operations**: Use async/await for all I/O operations
- **Connection limits**: Configure appropriate connection limits
- **Timeout handling**: Set reasonable timeouts for long queries

### Monitoring

**Health Checks**:
- Monitor `/health` endpoint for server status
- Check Denodo AI SDK connectivity
- Monitor query response times
- Track error rates and types

**Logging**:
```python
# Structured logging for production
import structlog

logger = structlog.get_logger()

@mcp.tool
async def denodo_query(query: str, mode: str = "data") -> str:
    logger.info("denodo_query_start", query=query, mode=mode)
    
    try:
        result = await execute_query(query, mode)
        logger.info("denodo_query_success", query=query, mode=mode, 
                   result_size=len(result))
        return result
    except Exception as e:
        logger.error("denodo_query_error", query=query, mode=mode, 
                    error=str(e))
        raise
```
