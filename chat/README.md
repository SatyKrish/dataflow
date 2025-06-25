# DataFlow Chat Interface

Modern React chat interface built with Next.js 15, featuring real-time streaming, artifact management, and Azure SSO authentication. Integrates seamlessly with the DataFlow Agent Core and MCP servers.

## Implementation Details

### Technology Stack
- **Framework**: Next.js 15 with App Router
- **UI Components**: shadcn/ui with Radix primitives
- **Styling**: Tailwind CSS with CSS variables for theming
- **Authentication**: NextAuth.js with Azure AD provider
- **State Management**: React hooks with local storage persistence
- **Charts**: Recharts for interactive data visualization
- **Diagrams**: Mermaid for flowcharts and sequence diagrams

### Key Features
- ✨ **Real-time streaming** with typewriter animations
- 📊 **Artifact panel** for code, charts, and diagrams
- 🔐 **Azure SSO** with role-based access
- 💾 **Session persistence** with automatic chat history
- 📱 **Responsive design** optimized for all screen sizes
- ⚡ **Performance optimized** with React 18 concurrent features

## Setup & Configuration

### Installation
```bash
cd chat
npm install
cp .env.local.example .env.local
```

### Environment Configuration
```env
# Authentication
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000

# API Endpoints
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MCP_URL=http://localhost:8081

# Optional: Additional MCP servers
NEXT_PUBLIC_DENODO_MCP_URL=http://localhost:8082
```

### Running the Application
```bash
# Development
npm run dev

# Type checking
npm run type-check

# Linting and formatting
npm run lint && npm run format

# Production build
npm run build && npm start

# Docker
docker build -t dataflow-chat .
docker run -p 3000:3000 dataflow-chat
```

## Architecture

### Component Structure
```
components/
├── ui/                        # Base shadcn/ui components
├── auth/                      # Authentication components
├── mcp/                       # MCP-specific components
├── chat-interface.tsx         # Main chat UI
├── artifacts-panel.tsx        # Code/chart/diagram viewer
├── message-bubble.tsx         # Individual message display
├── chart-renderer.tsx         # Recharts integration
├── markdown-renderer.tsx      # Rich text rendering
└── settings-dialog.tsx        # User preferences
```

### Key Hooks
```typescript
// Chat management
const { messages, input, handleSubmit, isLoading } = useChat({
  api: '/api/chat',
  onResponse: (response) => {
    // Handle streaming chunks
  }
});

// Session persistence
const { saveSession, loadSession } = useChatStorage();

// Mobile optimization
const isMobile = useMobile();

// Performance monitoring
const { performance } = useResizeOptimization();
```

### State Management

The application uses a combination of React hooks and local storage:

#### Chat State
- **Messages**: Stored in `useChat` hook from Vercel AI SDK
- **Session persistence**: Auto-saved to localStorage
- **Artifacts**: Extracted and managed separately from messages

#### Authentication State
- **User session**: Managed by NextAuth.js
- **Azure tokens**: Automatically refreshed
- **Role-based access**: Configured in auth callbacks

## API Integration

### Agent Core Integration
```typescript
// Streaming chat with the agent
const { messages, handleSubmit } = useChat({
  api: '/api/chat',
  headers: {
    'Authorization': `Bearer ${session?.accessToken}`
  },
  onResponse: (response) => {
    // Extract artifacts from response
    extractArtifacts(response);
  }
});
```

### MCP Server Integration
```typescript
// Direct MCP tool calls
const callMCPTool = async (toolName: string, params: any) => {
  const response = await fetch('/api/mcp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: { name: toolName, arguments: params },
      id: Date.now()
    })
  });
  return response.json();
};
```

## Artifact System

### Supported Artifact Types

#### 1. Code Blocks
```typescript
interface CodeArtifact {
  type: 'code';
  language: string;
  code: string;
  filename?: string;
  editable?: boolean;
}
```

#### 2. Charts
```typescript
interface ChartArtifact {
  type: 'chart';
  chartType: 'bar' | 'line' | 'pie' | 'scatter' | 'area';
  data: any[];
  xAxis?: string;
  yAxis?: string;
  title?: string;
  config?: RechartsConfig;
}
```

#### 3. Tables
```typescript
interface TableArtifact {
  type: 'table';
  columns: Array<{
    key: string;
    type: 'string' | 'number' | 'date' | 'boolean';
    sortable?: boolean;
    filterable?: boolean;
  }>;
  data: any[];
  title?: string;
}
```

#### 4. Mermaid Diagrams
```typescript
interface MermaidArtifact {
  type: 'mermaid';
  diagram: string;
  title?: string;
  config?: MermaidConfig;
}
```

### Artifact Detection
```typescript
// Automatic artifact extraction from AI responses
const extractArtifacts = (content: string): Artifact[] => {
  const artifacts: Artifact[] = [];
  
  // Code blocks
  const codeBlocks = content.match(/```(\w+)?\n([\s\S]*?)```/g);
  if (codeBlocks) {
    codeBlocks.forEach(block => {
      const [, language, code] = block.match(/```(\w+)?\n([\s\S]*?)```/) || [];
      artifacts.push({ type: 'code', language, code });
    });
  }
  
  // JSON data for charts/tables
  const jsonBlocks = content.match(/```json\n([\s\S]*?)```/g);
  if (jsonBlocks) {
    jsonBlocks.forEach(block => {
      try {
        const data = JSON.parse(block.replace(/```json\n|```/g, ''));
        if (data.type === 'chart' || data.type === 'table') {
          artifacts.push(data);
        }
      } catch (e) {
        // Invalid JSON, skip
      }
    });
  }
  
  return artifacts;
};
```

## Performance Optimization

### React 18 Features
- **Concurrent rendering**: Non-blocking UI updates during streaming
- **Suspense boundaries**: Graceful loading states for components
- **useTransition**: Smooth transitions between chat states

### Memory Management
```typescript
// Efficient message cleanup
const MAX_MESSAGES = 100;
const cleanupMessages = (messages: Message[]) => {
  if (messages.length > MAX_MESSAGES) {
    return messages.slice(-MAX_MESSAGES);
  }
  return messages;
};

// Debounced auto-save
const debouncedSave = useMemo(
  () => debounce(saveSession, 1000),
  [saveSession]
);
```

### Streaming Optimization
```typescript
// High-performance text streaming
const TypewriterText = ({ text, speed = 50 }: TypewriterProps) => {
  const [displayText, setDisplayText] = useState('');
  
  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(timer);
      }
    }, speed);
    
    return () => clearInterval(timer);
  }, [text, speed]);
  
  return <span>{displayText}</span>;
};
```

## Development

### Adding New Components
1. **Create component** in appropriate directory
2. **Export from index** for clean imports
3. **Add Storybook story** for documentation
4. **Include tests** with React Testing Library

### Styling Guidelines
- **Use CSS variables** for theme consistency
- **Follow shadcn/ui patterns** for component structure
- **Responsive first** - mobile-optimized layouts
- **Dark mode support** - automatic theme detection

### Testing Strategy
```bash
# Unit tests
npm run test

# E2E tests  
npm run test:e2e

# Visual regression tests
npm run test:visual

# Performance tests
npm run test:perf
```

### Troubleshooting

**Authentication issues**:
```bash
# Check Azure configuration
curl -X GET http://localhost:3000/api/auth/session

# Verify environment variables
echo $AZURE_CLIENT_ID
```

**Streaming issues**:
- Check network tab for proper SSE connection
- Verify CORS headers from agent
- Monitor browser console for errors

**Build issues**:
```bash
# Clear Next.js cache
rm -rf .next

# Check TypeScript compilation
npm run type-check

# Analyze bundle size
npm run analyze
```
