# Data Agent with LLM-Based Tool Selection

## Overview

The Data Agent has been enhanced to use **LLM-based intelligent tool selection** instead of hardcoded tool calls. It now:

1. **Dynamically discovers tools** from configured MCP servers
2. **Uses LLM to analyze queries** and select appropriate tools
3. **Executes selected tools** in parallel or sequentially
4. **Synthesizes results** using LLM for comprehensive analysis

## How It Works

### 1. Tool Discovery
The Data Agent automatically discovers available tools from all configured MCP servers:

```python
# Discovers tools from mcp_config.json servers
discovered_tools = await data_agent._discover_tools_from_mcp_servers()
```

### 2. LLM Tool Selection
The LLM analyzes the query and available tools to make intelligent selections:

```python
# LLM selects the best tools for the task
tool_selection = await data_agent._llm_select_tools(task_description, context)
```

**Selection Criteria:**
- **Relevance**: Does the tool match the request?
- **Server Capability**: What is each MCP server designed for?
- **Input Schema**: Does the tool accept the right parameters?
- **Completeness**: Do selected tools provide comprehensive coverage?

### 3. Tool Execution
Selected tools are executed according to the LLM's strategy:

```python
# Execute tools (parallel or sequential)
tool_results = await data_agent._execute_selected_tools(selection, task, context)
```

### 4. Result Synthesis
The LLM analyzes all results and provides comprehensive insights:

```python
# LLM analyzes and synthesizes results
final_analysis = await data_agent._llm_analyze_results(results, task, context)
```

## Configuration

### MCP Server Configuration

Add new data sources by configuring MCP servers in `mcp_config.json`:

```json
{
  "servers": {
    "demoAgent": {
      "type": "http",
      "url": "http://demo-mcp:8080/mcp",
      "description": "AI-powered synthetic data generation"
    },
    "denodoAgent": {
      "type": "http", 
      "url": "http://denodo-mcp:8081/mcp",
      "description": "Enterprise data warehouse queries"
    },
    "newDataSource": {
      "type": "http",
      "url": "http://new-source:8082/mcp",
      "description": "Your custom data source"
    }
  }
}
```

### Environment Variables

Configure the MCP config path:

```bash
export MCP_CONFIG_PATH="/path/to/mcp_config.json"
```

## Example Usage

### Query Examples

**Enterprise Data Request:**
```
"Retrieve customer sales data for Q4 2023"
```
→ LLM selects: `denodoAgent:denodo_query`

**Synthetic Data Request:**
```
"Generate sample customer data for testing"
```
→ LLM selects: `demoAgent:ask_ai`

**Mixed Analysis:**
```
"Analyze customer behavior with real data and examples"
```
→ LLM selects: `denodoAgent:denodo_query`, `demoAgent:ask_ai`

### Response Structure

```json
{
  "tool_discovery": {
    "discovered_tools": 4,
    "available_servers": ["demoAgent", "denodoAgent"]
  },
  "tool_selection_reasoning": {
    "selected_tools": ["denodoAgent:denodo_query"],
    "reasoning": {
      "denodoAgent:denodo_query": "Matches enterprise data requirements"
    },
    "execution_strategy": "parallel",
    "confidence": 0.9
  },
  "tool_executions": [
    {
      "tool": "denodoAgent:denodo_query",
      "status": "success",
      "result": { "data": [...] },
      "server": "denodoAgent"
    }
  ],
  "final_analysis": {
    "summary": "Retrieved 150 customer records from Q4 2023",
    "key_insights": ["Sales increased 15% from Q3", "..."],
    "recommendations": ["Focus on top-performing segments", "..."]
  }
}
```

## Testing

Run the test suite to verify functionality:

```bash
cd agent
python test_data_agent.py
```

The test includes:
- **MCP Configuration Loading** - Verifies config is loaded correctly
- **Tool Discovery** - Tests dynamic tool discovery from MCP servers
- **LLM Tool Selection** - Tests intelligent tool selection for different scenarios
- **Full Execution Simulation** - End-to-end test with mock responses

## Adding New Data Sources

### 1. Create MCP Server
Implement a new MCP server with relevant tools:

```python
@mcp.tool
async def my_data_tool(query: str) -> dict:
    """Description of what this tool does"""
    # Your data retrieval logic
    return {"data": [...]}
```

### 2. Add to Configuration
Add the server to `mcp_config.json`:

```json
{
  "myDataSource": {
    "type": "http",
    "url": "http://my-server:8080/mcp",
    "description": "Description for LLM context"
  }
}
```

### 3. Test Discovery
The Data Agent will automatically discover and use your new tools!

## Benefits

### ✅ **Simplified Architecture**
- No complex registry system
- Uses existing MCP infrastructure
- Dynamic tool discovery

### ✅ **Intelligent Selection**
- LLM analyzes query intent
- Considers tool capabilities and context
- Optimizes for relevance and completeness

### ✅ **Easy Extension**
- Add new data sources via MCP config
- No code changes required
- Automatic tool discovery

### ✅ **Flexible Execution**
- Parallel or sequential execution
- Error handling and fallbacks
- Comprehensive result synthesis

## Migration Notes

If you have existing hardcoded tool calls:

1. **Before**: Hardcoded calls to specific endpoints
2. **After**: LLM selects appropriate tools dynamically

The new approach is more flexible and intelligent while maintaining the same functionality. 