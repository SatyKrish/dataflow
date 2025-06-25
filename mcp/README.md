# DataFlow MCP Servers

Model Context Protocol (MCP) servers built with FastMCP 2.9+ for natural language database interactions and AI-powered tools. This directory contains two production-ready MCP servers with enterprise deployment capabilities.

## FastMCP Migration ✅

Successfully migrated from custom HTTP implementation to FastMCP 2.9+ with significant improvements:

- **69% code reduction** (1,269 → 388 lines total)
- **Multiple transports**: HTTP, STDIO, SSE support
- **Enhanced validation**: Automatic type-hint based validation  
- **Standards compliance**: Full MCP 2024-11-05 specification
- **Future-ready**: Middleware, auth, composition support

## Available Servers

### Demo Server (`/demo`)
**Purpose**: AI-powered tools with synthetic data generation  
**Provider**: Azure OpenAI or OpenAI  
**Tools**: `ask_ai`, `generate_synthetic_data`  
**Use Cases**: Development, testing, general AI assistance

### Denodo Server (`/denodo`) 
**Purpose**: Enterprise data virtualization with natural language queries  
**Provider**: Denodo AI SDK  
**Tools**: `denodo_query`  
**Use Cases**: Production database access, business intelligence

## Quick Start

### Development Setup
```bash
# Demo server
cd demo && pip install -r requirements.txt && cp .env.template .env

# Denodo server  
cd denodo && pip install -r requirements.txt && cp .env.template .env
```

### Running Servers
```bash
# Demo server (FastMCP)
cd demo && python fastmcp_main.py --transport http --port 8081

# Denodo server (FastMCP)
cd denodo && python fastmcp_main.py --transport http --port 8082
```

### Docker Deployment
```bash
# Start both FastMCP servers
docker-compose --profile fastmcp up -d

# Individual servers
docker-compose up -d dataflow-mcp-demo-fastmcp
docker-compose up -d dataflow-mcp-denodo-fastmcp
```

## Server Coordination

### Port Allocation
- **Demo Server**: 8081 (FastMCP), 8080 (Legacy)
- **Denodo Server**: 8082 (FastMCP), 8080 (Legacy)
- **Health Checks**: `GET /health` on each server

### Transport Options
Both servers support FastMCP's multiple transport protocols:

```bash
# HTTP for web applications
python fastmcp_main.py --transport http --port 808X

# STDIO for Claude Desktop
python fastmcp_main.py --transport stdio

# SSE for streaming applications  
python fastmcp_main.py --transport sse --port 808X
```

### Tool Discovery
```bash
# List all available tools across servers
curl -X POST http://localhost:8081/mcp -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
curl -X POST http://localhost:8082/mcp -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Migration Impact

| Server | Before | After | Reduction |
|--------|--------|-------|-----------|
| **Demo** | 758 lines | 187 lines | 75% |
| **Denodo** | 511 lines | 201 lines | 61% |
| **Total** | 1,269 lines | 388 lines | **69%** |

**Legacy files preserved** for comparison and rollback capability.

## Production Deployment

### Docker Compose Configuration
```yaml
services:
  # Demo MCP Server
  dataflow-mcp-demo-fastmcp:
    build:
      context: ./demo
      dockerfile: Dockerfile.fastmcp
    environment:
      - TRANSPORT=http
      - PORT=8081
    ports:
      - "8081:8081"

  # Denodo MCP Server  
  dataflow-mcp-denodo-fastmcp:
    build:
      context: ./denodo
      dockerfile: Dockerfile.fastmcp
    environment:
      - TRANSPORT=http
      - PORT=8082
    ports:
      - "8082:8082"
    depends_on:
      - denodo-ai-sdk
```

### Health Monitoring
```bash
# Check all MCP servers
curl http://localhost:8081/health  # Demo
curl http://localhost:8082/health  # Denodo

# Expected responses include server status, tool count, and uptime
```

## Development

### Adding New MCP Servers

1. **Create server directory** under `/mcp/new-server`
2. **Implement FastMCP server** following existing patterns
3. **Add Docker configuration** with unique port
4. **Update docker-compose.yml** with new service
5. **Document tools and usage** in server-specific README

### Server Communication

MCP servers are designed to be independent but can be coordinated:

```python
# Example: Multi-server tool orchestration
async def coordinated_query():
    # Step 1: Generate synthetic data (Demo server)
    synthetic_data = await call_mcp_tool("demo", "generate_synthetic_data", 
                                       {"data_type": "customers", "count": 100})
    
    # Step 2: Query real database (Denodo server)  
    real_data = await call_mcp_tool("denodo", "denodo_query",
                                   {"query": "SELECT COUNT(*) FROM customers"})
    
    return {"synthetic": synthetic_data, "real": real_data}
```

## Troubleshooting

### Common Issues

**Port conflicts**:
```bash
# Check port usage
lsof -i :8081 :8082

# Use alternative ports
python fastmcp_main.py --port 8083
```

**Server connectivity**:
```bash
# Test individual servers
curl http://localhost:8081/health
curl http://localhost:8082/health

# Test tool availability
curl -X POST http://localhost:808X/mcp \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

For detailed implementation, configuration, and troubleshooting information, see the individual server README files:
- [Demo Server README](./demo/README.md)
- [Denodo Server README](./denodo/README.md)
