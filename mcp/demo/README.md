# Demo MCP Server

FastMCP-powered AI tools server providing general AI assistance and synthetic data generation using Azure OpenAI or OpenAI. Features multiple transport options and enterprise-ready deployment.

## Implementation Details

### FastMCP Integration
- **Framework**: FastMCP 2.9+ with automatic protocol handling
- **Transports**: HTTP, STDIO, SSE support
- **Validation**: Automatic type-hint based parameter validation
- **Error Handling**: MCP-compliant error responses

### Features
- 🤖 **General AI assistance** with multiple modes (generate, analyze, info)
- 📊 **Synthetic data generation** for testing and development
- ⚡ **Async implementation** for optimal performance
- 🔒 **Secure authentication** with API key management
- 📝 **Comprehensive logging** with structured output
- 🏥 **Health monitoring** with detailed status reporting

## Available Tools

### 1. ask_ai
```python
@mcp.tool
async def ask_ai(question: str, mode: str = "generate") -> str:
    """
    AI assistant for general questions and tasks
    
    Args:
        question: The question or task description
        mode: Operation mode - 'generate', 'analyze', or 'info'
    
    Returns:
        AI-generated response based on the question and mode
    """
```

**Modes**:
- `generate`: Create new content, write code, compose text
- `analyze`: Analyze existing data, review code, provide insights  
- `info`: Provide factual information, explanations, tutorials

### 2. generate_synthetic_data
```python
@mcp.tool
async def generate_synthetic_data(data_type: str, count: int = 10) -> str:
    """
    Generate realistic synthetic data for testing and development
    
    Args:
        data_type: Type of data to generate (people, companies, products, etc.)
        count: Number of records to generate (1-100)
    
    Returns:
        JSON string containing generated synthetic data
    """
```

**Supported Data Types**:
- `people`: Names, ages, emails, addresses, occupations
- `companies`: Business info, revenue, industry, locations
- `products`: Product details, pricing, categories, specs
- `events`: Conferences, meetings, workshops with attendees
- `sales`: Transaction data, customer info, metrics
- `surveys`: Response data, demographics, satisfaction scores

## Setup & Configuration

### Installation
```bash
cd mcp/demo
pip install -r requirements.txt
cp .env.template .env
```

### Environment Configuration
```env
# Azure OpenAI (recommended)
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# OR OpenAI
OPENAI_API_KEY=your-openai-key

# Server Configuration
LOG_LEVEL=INFO
PORT=8081
HOST=0.0.0.0
```

### Running the Server

**FastMCP Implementation**:
```bash
# HTTP transport (web services)
python fastmcp_main.py --transport http --port 8081

# STDIO transport (Claude Desktop)
python fastmcp_main.py --transport stdio

# SSE transport (streaming)  
python fastmcp_main.py --transport sse --port 8081

# With custom configuration
python fastmcp_main.py --transport http --port 8082 --log-level DEBUG
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
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Call AI tool**:
```bash
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ask_ai",
      "arguments": {
        "question": "Explain machine learning",
        "mode": "info"
      }
    },
    "id": 2
  }'
```

**Generate synthetic data**:
```bash
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "generate_synthetic_data",
      "arguments": {
        "data_type": "people",
        "count": 5
      }
    },
    "id": 3
  }'
```

### Health Check
```bash
curl http://localhost:8081/health

# Response:
{
  "status": "healthy",
  "server": "Demo Server",
  "version": "2.9.0",
  "tools": 2,
  "ai_provider": "azure_openai",
  "uptime": "0:15:42"
}
```

## Implementation Architecture

### FastMCP Server (187 lines)
```python
from fastmcp import FastMCP
import asyncio
import json

# Initialize FastMCP server
mcp = FastMCP("Demo Server")

@mcp.tool
async def ask_ai(question: str, mode: str = "generate") -> str:
    """AI assistant tool implementation"""
    client = get_ai_client()  # Azure OpenAI or OpenAI
    
    system_prompts = {
        "generate": "You are a creative AI assistant...",
        "analyze": "You are an analytical AI assistant...", 
        "info": "You are an informative AI assistant..."
    }
    
    response = await client.chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": system_prompts[mode]},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

@mcp.tool
async def generate_synthetic_data(data_type: str, count: int = 10) -> str:
    """Synthetic data generation implementation"""
    if count > 100:
        raise ValueError("Count cannot exceed 100")
    
    prompt = f"Generate {count} realistic {data_type} records in JSON format..."
    response = await ask_ai(prompt, "generate")
    
    # Validate and format JSON
    try:
        data = json.loads(response)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError:
        # Fallback: extract JSON from response
        return extract_json_from_text(response)

if __name__ == "__main__":
    mcp.run()  # FastMCP handles everything else!
```

### Migration Benefits

**Code Reduction**: From 758 lines to 187 lines (75% reduction)

**Original Implementation Issues**:
- Manual JSON-RPC protocol handling (150+ lines)
- Custom parameter validation (50+ lines)
- Manual error formatting (30+ lines)
- CORS handling (20+ lines)
- Health check implementation (25+ lines)

**FastMCP Automatic Features**:
- ✅ Protocol handling (JSON-RPC 2.0)
- ✅ Parameter validation (from type hints)
- ✅ Error formatting (MCP-compliant)
- ✅ CORS handling (configurable)
- ✅ Health checks (built-in)
- ✅ Multiple transports (HTTP/STDIO/SSE)

## Development

### Project Structure
```
demo/
├── fastmcp_server.py          # New FastMCP implementation (187 lines)
├── fastmcp_main.py            # FastMCP entry point with CLI
├── test_migration.py          # Migration validation tests
├── Dockerfile.fastmcp         # FastMCP container config
├── requirements.txt           # Updated dependencies with FastMCP
├── .env.template              # Environment variables template
├── main.py                    # Legacy entry point
├── server.py                  # Legacy implementation (758 lines)
└── README.md                  # This file
```

### Adding New Tools

```python
@mcp.tool
async def new_custom_tool(param1: str, param2: int = 5) -> str:
    """Description for the LLM about what this tool does"""
    # Type hints automatically become parameter validation
    # Docstring becomes tool description
    # Implementation logic only
    return f"Processed {param1} with value {param2}"
```

### Testing

**Validate Migration**:
```bash
# Start both servers
python main.py --port 8080 &           # Legacy
python fastmcp_main.py --port 8081 &   # FastMCP

# Run comparison tests
python test_migration.py --original-port 8080 --fastmcp-port 8081

# Expected output:
# ✅ Tool parity: Both servers expose the same tools
# ✅ Both servers are functional
# ✅ Migration validation PASSED
```

**Manual Testing**:
```bash
# Test tool functionality
python -c "
from fastmcp_server import mcp
print('Available tools:', [tool.name for tool in mcp.tools])
"

# Test with different AI providers
AZURE_OPENAI_API_KEY=xxx python fastmcp_main.py --transport http
OPENAI_API_KEY=xxx python fastmcp_main.py --transport http
```

## Deployment

### Docker
```bash
# Build FastMCP container
docker build -f Dockerfile.fastmcp -t dataflow/demo-mcp:fastmcp .

# Run with environment
docker run -p 8081:8081 \
  -e AZURE_OPENAI_API_KEY=xxx \
  -e AZURE_OPENAI_ENDPOINT=xxx \
  dataflow/demo-mcp:fastmcp

# Docker Compose
docker-compose --profile fastmcp up -d
```

### Production Configuration
```yaml
# docker-compose.yml
services:
  demo-mcp-fastmcp:
    build:
      context: ./mcp/demo
      dockerfile: Dockerfile.fastmcp
    environment:
      TRANSPORT: http
      PORT: 8081
      LOG_LEVEL: INFO
      AZURE_OPENAI_API_KEY: ${AZURE_OPENAI_API_KEY}
      AZURE_OPENAI_ENDPOINT: ${AZURE_OPENAI_ENDPOINT}
    ports:
      - "8081:8081"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Troubleshooting

### Common Issues

**AI Provider Configuration**:
```bash
# Test Azure OpenAI connection
python -c "
import os
from openai import AzureOpenAI
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    api_version='2024-02-15-preview'
)
print('Connection test:', client.models.list())
"
```

**FastMCP Issues**:
```bash
# Check FastMCP installation
python -c "import fastmcp; print(fastmcp.__version__)"

# Enable debug logging
LOG_LEVEL=DEBUG python fastmcp_main.py

# Test tool calls directly
python -c "
import asyncio
from fastmcp_server import ask_ai
result = asyncio.run(ask_ai('test question'))
print(result)
"
```

**Performance Issues**:
- Monitor memory usage during large data generation
- Use connection pooling for high-throughput scenarios
- Consider caching for repeated synthetic data requests
- Enable async logging for better performance
