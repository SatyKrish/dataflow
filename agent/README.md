# DataFlow Agent Core

FastAPI backend with AutoGen Core integration for streaming AI responses. Compatible with Vercel AI SDK and supports multiple output formats including charts, tables, and code generation.

## Implementation Details

### Architecture
- **Framework**: FastAPI with async/await support
- **AI Integration**: AutoGen Core for multi-agent workflows
- **Streaming**: Server-sent events (SSE) compatible with Vercel AI SDK
- **CORS**: Enabled for cross-origin frontend integration

### Key Features
- 🔄 **Real-time streaming** responses with chunk-based delivery
- 📊 **Advanced data visualization** with Recharts-compatible JSON
- 🗂️ **Structured table output** with column types and sorting metadata
- 🎨 **Mermaid diagram generation** with syntax validation
- 💻 **Code generation** with language detection and syntax highlighting
- 🌐 **Multi-model support** with configurable LLM providers

## Setup & Configuration

### Installation
```bash
cd agent
pip install -r requirements.txt
cp model_config.yaml.template model_config.yaml
```

### Model Configuration
Edit `model_config.yaml` with your API credentials:

```yaml
models:
  - model: "gpt-4o"
    api_key: "your-azure-openai-key"
    base_url: "https://your-endpoint.openai.azure.com"
    api_version: "2024-02-15-preview"
    deployment: "gpt-4o"
  - model: "gpt-4"
    api_key: "your-openai-key"
    base_url: "https://api.openai.com/v1"
```

### Running the Server
```bash
# Development with auto-reload
python app.py

# Production with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker build -t dataflow-agent .
docker run -p 8000:8000 dataflow-agent
```

## API Reference

### Endpoints

**POST** `/api/chat` - Streaming chat completions
- Compatible with Vercel AI SDK `useChat()` hook
- Supports streaming and non-streaming modes
- Returns structured data for charts, tables, and code

**GET** `/health` - Health check with model status
```json
{
  "status": "healthy",
  "model_status": "loaded", 
  "uptime": "1h 23m 45s",
  "version": "1.0.0"
}
```

### Request Format
```typescript
interface ChatRequest {
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
  }>;
  stream?: boolean;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}
```

### Response Formats

The agent can return various structured data types:

#### 1. Chart Data
```json
{
  "type": "chart",
  "chartType": "bar|line|pie|scatter",
  "data": [...],
  "xAxis": "field_name",
  "yAxis": "field_name",
  "title": "Chart Title"
}
```

#### 2. Table Data
```json
{
  "type": "table", 
  "columns": [
    {"key": "name", "type": "string", "sortable": true},
    {"key": "value", "type": "number", "sortable": true}
  ],
  "data": [...],
  "title": "Table Title"
}
```

#### 3. Code Blocks
```json
{
  "type": "code",
  "language": "python|javascript|sql|...",
  "code": "...",
  "filename": "optional_filename.py"
}
```

#### 4. Mermaid Diagrams
```json
{
  "type": "mermaid",
  "diagram": "graph TD\n  A --> B",
  "title": "Diagram Title"
}
```

## Development

### Project Structure
```
agent/
├── app.py                     # Main FastAPI application
├── model_config.yaml.template # LLM configuration template
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

### Adding New Output Types

1. **Define the output format** in the agent's response schema
2. **Update the frontend** chart/table renderers to handle new types
3. **Test streaming** behavior with the new format

### Performance Optimization

- **Model caching**: Models are loaded once and reused
- **Async processing**: All I/O operations are asynchronous
- **Streaming chunks**: Responses are sent in real-time chunks
- **Memory management**: Automatic cleanup of completed conversations

### Troubleshooting

**Model loading issues**:
```bash
# Check model configuration
python -c "import yaml; print(yaml.safe_load(open('model_config.yaml')))"

# Test model connectivity
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

**Streaming issues**:
- Verify CORS headers are properly set
- Check that the frontend is using the correct Content-Type
- Monitor network tab for proper SSE connection

### Dependencies

Key packages and their purposes:
- `fastapi`: Web framework with async support
- `uvicorn`: ASGI server for production
- `autogen-core`: Multi-agent AI framework
- `openai`: OpenAI API client
- `pydantic`: Data validation and serialization
- `python-multipart`: File upload support
