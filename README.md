# DataFlow

<div align="center">

![DataFlow Logo](./chat/public/data-flow-logo.svg)

**A comprehensive AI-powered data platform for natural language database interactions and intelligent chat experiences**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](chat/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](agent/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.9+-green.svg)](mcp/)

</div>

## 🌟 Overview

DataFlow is a modern, full-stack platform that bridges the gap between natural language and data systems. It combines AI-powered chat interfaces, streaming data processing, and Model Context Protocol (MCP) servers to enable intuitive data interactions through conversational AI.

> **🚀 Migration Complete!** The MCP servers have been successfully migrated to **FastMCP 2.9+**, resulting in 69% code reduction, enhanced features, and future-ready architecture.

### Key Capabilities

- **🤖 Intelligent Chat Interface** - Next.js-based modern UI with real-time streaming and artifacts
- **📊 Rich Data Visualization** - Interactive charts, tables, and Mermaid diagrams  
- **🔌 Modern MCP Integration** - FastMCP-powered servers with multiple transport options
- **🚀 Streaming Architecture** - Real-time data processing with AutoGen Core
- **🔐 Enterprise Authentication** - Azure SSO integration with NextAuth.js
- **🐳 Production-Ready Deployment** - Full Docker and Kubernetes support

## 🏗️ Architecture

DataFlow consists of four main components working together seamlessly:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat UI       │    │   Agent Core    │    │   MCP Servers   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (FastMCP)     │
│                 │    │                 │    │                 │
│ • Real-time UI  │    │ • AutoGen Core  │    │ • Demo Server   │
│ • Artifacts     │    │ • Streaming     │    │ • Denodo AI SDK │
│ • Auth (Azure)  │    │ • AI Models     │    │ • HTTP/STDIO    │
│ • Charts & Code │    │ • Visualization │    │ • Natural Lang  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Multi-Agent System Architecture

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

### Specialized Agents

- **MetadataAgent**: Discover data schemas and metadata (schema discovery, data source mapping, Denodo MCP integration)
- **EntitlementAgent**: Validate data access permissions (access validation, permission checking, entitlement simulation)
- **DataAgent**: Retrieve and process data (data retrieval, processing, calls Denodo and Demo MCP)
- **AggregationAgent**: Synthesize research findings (result synthesis, citation generation, uses Azure OpenAI)

## 🚀 Quick Start

### Prerequisites
- PostgreSQL running on localhost:5432
- Python 3.8+ with pip
- Azure OpenAI API access

### 1. Environment Setup

**Option A: Use Environment Template (Recommended)**
```bash
cd agent
cp env.template .env
# Edit .env with your values
```

**Option B: Export Variables Directly**
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
export AZURE_OPENAI_API_VERSION="2024-10-21"
# Optional: If not provided, Azure AD authentication will be used
export AZURE_OPENAI_API_KEY="your-api-key"
```

### 2. Install Dependencies

```bash
cd data && pip install -r requirements.txt && cd ..
cd agent && pip install -r requirements.txt && cd ..
cd mcp/agent && pip install -r requirements.txt && cd ../..
```

### 3. Start the System

Use the convenient startup script:
```bash
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

### Usage Examples

**Basic Research Query**
```python
result = await mcp_client.call("multi_agent_research", {
    "query": "Show me sales data for Q4 2023",
    "research_mode": "data",
    "user_email": "user@example.com"
})
```

**Metadata Discovery**
```python
result = await mcp_client.call("multi_agent_research", {
    "query": "What tables contain customer information?",
    "research_mode": "metadata"
})
```

**Full Analysis**
```python
result = await mcp_client.call("multi_agent_research", {
    "query": "Analyze customer purchase trends and identify patterns",
    "research_mode": "full"
})
```

### Research Modes
- `metadata`: Schema and structure discovery only
- `data`: Data retrieval with permission validation
- `analysis`: Full analysis with synthesis
- `full`: Complete multi-agent research (default)

### Service Endpoints
| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Demo MCP | 8080 | http://localhost:8080 | Synthetic data generation |
| Denodo MCP | 8081 | http://localhost:8081 | Data source access |
| Agent Server | 8001 | http://localhost:8001 | Multi-agent orchestration |
| MCP Agent | 8082 | http://localhost:8082 | Chat interface integration |

### Monitoring & Health Checks

**Health Check Endpoints**
```bash
curl http://localhost:8082/health
curl http://localhost:8001/health  # Agent Server
curl http://localhost:8080/health  # Demo MCP
curl http://localhost:8081/health  # Denodo MCP
```

**Database Analytics**
- Research session statistics
- Agent execution performance
- Token usage and costs
- Success/failure rates

### Development

**Running Tests**
```bash
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

**Adding New Agents**
1. Create new agent class inheriting from `BaseAgent`
2. Implement `_execute_logic` method
3. Add to `AGENT_REGISTRY` in `subagents.py`
4. Update orchestrator execution plans
5. Add database enum entries if needed

**Debugging**
```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from agent.server import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8001)
"
```

### MVP Features Implemented

- Core Multi-Agent System (specialized subagents, parallel execution, session management)
- Database Integration (PostgreSQL schema, pooling, analytics)
- MCP Integration (single MCP server, integration with Demo/Denodo, error handling)
- Research Orchestration (query analysis, dynamic planning, result synthesis)
- Operational Support (health monitoring, scripts, logging)

### Future Enhancements (Phase 2)
- Langraph workflow graphs, dynamic graph construction, advanced error recovery
- Chain-of-thought streaming, context compression, intelligent agent selection
- OpenTelemetry, Redis, advanced entitlement, scalability

---

This MVP implementation provides a solid foundation for multi-agent research capabilities while maintaining compatibility with the existing chat interface and MCP ecosystem.

## 📁 Project Structure

```
dataflow/
├── 📁 chat/                    # Next.js Chat Interface
│   ├── 🎨 components/         # React components (UI, charts, artifacts)
│   │   ├── ui/               # shadcn/ui base components
│   │   ├── auth/             # Authentication components
│   │   └── mcp/              # MCP-specific components
│   ├── 📱 app/                # Next.js app router
│   │   ├── api/              # API routes (chat, auth, mcp)
│   │   ├── auth/             # Authentication pages
│   │   └── test/             # Test pages
│   ├── 🔧 lib/                # Utilities and configurations
│   │   ├── auth.ts           # NextAuth configuration
│   │   ├── chat-storage.ts   # Session persistence
│   │   ├── mcp/              # MCP client utilities
│   │   └── llm/              # LLM provider integrations
│   ├── 🎯 types/              # TypeScript definitions
│   └── 🎨 styles/             # Global styles and themes
│
├── 🤖 agent/                   # FastAPI Agent Core
│   ├── app.py                 # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── model_config.yaml      # AI model configuration template
│
├── 🔌 mcp/                     # FastMCP Servers (Migration Complete)
│   ├── demo/                  # Demo AI tools server
│   │   ├── fastmcp_server.py  # New FastMCP implementation (187 lines)
│   │   ├── fastmcp_main.py    # FastMCP entry point
│   │   ├── test_migration.py  # Migration validation
│   │   ├── Dockerfile.fastmcp # FastMCP container
│   │   └── requirements.txt   # Updated dependencies
│   ├── denodo/                # Denodo AI SDK server
│   │   ├── fastmcp_server.py  # New FastMCP implementation (201 lines)
│   │   ├── fastmcp_main.py    # FastMCP entry point
│   │   ├── Dockerfile.fastmcp # FastMCP container
│   │   └── requirements.txt   # Updated dependencies
│   └── README.md              # MCP servers documentation
│
├── 🚀 deploy/                  # Deployment configurations
│   └── helm/                  # Kubernetes Helm charts
│
├── 📊 logs/                    # Application logs and demos
└── 🐳 docker-compose.yml      # Container orchestration
```

### FastMCP Migration Benefits

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| **Demo Server** | 758 lines | 187 lines | 75% reduction |
| **Denodo Server** | 511 lines | 201 lines | 61% reduction |
| **Protocol Support** | HTTP only | HTTP/STDIO/SSE | 3x more options |
| **Validation** | Manual | Automatic | Type-driven |
| **Standards** | Custom | MCP 2024-11-05 | Full compliance |

## 🔧 Configuration

### Environment Variables

#### Chat Interface
```env
# Azure Authentication
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000

# API Endpoints
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MCP_URL=http://localhost:8081
```

#### Agent Core
```yaml
# model_config.yaml
models:
  - model: "gpt-4"
    api_key: "your-openai-api-key"
    base_url: "https://api.openai.com/v1"
  - model: "gpt-4o"
    api_key: "your-azure-openai-key"
    base_url: "https://your-endpoint.openai.azure.com"
    api_version: "2024-02-15-preview"
```

#### MCP Servers

**Demo Server (AI Tools)**
```env
# Azure OpenAI (recommended)
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-10-21

# Or OpenAI
OPENAI_API_KEY=your-openai-key

# Server Configuration
LOG_LEVEL=INFO
PORT=8081
```

**Denodo Server (Database)**
```env
# Denodo AI SDK Configuration
DENODO_AI_SDK_ENDPOINT=http://localhost:8008
DENODO_AI_SDK_USER=admin
DENODO_AI_SDK_PASSWORD=admin
DENODO_AI_SDK_VERIFY_SSL=false

# Server Configuration  
LOG_LEVEL=INFO
PORT=8082
```

### FastMCP Transport Options

FastMCP supports multiple transport protocols:

```bash
# HTTP for web clients (default)
python fastmcp_main.py --transport http --port 8081

# STDIO for Claude Desktop integration
python fastmcp_main.py --transport stdio

# SSE for streaming (legacy support)
python fastmcp_main.py --transport sse --port 8081
```

## 🌟 Features

### Chat Interface
- ✨ **Real-time Streaming** - Live AI responses with typewriter animations
- 📊 **Rich Artifacts** - Interactive code blocks, charts, and Mermaid diagrams
- 🔐 **Azure SSO** - Enterprise-grade authentication with NextAuth.js
- 💾 **Session Persistence** - Automatic chat history preservation
- 📱 **Responsive Design** - Optimized for desktop and mobile
- 🎨 **Modern UI** - Built with shadcn/ui and Tailwind CSS
- ⚡ **Performance Optimized** - High-performance streaming with monitoring

### Agent Core  
- 🔄 **Streaming API** - Real-time response generation compatible with Vercel AI SDK
- 📈 **Data Visualization** - Advanced charting with Recharts integration
- 💻 **Code Generation** - Syntax-highlighted code blocks with copy functionality
- 🎨 **Diagram Support** - Mermaid flowcharts, sequence diagrams, and more
- 📊 **Structured Output** - Tables with sorting, filtering, and column types
- 🌐 **CORS Enabled** - Cross-origin support for frontend integration

### MCP Integration (FastMCP 2.9+)
- 🗄️ **Natural Language DB Queries** - Ask questions in plain English
- 🤖 **AI-Powered Tools** - General AI assistance with context awareness
- 📊 **Synthetic Data Generation** - Create realistic test data for development
- 🔌 **Multiple Transports** - HTTP, STDIO, SSE protocol support
- 🏢 **Enterprise Data Access** - Denodo AI SDK integration for data virtualization
- 📋 **Comprehensive Logging** - Detailed operation tracking and health monitoring
- 🔒 **Secure Authentication** - Built-in auth support with extensible middleware

### Available MCP Tools

#### Demo Server Tools
- **ask_ai(question, mode)** - General AI assistance
  - `generate`: Create new content
  - `analyze`: Analyze existing data  
  - `info`: Provide information
- **generate_synthetic_data(type, count)** - Create test data
  - People, companies, products, events, sales, surveys

#### Denodo Server Tools  
- **denodo_query(query, mode)** - Natural language database queries
  - `data`: Execute data queries
  - `metadata`: Explore database schema and structure

## 🛠️ Development

### FastMCP Migration Status ✅

The DataFlow platform has successfully migrated to FastMCP 2.9+:

**Migration Benefits**:
- **69% code reduction** - From 1,269 to 388 lines across both servers
- **Enhanced features** - Multiple transports, validation, error handling
- **Future-ready** - Middleware, auth, composition support ready
- **Standards compliance** - Full MCP 2024-11-05 specification

**Validation**:
```bash
# Test migration success
cd mcp/demo && python test_migration.py
# Expected: ✅ Migration validation PASSED
```

### Adding New MCP Servers

With FastMCP, creating new servers is much simpler:

```python
# Create new server: mcp/myserver/fastmcp_server.py
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
async def my_tool(param: str) -> str:
    """My custom tool description"""
    return f"Result: {param}"

if __name__ == "__main__":
    mcp.run(transport="http", port=8083)
```

### Customizing the Chat Interface

The chat interface uses modern React patterns:

**Key Components**:
- **`chat-interface.tsx`** - Main chat UI with streaming
- **`artifacts-panel.tsx`** - Code, charts, and diagram rendering
- **`message-bubble.tsx`** - Individual message display
- **`chart-renderer.tsx`** - Interactive chart visualization
- **`settings-dialog.tsx`** - Configuration and preferences

**Custom Hooks**:
- **`use-resize-optimization.ts`** - Performance optimization
- **`use-mobile.tsx`** - Mobile responsiveness
- **`use-toast.ts`** - Notification system

**Utilities**:
- **`auth-utils.ts`** - Authentication helpers
- **`chat-storage.ts`** - Session persistence
- **`artifact-detector.ts`** - Content type detection

### Extending Agent Capabilities

Add new agent features by:

1. **Extending FastAPI endpoints** in `/agent/app.py`
2. **Adding AI model configurations** in `model_config.yaml`
3. **Implementing data processing pipelines** for specific use cases
4. **Creating custom visualization types** for domain-specific data

### Local Development Tips

**Chat Interface**:
```bash
# Hot reload development
cd chat && npm run dev

# Type checking  
npm run type-check

# Linting and formatting
npm run lint && npm run format
```

**MCP Servers**:
```bash
# Development with auto-reload
cd mcp/demo
pip install -e .
python fastmcp_main.py --reload

# Testing tools individually
python -c "from fastmcp_server import mcp; print(mcp.list_tools())"
```

**Debugging**:
- Enable detailed logging: `LOG_LEVEL=DEBUG`
- Use health check endpoints: `GET /health`
- Monitor performance with built-in metrics
- Check Docker logs: `docker logs dataflow-mcp-demo`

## 🚢 Deployment

### Docker Production Deployment

**FastMCP Servers (Recommended)**:
```bash
# Start all services with FastMCP
docker-compose --profile fastmcp up -d --build

# Or selective deployment
docker-compose up -d dataflow-chat dataflow-agent
docker-compose --profile fastmcp up -d dataflow-mcp-demo-fastmcp
```

**Traditional Deployment**:
```bash
# Build and start all services
docker-compose up -d --build

# Scale specific services  
docker-compose up -d --scale dataflow-chat=3

# Include Denodo server
docker-compose --profile denodo up -d
```

### Kubernetes Deployment

```bash
cd deploy/helm
helm install dataflow ./dataflow

# With custom values
helm install dataflow ./dataflow -f values.prod.yaml
```

### Environment-Specific Configurations

**Development**:
```bash
# Use development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production**:
```bash
# Use production optimizations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Health Monitoring

All services include health check endpoints:

- **Chat Interface**: `GET http://localhost:3000/api/health`
- **Agent Core**: `GET http://localhost:8000/health`
- **Demo MCP**: `GET http://localhost:8081/health`
- **Denodo MCP**: `GET http://localhost:8082/health`

### Performance Optimization

**FastMCP Benefits**:
- Reduced memory footprint (69% less code)
- Better error handling and recovery
- Built-in request validation
- Optimized JSON-RPC processing

**Scaling Recommendations**:
- Use multiple chat interface replicas for high traffic
- Separate MCP servers can be scaled independently  
- Agent core benefits from GPU acceleration for large models
- Consider Redis for session storage in multi-replica deployments

## 📚 API Documentation

### Chat API Endpoints

**POST** `/api/chat` - Streaming chat completions
```typescript
interface ChatRequest {
  messages: Array<{role: string, content: string}>;
  stream?: boolean;
}

interface ChatResponse {
  id: string;
  choices: Array<{delta: {content: string}}>;
}
```

**GET** `/api/health` - Health check
```json
{"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
```

### Agent API Endpoints

**POST** `/api/chat` - AI agent streaming responses
- Compatible with Vercel AI SDK
- Supports multiple output formats (text, code, charts, tables)
- Real-time streaming with server-sent events

**GET** `/health` - Agent health status
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "uptime": "1h 23m 45s"
}
```

### MCP API Endpoints

Both demo and Denodo servers expose standard MCP endpoints:

**POST** `/mcp` - Main MCP endpoint (JSON-RPC 2.0)
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "ask_ai",
    "arguments": {"question": "What is AI?", "mode": "generate"}
  },
  "id": 1
}
```

**GET** `/health` - Server health check
**GET** `/mcp/tools` - List available tools
**GET** `/mcp/resources` - List available resources

### Authentication

The platform uses NextAuth.js with Azure AD integration:

```typescript
// pages/api/auth/[...nextauth].ts
export default NextAuth({
  providers: [
    AzureADProvider({
      clientId: process.env.AZURE_CLIENT_ID!,
      clientSecret: process.env.AZURE_CLIENT_SECRET!,
      tenantId: process.env.AZURE_TENANT_ID!,
    })
  ]
})
```

## 🤝 Contributing

We welcome contributions to DataFlow! Here's how to get started:

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/dataflow.git
   cd dataflow
   ```

2. **Set up development environment**
   ```bash
   # Install dependencies for all components
   cd chat && npm install && cd ..
   cd agent && pip install -r requirements.txt && cd ..
   cd mcp/demo && pip install -r requirements.txt && cd ../..
   ```

3. **Configure environment variables**
   ```bash
   cp chat/.env.local.example chat/.env.local
   cp agent/model_config.yaml.template agent/model_config.yaml
   cp mcp/demo/.env.template mcp/demo/.env
   ```

4. **Start development servers**
   ```bash
   # Terminal 1: Chat interface
   cd chat && npm run dev
   
   # Terminal 2: Agent core  
   cd agent && python app.py
   
   # Terminal 3: MCP demo server
   cd mcp/demo && python fastmcp_main.py
   ```

### Contribution Guidelines

1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Follow coding standards**
   - **TypeScript/React**: ESLint + Prettier configuration
   - **Python**: Black formatting + type hints
   - **FastMCP**: Follow FastMCP best practices for new tools

3. **Test your changes**
   ```bash
   # Frontend tests
   cd chat && npm run test && npm run type-check
   
   # MCP server tests  
   cd mcp/demo && python test_migration.py
   ```

4. **Write meaningful commit messages**
   ```bash
   git commit -m "feat: add new chart visualization type"
   git commit -m "fix: resolve streaming connection issues"
   git commit -m "docs: update FastMCP migration guide"
   ```

5. **Push and create Pull Request**
   ```bash
   git push origin feature/amazing-feature
   ```

### Areas for Contribution

- 🎨 **UI/UX Improvements** - Enhanced chat interface and visualizations
- 🔌 **New MCP Tools** - Additional data source integrations
- 📊 **Visualization Types** - Custom chart types and data renderers  
- 🔐 **Authentication** - Additional SSO providers and security features
- 🚀 **Performance** - Optimization and caching improvements
- 📚 **Documentation** - Guides, tutorials, and API documentation

### Code Review Process

1. All PRs require review from at least one maintainer
2. Automated tests must pass (CI/CD pipeline)
3. Documentation updates for new features
4. Performance impact assessment for significant changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Chat Interface Issues**:
```bash
# Clear Next.js cache
cd chat && rm -rf .next && npm run dev

# Check environment variables
cat .env.local | grep -v SECRET
```

**Agent Connection Issues**:
```bash
# Verify agent is running
curl http://localhost:8000/health

# Check model configuration
cd agent && python -c "import yaml; print(yaml.safe_load(open('model_config.yaml')))"
```

**MCP Server Issues**:
```bash
# Test FastMCP server directly
cd mcp/demo && python fastmcp_main.py --transport http --port 8081

# Validate migration
python test_migration.py

# Check tool availability
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Performance Monitoring

The platform includes built-in monitoring:

- **Response Times** - Tracked in chat interface performance panel
- **Memory Usage** - Docker stats and application metrics
- **Error Rates** - Comprehensive logging with structured output
- **Tool Usage** - MCP server request/response analytics

### Getting Help

1. **Check the logs** - All services log to stdout with structured JSON
2. **Health endpoints** - Use `/health` endpoints to verify service status
3. **Migration documentation** - See FastMCP migration details for MCP issues
4. **GitHub Issues** - Report bugs and feature requests
5. **GitHub Discussions** - Community support and questions

## 🔗 Related Links

- **[FastMCP Documentation](https://gofastmcp.com/)** - FastMCP framework guide
- **[Model Context Protocol](https://spec.modelcontextprotocol.io/)** - MCP specification  
- **[Next.js Documentation](https://nextjs.org/docs)** - Next.js framework
- **[AutoGen Core](https://github.com/microsoft/autogen)** - Multi-agent AI framework
- **[Vercel AI SDK](https://sdk.vercel.ai/)** - AI application building blocks
- **[shadcn/ui](https://ui.shadcn.com/)** - Re-usable UI components

## 🎯 Roadmap

### Completed ✅
- FastMCP migration (69% code reduction)
- Real-time streaming chat interface
- Azure SSO authentication
- Multi-transport MCP support
- Docker containerization

### In Progress 🚧
- Kubernetes Helm charts
- Performance optimization
- Advanced data visualization types
- Enhanced error handling

### Planned 📋
- Additional MCP server templates
- Real-time collaboration features
- Advanced analytics dashboard
- Mobile app development
- Plugin architecture for custom tools

---

<div align="center">

**Made with ❤️ by the DataFlow Team**

*Powered by FastMCP 2.9+ | Next.js 15 | AutoGen Core*

</div>
