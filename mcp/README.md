# Digit MCP Servers

A collection of Model Context Protocol (MCP) servers that provide tools for natural language database interactions and AI-powered data queries.

## Overview

This repository contains multiple MCP server implementations that enable natural language querying of different data sources through the Model Context Protocol. Each server provides HTTP transport capabilities for containerized deployments and web services integration.

## 🏗️ Project Structure

```
digit-mcp/
├── demo/              # Demo MCP server with simulated banking database
├── denodo/            # Denodo AI SDK MCP server
├── LICENSE            # MIT License
└── README.md          
```

## 📋 Available Servers

### 🏦 Demo MCP Server (`/demo`)

A demonstration MCP server that provides tools to interact with a simulated banking database using OpenAI.

**Key Features:**
- Natural language database queries using OpenAI
- Simulated banking data for testing and demonstrations
- HTTP transport with JSON-RPC 2.0 protocol
- Docker containerization support
- Comprehensive logging and health monitoring

**Use Cases:**
- Testing MCP implementations
- Demonstrating natural language database queries
- Learning MCP protocol integration

### 🔌 Denodo AI SDK MCP Server (`/denodo`)

An MCP server that interfaces with Denodo AI SDK for enterprise data virtualization and AI-powered analytics.

**Key Features:**
- Integration with Denodo AI SDK
- Enterprise-grade authentication (username/password)
- Data and metadata exploration modes
- Async implementation for performance
- Production-ready Docker containers

**Use Cases:**
- Enterprise data virtualization
- AI-powered business intelligence
- Data governance and metadata management

## 📚 Documentation

Each server includes detailed documentation:

- [`demo/README.md`](./demo/README.md) - Complete demo server documentation
- [`denodo/README.md`](./denodo/README.md) - Complete denodo server documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions and support:

1. Check the individual server README files for specific documentation
2. Review the logs for troubleshooting information
3. Open an issue in this repository for bugs or feature requests

## 🔗 Related Links

- [Model Context Protocol (MCP) Documentation](https://github.com/modelcontextprotocol)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Denodo AI SDK Documentation](https://www.denodo.com/en/solutions/by-capability/ai-software-development-kit)
