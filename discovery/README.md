## Discovery Agent UI

A Next.js UI for driving a discovery agent. It supports a LangGraph backend (streaming capable) and a REST backend (optional).

### Prerequisites
- Node 18+
- A running backend:
	- LangGraph server at `http://localhost:2024` (default), with a graph/assistant name (e.g., `research`)
	- OR a REST API exposing `/chats`, `/chats/:id/messages`, etc. (see `src/providers/DiscoveryAgentHTTPProvider.ts`)

### Config
Create `.env.local`:

```
NEXT_PUBLIC_AGENT_BACKEND=langgraph
NEXT_PUBLIC_LANGGRAPH_BASE_URL=http://localhost:2024
NEXT_PUBLIC_LANGGRAPH_GRAPH=research
# Public vars are exposed to the browser. Do NOT store secrets in NEXT_PUBLIC_*
```

Notes:
- For REST, set `NEXT_PUBLIC_AGENT_BACKEND=rest` and implement/configure the REST provider.

### Run

```bash
npm install
npm run dev
```

Open http://localhost:3000.

### Features
- Chat list, search, dark mode
- Send messages; stream-ready provider path (LangGraph)
- Artifacts grid + viewer (charts, tables, files)
- Pin/unpin UI (requires backend support)

### Roadmap
- Wire streaming UI end-to-end with `DiscoveryAgentBridgeProvider`
- File attachments and SAS download URLs via provider API
- Unify types into a shared module
