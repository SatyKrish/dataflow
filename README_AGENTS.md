# Multi-Agent Research System - MVP Implementation

This repository contains the MVP implementation of a multi-agent research system that enables natural language queries across multiple data sources using specialized AI agents.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat Interface│    │ MCP Agent Server│    │ Agent Server    │
│                 │────│ (FastMCP)       │────│ (FastAPI)       │
│ chat/           │    │ mcp/agent/      │    │ agent/          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │ Research        │    │ Specialized     │    │ External MCP    │
                    │ Orchestrator    │    │ Subagents       │    │ Servers         │
                    │                 │    │                 │    │                 │
                    │ • Query Analysis│    │ • MetadataAgent │    │ • Demo MCP      │
                    │ • Task Planning │    │ • EntitlementAgent│  │ • Denodo MCP    │
                    │ • Parallel Exec │    │ • DataAgent     │    │                 │
                    │ • Result Synthesis│  │ • AggregationAgent│  │                 │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │                         │
                              └─────────────────────────┼─────────────────────────┘
                                                        ▼
                                              ┌─────────────────┐
                                              │ PostgreSQL DB   │
                                              │                 │
                                              │ • Sessions      │
                                              │ • Executions    │
                                              │ • Results       │
                                              │ • Analytics     │
                                              └─────────────────┘
```

## 📁 Component Structure

### Core Components

- **`agent/`** - Langraph-based research agents (FastAPI server)
  - `server.py` - HTTP API endpoints
  - `orchestrator.py` - Multi-agent coordination
  - `subagents.py` - Specialized agent implementations
  - `database.py` - PostgreSQL integration

- **`mcp/agent/`** - MCP server (single interface point)
  - `server.py` - FastMCP server exposing tools to chat
  - `database.py` - Database client for MCP operations

- **`data/`** - Database infrastructure
  - `schema.sql` - PostgreSQL schema definition
  - `init_db.py` - Database initialization script

### Supporting Infrastructure

- **`mcp/demo/`** - Demo MCP server for synthetic data
- **`mcp/denodo/`** - Denodo MCP server for data access
- **`chat/`** - Chat interface (existing)

## 🤖 Specialized Agents

### MetadataAgent
- **Purpose**: Discover data schemas and metadata
- **Capabilities**: Schema discovery, data source mapping
- **Integration**: Calls Denodo MCP for metadata queries

### EntitlementAgent
- **Purpose**: Validate data access permissions
- **Capabilities**: Access validation, permission checking
- **Integration**: Basic entitlement simulation (MVP)

### DataAgent
- **Purpose**: Retrieve and process data
- **Capabilities**: Data retrieval, data processing
- **Integration**: Calls Denodo and Demo MCP servers

### AggregationAgent
- **Purpose**: Synthesize research findings
- **Capabilities**: Result synthesis, citation generation
- **Integration**: Azure OpenAI for analysis and synthesis

## 🚀 Quick Start

### Prerequisites

1. **PostgreSQL** running on localhost:5432
2. **Python 3.8+** with pip
3. **Azure OpenAI** API access

### 1. Environment Setup

Create `.env` files in each component directory with:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_API_VERSION=2024-10-21

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dataflow_agents
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 2. Install Dependencies

```bash
# Install dependencies for all components
cd data && pip install -r requirements.txt && cd ..
cd agent && pip install -r requirements.txt && cd ..
cd mcp/agent && pip install -r requirements.txt && cd ../..
```

### 3. Start the System

Use the convenient startup script:

```bash
# Start all services
bash start_agents.sh start

# Check service health
bash start_agents.sh status

# Stop all services
bash start_agents.sh stop
```

Or start manually:

```bash
# Terminal 1: Demo MCP Server
cd mcp/demo && python server.py

# Terminal 2: Denodo MCP Server  
cd mcp/denodo && python server.py

# Terminal 3: Agent Server
cd agent && python server.py

# Terminal 4: MCP Agent Server
cd mcp/agent && python server.py
```

### 4. Integration with Chat Interface

Add to `chat/mcp_config.json`:

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

## 💬 Usage Examples

### Basic Research Query

```python
# Via MCP client in chat interface
result = await mcp_client.call("multi_agent_research", {
    "query": "Show me sales data for Q4 2023",
    "research_mode": "data",
    "user_email": "user@example.com"
})
```

### Metadata Discovery

```python
# Discover available schemas
result = await mcp_client.call("multi_agent_research", {
    "query": "What tables contain customer information?",
    "research_mode": "metadata"
})
```

### Full Analysis

```python
# Complete multi-agent research
result = await mcp_client.call("multi_agent_research", {
    "query": "Analyze customer purchase trends and identify patterns",
    "research_mode": "full"
})
```

## 🔧 Research Modes

- **`metadata`**: Schema and structure discovery only
- **`data`**: Data retrieval with permission validation
- **`analysis`**: Full analysis with synthesis
- **`full`**: Complete multi-agent research (default)

## 📊 Service Endpoints

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Demo MCP | 8080 | http://localhost:8080 | Synthetic data generation |
| Denodo MCP | 8081 | http://localhost:8081 | Data source access |
| Agent Server | 8001 | http://localhost:8001 | Multi-agent orchestration |
| MCP Agent | 8082 | http://localhost:8082 | Chat interface integration |

## 📈 Monitoring & Health Checks

### Health Check Endpoints

```bash
# Check all services
curl http://localhost:8082/health

# Individual service health
curl http://localhost:8001/health  # Agent Server
curl http://localhost:8080/health  # Demo MCP
curl http://localhost:8081/health  # Denodo MCP
```

### Database Analytics

The system tracks:
- Research session statistics
- Agent execution performance
- Token usage and costs
- Success/failure rates

## 🛠️ Development

### Running Tests

```bash
# Test individual components
cd agent
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

1. Create new agent class inheriting from `BaseAgent`
2. Implement `_execute_logic` method
3. Add to `AGENT_REGISTRY` in `subagents.py`
4. Update orchestrator execution plans
5. Add database enum entries if needed

### Debugging

```bash
# Enable debug logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from agent.server import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8001)
"
```

## 🎯 MVP Features Implemented

✅ **Core Multi-Agent System**
- Specialized subagents (Metadata, Entitlement, Data, Aggregation)
- Parallel agent execution for efficiency
- Session management and tracking

✅ **Database Integration**
- PostgreSQL schema for session/execution tracking
- Connection pooling and error handling
- Analytics and monitoring support

✅ **MCP Integration**
- Single MCP server exposed to chat interface
- Integration with existing Demo and Denodo MCP servers
- Structured error handling and timeouts

✅ **Research Orchestration**
- Query intent analysis
- Dynamic execution planning
- Result synthesis and citation

✅ **Operational Support**
- Health monitoring across all components
- Startup/shutdown scripts
- Comprehensive logging and error handling

## 🔮 Future Enhancements (Phase 2)

### Langraph Integration
- Replace basic orchestrator with Langraph workflow graphs
- Dynamic graph construction based on query complexity
- Advanced error recovery and retry logic

### Advanced Features
- Chain-of-thought streaming to frontend
- Context compression for long conversations
- Intelligent agent selection based on query analysis
- Performance optimization with caching

### Production Readiness
- OpenTelemetry integration for observability
- Redis integration for active session coordination
- Advanced entitlement system integration
- Scalability improvements

## 📚 Documentation

- [`agent/README.md`](agent/README.md) - Langraph agents documentation
- [`mcp/agent/README.md`](mcp/agent/README.md) - MCP server documentation
- [`agent/implementation_plan.md`](agent/implementation_plan.md) - Detailed implementation plan

## 🤝 Contributing

1. Follow the existing code patterns and error handling
2. Add comprehensive logging for debugging
3. Update database schema if adding new data structures
4. Test integration with existing MCP servers
5. Update documentation for any new features

---

This MVP implementation provides a solid foundation for multi-agent research capabilities while maintaining compatibility with the existing chat interface and MCP ecosystem. 