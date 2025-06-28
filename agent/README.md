# LangGraph Multi-Agent Research System

A clean, modern multi-agent research system built with **LangGraph** for intelligent workflow orchestration. Each agent uses LLM reasoning for true agentic behavior rather than simple tool execution.

## 🎯 What Makes This "Agentic"

Unlike simple tools or libraries, each agent:

1. **Reasons** about the task using LLM
2. **Plans** multi-step approaches  
3. **Selects** optimal tools/methods
4. **Adapts** based on results
5. **Synthesizes** insights and recommendations

### Agent vs Tool/Library

| Aspect | Tool/Library | Agent |
|--------|--------------|-------|
| **Decision Making** | Follows predefined logic | Uses LLM to reason and decide |
| **Adaptability** | Fixed behavior | Adapts approach based on context |
| **Problem Solving** | Executes predetermined steps | Plans and strategizes dynamically |
| **Error Handling** | Basic fallbacks | Intelligent recovery and adaptation |

## 🏗️ Architecture

This system uses **LangGraph StateGraph** with **Command-based handoffs** to coordinate multiple LLM-powered agents:

- **Supervisor Agent**: LLM-powered workflow coordinator with intelligent routing
- **Metadata Agent**: Strategic metadata discovery specialist using adaptive exploration
- **Entitlement Agent**: Security reasoning specialist with compliance analysis
- **Data Agent**: Intelligent data tool orchestrator with dynamic MCP discovery
- **Aggregation Agent**: Strategic data analyst generating actionable insights

### LangGraph Features

- **StateGraph**: Modern state management with message history
- **Command Handoffs**: Proper agent-to-agent transitions
- **LLM Supervision**: Intelligent workflow coordination
- **Error Recovery**: Adaptive error handling and fallback mechanisms
- **Message-Based Communication**: Agent conversation tracking

## ✨ Key Features

- **True Agentic Behavior**: Every agent uses LLM reasoning for decision-making
- **Dynamic Tool Discovery**: Agents discover and select tools via MCP protocol
- **Intelligent Workflows**: LLM-supervised execution flow with error recovery
- **Adaptive Execution**: Agents can retry, fallback, or change approach based on results
- **Context-Aware Decisions**: Consider task requirements, resources, and business context

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MCP Servers
Copy and edit the configuration:
```bash
cp mcp_config.example.json mcp_config.json
```

Example configuration:
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
    }
  }
}
```

### 3. Set Environment Variables
```bash
export OPENAI_API_KEY="your-api-key"
export AGENT_SERVER_HOST="0.0.0.0"
export AGENT_SERVER_PORT="8001"
export MCP_CONFIG_PATH="./mcp_config.json"
```

### 4. Start the Server
```bash
python server.py
```

## 📡 API Endpoints

- `POST /research` - Execute multi-agent research
- `GET /health` - System health check
- `GET /agents` - List agents and capabilities
- `GET /` - Basic system information

### Example Request

```bash
curl -X POST http://localhost:8001/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What customer data is available in the sales database?",
    "user_email": "user@example.com"
  }'
```

### Response Structure

```json
{
  "session_id": "session_20240101_120000_abc123",
  "workflow_status": "completed",
  "metadata_results": {
    "summary": "Discovered 15 tables with customer data",
    "schemas": [...],
    "recommendations": [...]
  },
  "entitlement_results": {
    "access_status": "granted",
    "security_analysis": {...},
    "compliance_requirements": [...]
  },
  "data_results": {
    "tool_selection_reasoning": {...},
    "tool_executions": [...],
    "final_analysis": {...}
  },
  "aggregation_results": {
    "synthesis": "Comprehensive customer data analysis",
    "insights": [...],
    "recommendations": [...]
  },
  "messages": [...]
}
```

## 🧠 Agent Architecture Deep Dive

### Metadata Agent - Intelligent Discovery Strategist

**LLM-Driven Capabilities:**
- **Strategic Planning**: Creates tailored discovery strategies based on task requirements
- **Method Selection**: Chooses optimal discovery approaches (Denodo, filesystem, APIs, etc.)
- **Adaptive Execution**: Can stop early if sufficient metadata discovered
- **Quality Assessment**: Identifies data quality and access risks
- **Business Context**: Connects metadata findings to business requirements

```python
# LLM-driven reasoning example
async def _execute_logic(self, task, context):
    # 1. LLM analyzes task and creates discovery strategy
    strategy = await self._llm_create_discovery_strategy(task, context)
    
    # 2. LLM selects optimal discovery methods
    methods = await self._llm_select_discovery_methods(strategy, task, context)
    
    # 3. Execute with intelligent adaptation
    results = await self._execute_discovery_methods(methods, strategy, context)
    
    # 4. LLM synthesizes findings into actionable insights
    synthesis = await self._llm_synthesize_metadata(results, task, context)
```

### Entitlement Agent - Security Reasoning Specialist

**LLM-Driven Capabilities:**
- **Threat Analysis**: Identifies security implications and threat vectors
- **Compliance Reasoning**: Determines applicable regulations (GDPR, CCPA, HIPAA, SOX)
- **Risk Assessment**: Multi-dimensional risk evaluation
- **Framework Selection**: Chooses appropriate security models (RBAC, ABAC, Zero Trust)
- **Intelligent Decisions**: Context-aware access control with conditions

### Data Agent - Intelligent Tool Orchestrator

**LLM-Driven Capabilities:**
- **Dynamic Tool Discovery**: Loads tools from MCP configuration dynamically
- **Intelligent Selection**: Chooses tools based on capabilities and context
- **Adaptive Execution**: Can retry, fallback, or change approach based on results
- **Result Synthesis**: Combines data from multiple sources intelligently

#### How Data Agent Works

1. **Tool Discovery**: Automatically discovers available tools from all configured MCP servers
2. **LLM Tool Selection**: Analyzes query and selects appropriate tools based on relevance and capabilities
3. **Strategic Execution**: Executes tools in parallel or sequentially based on LLM strategy
4. **Result Synthesis**: LLM analyzes all results for comprehensive insights

Example tool selection reasoning:
```
Query: "Retrieve customer sales data for Q4 2023"
→ LLM selects: denodoAgent:denodo_query (enterprise data capability)

Query: "Generate sample customer data for testing"  
→ LLM selects: demoAgent:ask_ai (synthetic data generation)

Query: "Analyze customer behavior with real data and examples"
→ LLM selects: denodoAgent:denodo_query + demoAgent:ask_ai (mixed analysis)
```

### Aggregation Agent - Strategic Data Analyst

**LLM-Driven Capabilities:**
- **Strategic Planning**: Creates comprehensive analysis strategies
- **Framework Selection**: Chooses analytical approaches (statistical, pattern recognition, BI, predictive)
- **Pattern Recognition**: Identifies trends, anomalies, and relationships
- **Insight Generation**: Converts patterns into actionable business insights
- **Executive Reports**: Produces comprehensive analytical summaries

## 🧪 Testing

Run the test script to validate the implementation:

```bash
python test_server.py
```

Test the data agent specifically:
```bash
python test_data_agent.py
```

## 🔧 Adding New Data Sources

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

## 🎯 Common LLM-Driven Patterns

### Multi-Step Reasoning Chain
Each agent follows a structured reasoning chain:
1. **Analyze** the task and context
2. **Plan** the optimal approach
3. **Select** appropriate methods/tools
4. **Execute** with intelligent adaptation
5. **Synthesize** results into insights
6. **Recommend** next steps or actions

### Adaptive Execution
Agents can:
- **Early Termination**: Stop when sufficient information is gathered
- **Retry Logic**: Attempt different approaches if initial attempts fail
- **Escalation**: Escalate to human or other agents when needed
- **Context Learning**: Learn from previous results within the session

### Fallback Mechanisms
When LLM calls fail, agents have intelligent fallbacks:
- **Sequential Logic**: Fall back to predetermined sequential execution
- **Error Recovery**: Attempt alternative approaches
- **Graceful Degradation**: Continue with partial results when appropriate

## 🏃‍♂️ Performance Benefits

- **Parallel Execution**: Multiple agents can run simultaneously
- **Intelligent Routing**: LLM supervisor routes tasks optimally
- **Dynamic Adaptation**: Agents adapt strategies based on real-time results
- **Context Compression**: Agents synthesize large amounts of data into focused insights
- **Tool Optimization**: Smart tool selection reduces unnecessary API calls

## 📋 System Requirements

- Python 3.9+
- LangGraph 0.2.74+
- OpenAI API access
- MCP servers for data sources
- PostgreSQL (optional, for session tracking)
- Redis (optional, for caching)

This creates truly intelligent agents that think, plan, and adapt rather than just execute predefined logic.