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

## Agent Directory Structure

- `orchestrator/fastmcp_server.py`: Main FastMCP orchestrator server (lead agent)
- `subagents/metadata_agent.py`: Metadata retrieval subagent
- `subagents/entitlement_agent.py`: Entitlement check subagent
- `subagents/data_agent.py`: Data retrieval subagent
- `subagents/aggregation_agent.py`: Aggregation subagent
- `subagents/persona_profiler.py`: Persona/intent detection subagent
- `subagents/citation_agent.py`: Citation/attribution subagent

All tools follow the FastMCP protocol and are implemented as async Python classes with Pydantic models for request/response validation.

## How to Run

1. Install dependencies (see above)
2. Start the orchestrator server:
   ```bash
   python -m agent.orchestrator.fastmcp_server
   ```
3. Register and run subagents as FastMCP tools as needed.

## Development Notes
- All code follows `copilot_rules.md` for style, async, and security.
- Subagents are modular and can be extended or replaced.
- See `implementation_plan.md` for architecture and workflow details.