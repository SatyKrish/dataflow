# Multi-Agent System - Modular Structure

This document explains the new modular structure of the multi-agent system, which has been refactored from a single large file into focused, maintainable modules.

## File Structure

```
agent/
├── base_agent.py           # Abstract base class and common functionality
├── metadata_agent.py       # Schema and metadata discovery agent
├── entitlement_agent.py    # Permission validation agent  
├── data_agent.py          # Data retrieval and processing agent
├── aggregation_agent.py   # Result synthesis agent
├── agent_registry.py      # Agent registry and factory functions
├── db_client.py           # Database client and agent types
└── README_AGENTS_STRUCTURE.md  # This documentation
```

## Module Descriptions

### `base_agent.py`
Contains the `BaseAgent` abstract class that provides:
- Common execution framework with database tracking
- Error handling and status management
- LLM integration helper methods
- Abstract `_execute_logic()` method for implementation by subclasses

### `metadata_agent.py`
**MetadataAgent** - Specialized for data schema discovery:
- Identifies relevant data sources
- Discovers schemas, tables, and data structures
- Maps relationships between data sources
- Provides exploration recommendations

### `entitlement_agent.py`
**EntitlementAgent** - Handles access permission validation:
- Validates user permissions for data sources
- Checks access rights for specific tables/datasets
- Identifies data governance restrictions
- Provides clear access status and limitations

### `data_agent.py`
**DataAgent** - Manages data retrieval and processing:
- Retrieves data from approved sources
- Processes and cleans retrieved data
- Applies necessary transformations
- Ensures data quality and completeness

### `aggregation_agent.py`
**AggregationAgent** - Synthesizes results from other agents:
- Combines findings from all other agents
- Identifies key insights and patterns
- Provides comprehensive conclusions
- Generates citations and source attributions

### `agent_registry.py`
Central registry and factory system:
- `AGENT_REGISTRY`: Maps agent types to their classes
- `create_agent()`: Factory function to instantiate agents
- `get_available_agent_types()`: Lists all available agent types
- `get_agent_class()`: Returns agent class for a given type

### `db_client.py`
Database client and core type definitions:
- `DatabaseClient`: PostgreSQL client for agent operations
- `AgentType`, `ExecutionStatus`, `SessionStatus`: Core enums
- Agent execution tracking and database operations

### Removed Files
The original monolithic `subagents.py` file has been completely removed. All imports have been updated to use the individual agent modules directly.

## Benefits of This Structure

1. **Improved Maintainability**: Each agent is in its own focused module
2. **Better Testing**: Individual agents can be tested in isolation
3. **Easier Extension**: New agents can be added without modifying existing code
4. **Clear Separation of Concerns**: Each module has a single responsibility
5. **Clean Imports**: Direct imports from individual modules for better clarity
6. **Better Documentation**: Each module can have focused documentation

## Usage Examples

### Using the Registry (Recommended)
```python
from agent_registry import create_agent
from db_client import AgentType

# Create an agent using the factory
metadata_agent = create_agent(AgentType.METADATA)
result = await metadata_agent.execute(session_id, task_description, context)
```

### Direct Import
```python
from metadata_agent import MetadataAgent

# Direct instantiation
agent = MetadataAgent()
result = await agent.execute(session_id, task_description, context)
```

### Current Import Style (After Refactoring)
```python
from metadata_agent import MetadataAgent
from agent_registry import create_agent
from db_client import AgentType, db_client
# Clean, direct imports from individual modules
```

## Adding New Agents

To add a new agent:

1. Create a new file: `agent/new_agent.py`
2. Inherit from `BaseAgent` and implement `_execute_logic()`
3. Add the agent to `AGENT_REGISTRY` in `agent_registry.py`
4. Update any files that need to import the new agent
5. Update the documentation

## Migration Notes

The refactoring has been completed and all imports have been updated to use the individual agent modules directly. The original monolithic `subagents.py` file has been removed for cleaner architecture. 