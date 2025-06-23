# DataFlow

<div align="center">

![DataFlow Logo](./chat/public/data-flow-logo.svg)

**A comprehensive AI-powered data platform for natural language database interactions and intelligent chat experiences**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](chat/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](agent/)

</div>

## 🌟 Overview

DataFlow is a modern, full-stack platform that bridges the gap between natural language and data systems. It combines AI-powered chat interfaces, streaming data processing, and Model Context Protocol (MCP) servers to enable intuitive data interactions through conversational AI.

### Key Capabilities

- **🤖 Intelligent Chat Interface** - Next.js-based modern UI with real-time streaming
- **📊 Data Visualization** - Interactive charts, tables, and Mermaid diagrams
- **🔌 MCP Integration** - Model Context Protocol servers for database connections
- **🚀 Streaming Architecture** - Real-time data processing with AutoGen Core
- **🔐 Enterprise Authentication** - Azure SSO integration
- **🐳 Container-Ready** - Full Docker deployment support

## 🏗️ Architecture

DataFlow consists of four main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat UI       │    │   Agent Core    │    │   MCP Servers   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│                 │    │                 │    │                 │
│ • Real-time UI  │    │ • AutoGen Core  │    │ • Demo Server   │
│ • Artifacts     │    │ • Streaming     │    │ • Denodo        │
│ • Auth (Azure)  │    │ • AI Models     │    │ • HTTP/JSON-RPC │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

#### 🎨 **Chat Interface** (`/chat`)
- **Framework**: Next.js 15 with TypeScript
- **UI**: shadcn/ui components with Tailwind CSS
- **Features**: 
  - Real-time streaming chat
  - Artifact management (code, charts, diagrams)
  - Session persistence
  - Azure SSO authentication
  - Responsive design

#### 🤖 **Agent Core** (`/agent`)
- **Framework**: FastAPI with AutoGen Core
- **Features**:
  - Streaming AI responses
  - Advanced data visualization
  - Code generation with syntax highlighting
  - CORS-enabled API endpoints

#### 🔌 **MCP Servers** (`/mcp`)
- **Demo Server**: Simulated banking database with OpenAI integration
- **Denodo Server**: Enterprise data virtualization platform integration
- **Protocol**: Model Context Protocol with HTTP transport
- **Features**: Natural language database queries, JSON-RPC 2.0

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dataflow
   ```

2. **Configure environment variables**
   ```bash
   # Copy environment templates
   cp chat/.env.production.template chat/.env.production
   cp mcp/demo/.env.template mcp/demo/.env
   cp mcp/denodo/.env.template mcp/denodo/.env
   
   # Edit with your API keys and configurations
   ```

3. **Start the platform**
   ```bash
   # Start core services (chat + demo MCP)
   docker-compose up -d
   
   # Or include Denodo MCP server
   docker-compose --profile denodo up -d
   ```

4. **Access the application**
   - **Chat Interface**: http://localhost:3000
   - **Demo MCP Server**: http://localhost:8081
   - **Denodo MCP Server**: http://localhost:8082 (if enabled)

### Local Development

#### Chat Interface
```bash
cd chat
npm install
npm run dev
```

#### Agent Core
```bash
cd agent
pip install -r requirements.txt
cp model_config.yaml.template model_config.yaml
# Configure your API keys in model_config.yaml
python app.py
```

#### MCP Servers
```bash
cd mcp/demo  # or mcp/denodo
pip install -r requirements.txt
python main.py
```

## 📁 Project Structure

```
dataflow/
├── 📁 chat/                    # Next.js Chat Interface
│   ├── 🎨 components/         # React components
│   ├── 📱 app/                # Next.js app router
│   ├── 🔧 lib/                # Utilities and configurations
│   └── 🎯 types/              # TypeScript definitions
│
├── 🤖 agent/                   # FastAPI Agent Core
│   ├── app.py                 # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── model_config.yaml      # AI model configuration
│
├── 🔌 mcp/                     # Model Context Protocol Servers
│   ├── demo/                  # Demo banking database server
│   └── denodo/                # Denodo integration server
│
├── 🚀 deploy/                  # Deployment configurations
│   └── helm/                  # Kubernetes Helm charts
│
├── 📊 logs/                    # Application logs
└── 🐳 docker-compose.yml      # Container orchestration
```

## 🔧 Configuration

### Environment Variables

#### Chat Interface
```env
# Azure Authentication
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

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
```

#### MCP Servers
```env
# Demo MCP Server
OPENAI_API_KEY=your-openai-api-key
LOG_LEVEL=INFO

# Denodo MCP Server
DENODO_URL=your-denodo-endpoint
DENODO_USERNAME=your-username
DENODO_PASSWORD=your-password
```

## 🌟 Features

### Chat Interface
- ✨ **Real-time Streaming** - Live AI responses with smooth animations
- 📊 **Rich Artifacts** - Code blocks, interactive charts, and Mermaid diagrams
- 🔐 **Azure SSO** - Enterprise-grade authentication
- 💾 **Session Persistence** - Chat history preservation
- 📱 **Responsive Design** - Works across all devices

### Agent Core
- 🔄 **Streaming API** - Real-time response generation
- 📈 **Data Visualization** - Advanced charting capabilities
- 💻 **Code Generation** - Syntax-highlighted code blocks
- 🎨 **Diagram Support** - Mermaid flowcharts and diagrams

### MCP Integration
- 🗄️ **Natural Language DB Queries** - Ask questions in plain English
- 🔌 **Multiple Data Sources** - Demo and enterprise database support
- 🌐 **HTTP Transport** - Web-friendly JSON-RPC protocol
- 📋 **Comprehensive Logging** - Detailed operation tracking

## 🛠️ Development

### Adding New MCP Servers

1. Create a new directory under `/mcp/your-server`
2. Implement the MCP protocol interface
3. Add Docker configuration
4. Update `docker-compose.yml` with your service

### Customizing the Chat Interface

The chat interface is built with modern React patterns:
- **Components**: Reusable UI components in `/chat/components`
- **Hooks**: Custom React hooks in `/chat/hooks`
- **Utilities**: Helper functions in `/chat/lib`

### Extending Agent Capabilities

Add new agent capabilities by:
- Extending the FastAPI endpoints in `/agent/app.py`
- Adding new AI model configurations
- Implementing custom data processing pipelines

## 🚢 Deployment

### Docker Production Deployment
```bash
# Build and start all services
docker-compose -f docker-compose.yml up -d --build

# Scale specific services
docker-compose up -d --scale dataflow-chat=3
```

### Kubernetes Deployment
```bash
cd deploy/helm
helm install dataflow ./dataflow
```

## 📚 Documentation

- [Chat Interface Guide](./chat/README.md)
- [Agent Core Documentation](./agent/README.md)
- [MCP Servers Overview](./mcp/README.md)
- [Deployment Guide](./deploy/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [Internal Wiki](docs/)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

---

<div align="center">
Made with ❤️ by the DataFlow Team
</div>
