# Multi-Agent Research System - Langraph Agents

This folder contains the langraph-based agents that execute multi-agent research tasks. The system uses a FastAPI server to expose HTTP endpoints that are called by the MCP server.

## Overview

The agent system consists of:

- **FastAPI Server** (`server.py`) - HTTP API for research execution
- **Research Orchestrator** (`orchestrator.py`) - Coordinates subagent execution  
- **Specialized Subagents** (`subagents.py`) - Individual agent implementations
- **Database Client** (`database.py`) - PostgreSQL integration for session tracking

## Architecture

```
FastAPI Server (server.py)
      ↓
Research Orchestrator (orchestrator.py)
      ↓
Parallel/Sequential Execution
      ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Metadata    │ Entitlement │ Data        │ Aggregation │
│ Agent       │ Agent       │ Agent       │ Agent       │
└─────────────┴─────────────┴─────────────┴─────────────┘
      ↓               ↓            ↓               ↓
External MCP Servers (denodo/, demo/) + Azure OpenAI
```

## Specialized Agents

### MetadataAgent
- **Purpose**: Discover data schemas and metadata
- **Capabilities**: Schema discovery, data source mapping
- **Tools**: Calls Denodo MCP for metadata queries

### EntitlementAgent  
- **Purpose**: Validate data access permissions
- **Capabilities**: Access validation, permission checking
- **Tools**: Basic entitlement simulation (MVP)

### DataAgent
- **Purpose**: Retrieve and process data
- **Capabilities**: Data retrieval, data processing
- **Tools**: Calls Denodo and Demo MCP servers

### AggregationAgent
- **Purpose**: Synthesize research findings
- **Capabilities**: Result synthesis, citation generation
- **Tools**: Azure OpenAI for synthesis

## Setup

### 1. Install Dependencies

```bash
cd agent
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file or set environment variables:

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

# External MCP Endpoints
DENODO_MCP_ENDPOINT=http://localhost:8081
DEMO_MCP_ENDPOINT=http://localhost:8080

# Agent Server Configuration
AGENT_SERVER_HOST=0.0.0.0
AGENT_SERVER_PORT=8001
```

### 3. Initialize Database

Ensure the database is set up:

```bash
cd ../data
python init_db.py
```

### 4. Start External MCP Servers

Start the required MCP servers:

```bash
# Terminal 1: Demo MCP Server
cd ../mcp/demo
python server.py

# Terminal 2: Denodo MCP Server  
cd ../mcp/denodo
python server.py
```

### 5. Start the Agent Server

```bash
cd agent
python server.py
```

The server will start on `http://localhost:8001`

## Usage

### Direct API Calls

```bash
# Health check
curl http://localhost:8001/health

# List agents
curl http://localhost:8001/agents

# Execute research
curl -X POST http://localhost:8001/execute_research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me customer data",
    "research_mode": "full",
    "user_email": "user@example.com"
  }'
```

### Python Client

```python
import httpx
import asyncio

async def test_research():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/execute_research",
            json={
                "query": "What tables contain sales data?",
                "research_mode": "metadata",
                "user_email": "test@example.com"
            }
        )
        return response.json()

result = asyncio.run(test_research())
print(result)
```

## Research Execution Flow

### 1. Query Analysis
The orchestrator analyzes the query and research mode to develop an execution plan.

### 2. Phase Execution
Agents are executed in phases based on the plan:

- **Phase 1**: Metadata + Entitlement (parallel)
- **Phase 2**: Data (sequential) 
- **Phase 3**: Aggregation (sequential)

### 3. Result Synthesis
The AggregationAgent synthesizes all findings into a comprehensive response.

## Research Modes

### Metadata Mode
- Executes: MetadataAgent only
- Use case: Schema discovery, table exploration

### Data Mode  
- Executes: MetadataAgent → EntitlementAgent → DataAgent
- Use case: Data retrieval with validation

### Analysis Mode
- Executes: Full pipeline with synthesis
- Use case: Data analysis and insights

### Full Mode (Default)
- Executes: Complete multi-agent research
- Use case: Comprehensive research tasks

## Database Integration

All agent executions are tracked in PostgreSQL:

- **Sessions**: Research session management
- **Executions**: Individual agent execution tracking
- **Results**: Agent output storage
- **Analytics**: Performance monitoring

### Session Tracking

```python
from database import db_client, AgentType

# Create execution record
execution_id = await db_client.create_subagent_execution(
    session_id=session_id,
    agent_type=AgentType.METADATA,
    task_description="Discover schemas"
)

# Update with results
await db_client.update_subagent_execution(
    execution_id=execution_id,
    status=ExecutionStatus.COMPLETED,
    results={"schemas": [...]}
)
```

## Error Handling

The system implements comprehensive error handling:

- **Agent Failures**: Individual agents can fail without breaking the pipeline
- **Timeout Protection**: Configurable timeouts for external calls
- **Database Resilience**: Continues operation with degraded database
- **Retry Logic**: Built into external MCP calls

## Performance Optimization

### Parallel Execution
- MetadataAgent and EntitlementAgent run in parallel
- Reduces overall execution time

### Connection Pooling
- Database connection pooling for efficiency
- HTTP client reuse for external calls

### Resource Management
- Configurable timeouts and connection limits
- Memory-efficient result processing

## Monitoring and Observability

### Health Endpoints
```bash
# Agent server health
GET /health

# List available agents
GET /agents

# Root information
GET /
```

### Database Analytics
```python
# Get execution analytics
analytics = await db_client.get_session_analytics(days=7)
print(analytics["session_stats"])
print(analytics["subagent_stats"])
```

### Logging
All components use structured logging:
- Agent execution tracking
- External call monitoring
- Error logging with context

## Future Enhancements (Phase 2)

### Langraph Integration
- Replace basic orchestrator with Langraph workflow graphs
- Dynamic graph construction based on query complexity
- Advanced error recovery and retry logic

### Advanced Features
- Chain-of-thought streaming to frontend
- Context compression for long conversations
- Intelligent agent selection based on query analysis
- Performance optimization with caching

## Development

### Running Tests
```bash
# Test individual agents
python -c "
import asyncio
from subagents import MetadataAgent
from database import db_client

async def test():
    await db_client.connect()
    agent = MetadataAgent()
    result = await agent.execute('test-session', 'test task')
    print(result)

asyncio.run(test())
"
```

### Adding New Agents
1. Inherit from `BaseAgent` in `subagents.py`
2. Implement `_execute_logic` method
3. Add to `AGENT_REGISTRY`
4. Update orchestrator execution plans
5. Add database enum entries

### Debugging
```bash
# Enable debug logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from server import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8001)
"
```