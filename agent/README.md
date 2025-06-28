# LangGraph Multi-Agent Research System

A clean, modern multi-agent research system built with **LangGraph** for intelligent workflow orchestration.

## Architecture

This system uses **LangGraph StateGraph** with **Command-based handoffs** to coordinate multiple LLM-powered agents:

- **Supervisor Agent**: LLM-powered workflow coordinator
- **Metadata Agent**: Strategic metadata discovery specialist  
- **Entitlement Agent**: Security reasoning specialist
- **Data Agent**: Intelligent data tool orchestrator
- **Aggregation Agent**: Strategic data analyst

## Key Features

- **True Agentic Behavior**: Every agent uses LLM reasoning for decision-making
- **LangGraph StateGraph**: Modern state management with Message history
- **Command Handoffs**: Proper agent-to-agent transitions
- **Dynamic Tool Discovery**: Agents discover and select tools via MCP protocol
- **Intelligent Workflows**: LLM-supervised execution flow with error recovery

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure MCP servers** (copy and edit):
   ```bash
   cp mcp_config.example.json mcp_config.json
   ```

3. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export AGENT_SERVER_HOST="0.0.0.0"
   export AGENT_SERVER_PORT="8001"
   ```

4. **Start the server**:
   ```bash
   python server.py
   ```

## API Endpoints

- `POST /research` - Execute multi-agent research
- `GET /health` - System health check
- `GET /agents` - List agents and capabilities
- `GET /` - Basic system information

## Example Request

```bash
curl -X POST http://localhost:8001/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What customer data is available in the sales database?",
    "user_email": "user@example.com"
  }'
```

## Testing

Run the test script to validate the implementation:

```bash
python test_server.py
```

## Architecture Details

See detailed documentation:
- [LLM Agent Architecture](README_LLM_AGENT_ARCHITECTURE.md)
- [Data Agent LLM Tools](README_DATA_AGENT_LLM_TOOLS.md)

## What Makes This "Agentic"

Unlike simple tools or libraries, each agent:

1. **Reasons** about the task using LLM
2. **Plans** multi-step approaches  
3. **Selects** optimal tools/methods
4. **Adapts** based on results
5. **Synthesizes** insights and recommendations

This creates truly intelligent agents that think, plan, and adapt rather than just execute predefined logic.