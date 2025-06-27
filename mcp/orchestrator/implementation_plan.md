# Multi-Agent Research System Implementation Plan (FastMCP Orchestration)

## 1. System Overview
- **Goal:** Enable users to use natural language for data/metadata queries, analysis, and research, with dynamic agent orchestration and entitlement checks.
- **Key Features:**
  - Multi-agent orchestration (lead agent + subagents) using FastMCP
  - Dynamic persona/intent detection
  - On-demand entitlement checks
  - Data/metadata retrieval from multiple sources
  - Conversation storage and personality profiling
  - Scalable, production-ready, and observable

---

## 2. High-Level Architecture (with FastMCP)

- **Orchestrator MCP Server (Lead Agent):**
  - Implemented as a FastMCP server (e.g., `/mcp/orchestrator/fastmcp_server.py`).
  - Exposes a `multi_agent_research` tool (and others as needed) via FastMCP protocol.
  - Receives user query, analyzes intent/persona, plans research steps.
  - Decomposes query into subtasks (metadata, entitlement, data retrieval, aggregation).
  - Spawns subagents as FastMCP tool calls (can call tools on other MCP servers).
  - Aggregates and synthesizes subagent results.
  - Iterates if more research is needed.

- **Subagents:**
  - Implemented as FastMCP tools (can be in the same or other MCP servers).
  - Types: MetadataAgent, EntitlementAgent, DataAgent, AggregationAgent, etc.
  - Each subagent is a tool with a clear contract and output format.

- **Memory/Context:**
  - Store plan, intermediate results, and conversation history (DB, Redis, or file).
  - Summarize/compress context for long conversations.

- **Citation/Attribution Agent:**
  - Post-processes results to add citations and source attributions.

- **Personality/Intent Profiler:**
  - Analyzes user queries and history to infer persona and intent.

---

## 3. Implementation Steps (with FastMCP)

### A. Orchestrator MCP Server (Lead Agent)
- Scaffold a FastMCP server (`fastmcp_server.py`) in `/mcp/orchestrator`.
- Expose a `multi_agent_research` tool:
  - Accepts user query and session info.
  - Analyzes intent/persona (calls persona profiler tool or uses LLM prompt).
  - Decomposes query into subtasks.
  - Calls subagent tools (can be local or remote MCP tools) using FastMCP client.
  - Aggregates results and returns structured response.
- Add a `health_check` tool for monitoring.

### B. Subagent Design (as FastMCP Tools)
- **MetadataAgent:** Calls Denodo MCP server's `denodo_query` tool with `mode=metadata`.
- **EntitlementAgent:** Calls an entitlement-check tool (could be a new MCP server/tool).
- **DataAgent:** Calls Denodo MCP server's `denodo_query` tool with `mode=data`.
- **AggregationAgent:** Aggregates results from other subagents (could be a tool or inline logic).
- Each subagent tool should:
  - Receive a clear objective and output format.
  - Use FastMCP client to call other tools as needed.
  - Return structured results and reasoning.

### C. Tooling & Integration
- Use FastMCP client to call tools on other MCP servers (Demo, Denodo, Entitlement, etc.).
- Add new MCP tools as needed for new data sources or entitlement checks.

### D. Persona/Intent Detection (Detailed)
- Implement as a FastMCP tool (e.g., `detect_persona`).
- Use LLM-based classification or prompt engineering to infer persona (developer, analyst, etc.) and intent from query and history.
- Store/update persona profile per user/session in memory or DB.
- Orchestrator calls this tool at the start of each research session.

### E. Entitlement Check Integration (Detailed)
- Implement as a FastMCP tool (e.g., `check_entitlement`).
- Only trigger entitlement checks when subagent detects a data access operation.
- Cache entitlement results per session to avoid redundant checks.
- Return entitlement status and details to orchestrator for aggregation.

### F. Subagent Orchestration (Detailed)
- Orchestrator tool (`multi_agent_research`) spawns subagent tool calls in parallel (using asyncio.gather or similar).
- Each subagent tool call is a FastMCP client call (can be local or remote).
- Aggregate results, handle errors, and retry as needed.
- Iterate if more research is needed (e.g., if subagent results indicate missing info).

### G. Memory & Context Management
- Store plan, subagent outputs, and conversation history in a memory module (DB, Redis, or file).
- Implement context compression/summarization for long conversations.
- Retrieve and update memory as part of orchestrator tool logic.

### H. Conversation Storage & Profiling
- Store all conversations and subagent actions for future reference and personality building.
- Use this data to improve intent detection and user experience.

### I. Citation/Attribution
- After aggregation, run a citation agent/tool to attribute results to sources (tool outputs, data sources, etc.).
- Implement as a FastMCP tool if needed.

### J. Frontend Changes (Detailed)
- Update chat UI to display:
  - Multi-agent progress (subtask status, agent reasoning, persona feedback).
  - Citations and source attributions.
  - Persona/intent feedback and profile.
- Use MCP client in frontend to call orchestrator and subagent tools as needed.
- Show detailed agent/subagent reasoning and results in the UI.

### K. Observability & Reliability
- Add structured logging and tracing for all agent/subagent actions.
- Implement error handling, retries, and checkpointing for long-running tasks.
- Monitor health and performance of all MCP servers and agents.

### L. Chain-of-Thought Streaming to Frontend
- Orchestrator and subagents should emit chain-of-thought (CoT) traces as they plan, reason, and execute subtasks.
- Implement a streaming mechanism (e.g., Server-Sent Events, WebSockets, or FastMCP streaming) to send CoT traces to the frontend in real time.
- Allow users to opt-in to see agent/subagent thinking, plans, and execution steps as a live trace panel in the UI.
- CoT traces should include:
  - Planning steps (e.g., how the query is decomposed)
  - Subagent tool calls and responses
  - Reasoning, error handling, and retries
  - Aggregation and final synthesis steps
- Frontend should provide a toggle to show/hide live agent traces for transparency and debugging.
- Store CoT traces with conversation history for future review and debugging.

---

## 4. Best Practices (from Anthropic and DataFlow)
- Use orchestrator-worker (lead agent + subagents) pattern with FastMCP tools.
- Parallelize subagent execution for speed and coverage.
- Use explicit, detailed prompts for each subagent.
- Scale agent effort to query complexity.
- Prefer specialized tools over generic ones.
- Start with broad queries, then narrow down.
- Guide agent thinking with planning and scratchpad steps.
- Store intermediate results in memory, not just conversation context.
- Evaluate agent outcomes, not just process.
- Use LLM-as-judge for output evaluation and quality control.
- Add observability and tracing for debugging and reliability.

---

## 5. Next Steps
1. Scaffold orchestrator FastMCP server and tools.
2. Implement persona detection and subagent orchestration as FastMCP tools.
3. Integrate entitlement check as a FastMCP tool.
4. Update MCP servers/tools as needed for new data sources.
5. Add memory/context and conversation storage.
6. Enhance frontend for multi-agent visibility and citation.
7. Add observability, error handling, and evaluation.
8. Iterate with real user queries and refine prompts/logic.

---

*This plan is tailored for FastMCP-based agent orchestration and can be iteratively refined as the system evolves.*
