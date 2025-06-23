"""
AutoGen Core Backend - Single File
Streaming FastAPI backend for general purpose AI assistant
Compatible with Vercel AI SDK useChat hook

Run with: python app.py
Then use with Vercel AI SDK frontend
"""

import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, List, Optional, Any

import aiofiles
import yaml
from autogen_core import (
    AgentId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
    type_subscription,
    DefaultTopicId,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class TextMessage:
    """Base message"""
    source: str
    content: str

@dataclass
class UserTextMessage(TextMessage):
    """User message"""
    pass

@dataclass
class AssistantTextMessage(TextMessage):
    """Assistant message"""
    pass

@dataclass
class AgentResponse:
    """Final response from streaming"""
    content: str

@dataclass
class UserRequest:
    """User request from streaming example"""
    messages: List[Dict[str, str]]
    session_id: Optional[str] = None

# ============================================================================
# STREAMING INFRASTRUCTURE
# ============================================================================

# Session-based queues for streaming responses
session_queues: Dict[str, asyncio.Queue] = {}
STREAM_DONE = object()  # Sentinel

def get_or_create_queue(session_id: str) -> asyncio.Queue:
    """Get or create a queue for a specific session"""
    if session_id not in session_queues:
        session_queues[session_id] = asyncio.Queue()
    return session_queues[session_id]

# ============================================================================
# STREAMING ASSISTANT AGENT
# ============================================================================

@type_subscription("general_assistant_conversation")
class StreamingGeneralAssistantAgent(RoutedAgent):
    """General purpose assistant agent with streaming + code generation"""
    
    def __init__(
        self,
        name: str,
        description: str,
        model_client: ChatCompletionClient,
        session_id: str,
    ) -> None:
        super().__init__(description)
        self._name = name
        self._model_client = model_client
        self._session_id = session_id
        self._response_queue = get_or_create_queue(session_id)
        self._system_messages = [
            SystemMessage(
                content=f"""You are a helpful AI assistant skilled in various tasks including coding, creating diagrams, data visualization, and general assistance.

When generating code:
- Always use proper markdown code blocks with the language specified
- For example: ```python, ```javascript, ```typescript, etc.
- Ensure proper indentation and formatting
- Add comments to explain complex parts

When creating Mermaid diagrams:
- mermaid should be visually appealing with colored blocks and lines and easy to understand with clear descriptions
- Use ```mermaid code blocks
- Ensure proper Mermaid syntax
- Include clear labels and descriptions

When creating data visualizations or charts (should look professional):
- Chart should be visually appealing with professional colors and easy to understand with clear labels 
- Use ```chart code blocks
- Output a JSON object with this exact schema:

```json
{{
  "chartType": "bar",
  "data": [
    {{"month": "Jan", "sales": 4000, "profit": 2400}},
    {{"month": "Feb", "sales": 3000, "profit": 1398}},
    {{"month": "Mar", "sales": 2000, "profit": 9800}}
  ],
  "config": {{
    "title": "Q1 Sales Performance",
    "subtitle": "Revenue and profit analysis for first quarter",
    "footer": "Data updated as of March 31, 2024",
    "legend": true,
    "grid": true,
    "xAxis": {{"dataKey": "month"}},
    "yAxis": {{}},
    "series": [
      {{
        "dataKey": "sales", 
        "fill": "#3b82f6", 
        "name": "Sales ($)"
      }},
      {{
        "dataKey": "profit", 
        "fill": "#10b981", 
        "name": "Profit ($)"
      }}
    ]
  }}
}}
```

Chart schema explanation:
- chartType: Type of chart - "bar", "line", "area", or "pie"
- data: Array of data points (objects with consistent keys)
- config:
  - title: Main chart title (Mandatory)
  - subtitle: Chart subtitle (optional)
  - footer: Chart footer text (optional)
  - legend: Whether to show legend (boolean, Mandatory)
  - grid: Whether to show grid lines (boolean, Mandatory)
  - xAxis.dataKey: The key from data objects for X-axis labels
  - yAxis: Y-axis configuration (can be empty object)
  - series: Array defining what to plot
    - dataKey: Key from data objects for this series' values
    - fill: Color for bar/area charts (e.g., "#3b82f6")
    - stroke: Color for line charts (e.g., "#3b82f6")
    - name: Display name for the series (optional)

Example chart response:
```chart
{{
  "chartType": "line",
  "data": [
    {{"month": "Jan", "revenue": 12000, "profit": 3000}},
    {{"month": "Feb", "revenue": 15000, "profit": 4500}},
    {{"month": "Mar", "revenue": 18000, "profit": 5200}}
  ],
  "config": {{
    "title": "Q1 Revenue Analysis",
    "subtitle": "Monthly revenue and profit trends",
    "legend": true,
    "grid": true,
    "xAxis": {{"dataKey": "month"}},
    "yAxis": {{}},
    "series": [
      {{"dataKey": "revenue", "fill": "#3b82f6", "name": "Revenue ($)"}},
      {{"dataKey": "profit", "fill": "#10b981", "name": "Profit ($)"}}
    ]
  }}
}}
```

When presenting data points or datasets:
- Always present data in advanced tabular format using ```table code blocks
- Use the structured JSON format with column definitions and data types
- Include proper column types, sorting options, and formatting
- Add summary information and metadata

Advanced table format with full schema:
```table
{{
  "title": "Sample Data Dashboard",
  "subtitle": "Data analysis and insights",
  "columns": [
    {{"key": "id", "label": "ID", "type": "string", "width": "80px"}},
    {{"key": "name", "label": "Name", "type": "string", "sortable": true}},
    {{"key": "department", "label": "Department", "type": "string", "sortable": true}},
    {{"key": "amount", "label": "Amount", "type": "currency", "sortable": true}},
    {{"key": "score", "label": "Score", "type": "number", "sortable": true}},
    {{"key": "active", "label": "Active", "type": "boolean", "sortable": true}},
    {{"key": "date", "label": "Date", "type": "date", "sortable": true}}
  ],
  "data": [
    {{
      "id": "001",
      "name": "John Smith",
      "department": "Sales",
      "amount": 95000,
      "score": 4.2,
      "active": true,
      "date": "2023-03-15"
    }},
    {{
      "id": "002",
      "name": "Sarah Johnson", 
      "department": "Marketing",
      "amount": 78000,
      "score": 4.8,
      "active": true,
      "date": "2021-07-22"
    }}
  ],
  "summary": {{
    "totalRows": 2,
    "totalColumns": 7,
    "lastUpdated": "{time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
  }}
}}
```

## Column Types Supported:
- **"string"** - Regular text
- **"number"** - Formatted numbers (1,234.56)
- **"currency"** - Currency format ($1,234.56)
- **"date"** - Date formatting
- **"boolean"** - ✅/❌ checkmarks

Column properties:
- **key**: Data field identifier
- **label**: Display name for column header
- **type**: Data type for formatting
- **width**: Optional column width (e.g., "80px", "120px")
- **sortable**: Whether column can be sorted (true/false)

When users ask for data points, statistics, or datasets:
1. First present the data in advanced table format using ```table
2. Include appropriate column types and formatting
3. Add sortable properties where relevant
4. Include summary metadata (totalRows, totalColumns, lastUpdated)
5. If visualization is also requested, follow with a ```chart

For code examples, always use this format:
```language
// Your code here
```

For Mermaid diagrams:
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

Today's date is {time.strftime("%Y-%m-%d")}
"""
            )
        ]

    @message_handler
    async def handle_message(self, message: UserRequest, ctx: MessageContext) -> None:
        """Handle user messages with streaming"""
        # Build full conversation history
        messages = self._system_messages.copy()
        
        # Add all messages from the conversation history
        for msg in message.messages:
            if msg["source"] == "User":
                messages.append(UserMessage(content=msg["content"], source=msg["source"]))
            else:
                messages.append(AssistantMessage(content=msg["content"], source=msg["source"]))
        
        accumulated_content = ""
        
        try:
            # Use streaming API with full conversation history
            async for chunk in self._model_client.create_stream(
                messages,
                cancellation_token=ctx.cancellation_token
            ):
                if isinstance(chunk, str):
                    accumulated_content += chunk
                    await self._response_queue.put({
                        "type": "text", 
                        "content": chunk
                    })
                    # Add delay between chunks for slower streaming
                    await asyncio.sleep(0.030)  # 30ms delay between chunks
                else:
                    break
            
            await self._response_queue.put(STREAM_DONE)
            
        except Exception as e:
            # Send error message
            await self._response_queue.put({
                "type": "error",
                "error": str(e)
            })
            await self._response_queue.put(STREAM_DONE)

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

runtime = SingleThreadedAgentRuntime()

# API Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant" (AI SDK format)
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan"""
    # Load model configuration
    async with aiofiles.open("model_config.yaml", "r") as file:
        model_config = yaml.safe_load(await file.read())
    model_client = ChatCompletionClient.load_component(model_config)
    
    # Store globally for agent registration
    app.state.model_client = model_client
    
    # Start the runtime
    runtime.start()
    yield
    await runtime.stop()
    await model_client.close()

app = FastAPI(
    title="AutoGen Streaming API",
    description="Streaming chat API with code generation and visualization support",
    lifespan=lifespan
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat_completions(request: ChatRequest):
    """Vercel AI SDK compatible chat endpoint"""
    
    # Validate messages
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Convert AI SDK messages to AutoGen format
    autogen_messages = []
    for msg in request.messages:
        if msg.role not in ["user", "assistant", "system"]:
            raise HTTPException(status_code=400, detail=f"Invalid role: {msg.role}")
        
        # Map role to source for AutoGen
        source = "User" if msg.role == "user" else "Assistant"
        autogen_messages.append({"source": source, "content": msg.content})
    
    user_request = UserRequest(messages=autogen_messages, session_id=session_id)

    # Register agent for this session
    agent_id = f"agent_{session_id}"
    
    try:
        # Register assistant agent
        await StreamingGeneralAssistantAgent.register(
            runtime,
            agent_id,
            lambda: StreamingGeneralAssistantAgent(
                "GeneralAssistant",
                description="AI assistant for coding, diagrams, and general help",
                model_client=app.state.model_client,
                session_id=session_id,
            ),
        )
    except Exception:
        # Agent already registered for this session
        pass

    # Streaming response generator
    async def response_stream() -> AsyncGenerator[str, None]:
        response_queue = get_or_create_queue(session_id)
        
        # Send the full conversation history to runtime
        runtime_message = UserRequest(
            messages=autogen_messages,
            session_id=session_id
        )
        
        # Start the conversation
        task = asyncio.create_task(
            runtime.publish_message(
                runtime_message,
                DefaultTopicId("general_assistant_conversation"),
            )
        )
        
        try:
            while True:
                item = await response_queue.get()
                
                if item is STREAM_DONE:
                    # Send OpenAI-style completion
                    yield "data: [DONE]\n\n"
                    break
                    
                elif isinstance(item, dict):
                    if item["type"] == "text":
                        # Stream text content (OpenAI format for Vercel AI SDK)
                        chunk_data = {
                            "id": f"chatcmpl-{session_id}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": "gpt-4",
                            "choices": [{
                                "index": 0,
                                "delta": {"content": item["content"]},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        
                    elif item["type"] == "error":
                        # Send error in OpenAI format
                        error_data = {
                            "error": {
                                "message": item["error"],
                                "type": "server_error",
                                "code": None
                            }
                        }
                        yield f"data: {json.dumps(error_data)}\n\n"
                        yield "data: [DONE]\n\n"
                        break
                        
        except Exception as e:
            error_data = {
                "error": {
                    "message": str(e),
                    "type": "server_error",
                    "code": None
                }
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            yield "data: [DONE]\n\n"
        finally:
            await task

    return StreamingResponse(
        response_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "autogen-streaming-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501, reload=True)