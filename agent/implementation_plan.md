# Multi-Agent Research System Implementation Plan (FastMCP Orchestration)

## 0. TECH STACK UPDATE 

**This implementation plan is updated for the following stack:**
- **Langraph** for agent logic and graph-based workflows (https://langraph.com/)
- **FastMCP** for agent orchestration (multi-agent coordination, tool calls, persona/entitlement subagents)
- **Azure OpenAI** as the LLM backend for all agent reasoning and generation

**Key integration points:**
- Define agent logic and subagent workflows as Langraph graphs (nodes for subagents, tools, memory, etc.) 
- Use FastMCP to expose orchestrator and subagent tools, and to coordinate multi-agent workflows
- Use Azure OpenAI API for all LLM calls (via Langraph or FastMCP tool wrappers)
- (Optional) Use Langraph's streaming and trace APIs to stream chain-of-thought to frontend

---

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

## 2. High-Level Architecture (Enhanced with Anthropic's Multi-Agent Pattern)

### 2.1 Orchestrator-Worker Pattern (Lead Agent + Specialized Subagents)

- **Orchestrator MCP Server (Lead Agent):**
  - Implemented as a FastMCP server (e.g., `/agent/orchestrator/fastmcp_server.py`)
  - Exposes a `multi_agent_research` tool and supporting tools via FastMCP protocol
  - **Research Planning:** Analyzes user query, develops strategy, saves plan to persistent memory
  - **Task Decomposition:** Breaks down complex queries into specific, bounded subtasks for subagents
  - **Parallel Coordination:** Spawns specialized subagents simultaneously with separate context windows
  - **Iterative Research:** Evaluates subagent results and determines if additional research rounds are needed
  - **Synthesis & Aggregation:** Combines and analyzes findings from all subagents for final response

- **Specialized Subagents (as FastMCP Tools):**
  - **MetadataAgent:** Explores data schemas, table structures, and semantic relationships
  - **EntitlementAgent:** Validates user permissions and data access rights
  - **DataAgent:** Retrieves and processes actual data based on metadata findings
  - **AggregationAgent:** Synthesizes results from multiple data sources and subagents
  - **CitationAgent:** Post-processes results to add source attributions and citations
  - Each subagent operates with:
    - Clear objectives and output format specifications
    - Dedicated context windows for parallel exploration
    - Specialized tool access and domain expertise
    - Independent reasoning and tool execution capabilities

### 2.2 Dynamic Multi-Step Search vs Static RAG
- **Traditional RAG limitations:** Static retrieval fetches similarity-based chunks without adaptation
- **Our dynamic approach:** Multi-step search that:
  - Adapts to intermediate findings during research process
  - Follows leads that emerge from initial investigations  
  - Uses intelligent filtering through subagents as context compression mechanisms
  - Continuously refines search strategy based on discoveries
  - Operates across multiple independent context windows simultaneously

### 2.3 Context and Memory Architecture
- **External Memory Systems:** 
  - Persistent storage for research plans, intermediate results, and conversation history
  - Separate from conversation context to prevent token overflow
  - Enables resumption from checkpoints without losing research progress
- **Artifact Storage:**
  - Direct subagent output to filesystem/database to minimize information loss
  - Structured outputs (reports, data, visualizations) stored independently
  - Lightweight references passed between agents instead of full content
- **Context Compression:**
  - Intelligent summarization when approaching context limits
  - Work phase completion summaries before proceeding to new tasks
  - Fresh subagent spawning with clean contexts while maintaining continuity

### 2.4 Supporting Components
- **Persona/Intent Profiler:** Analyzes user queries and history to optimize research strategy and subagent selection
- **Health Monitoring:** Tracks agent performance, success rates, and system reliability
- **Evaluation Systems:** End-state outcome assessment and LLM-as-judge quality control

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

### G. Memory & Context Management (Enhanced with Anthropic Insights)
- **External memory systems:** Store plan, subagent outputs, and conversation history in persistent memory (DB, Redis, or file) separate from conversation context
- **Context compression strategies:** 
  - Summarize completed work phases before proceeding to new tasks
  - Compress context when approaching 200K token limits to retain essential information
  - Use intelligent summarization to preserve key research findings and methodology
- **Artifact-based output storage:**
  - Implement filesystem/database storage for subagent structured outputs (reports, data, visualizations)
  - Store lightweight references in conversation context instead of full outputs
  - Enable direct subagent-to-storage workflows to minimize information loss through "telephone game"
- **Memory retrieval patterns:**
  - Retrieve stored context and research plans when resuming from checkpoints
  - Update memory incrementally as orchestrator and subagents complete tasks
  - Use semantic search or structured queries to retrieve relevant historical context
- **Long-horizon conversation support:**
  - Spawn fresh subagents with clean contexts while maintaining continuity through memory handoffs
  - Implement conversation coherence across context window boundaries
  - Store intermediate results separately from conversation flow for later aggregation

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

### M. Observability and End-to-End Tracing with OpenTelemetry

- Integrate OpenTelemetry into all components (orchestrator, subagents, FastMCP, and Langraph nodes) to enable distributed tracing and metrics collection.
- Ensure that each request is assigned a unique trace context that is propagated across all subagent/tool calls and workflow steps.
- Instrument Langraph nodes and FastMCP tool invocations to emit OpenTelemetry spans, capturing timing, status, and relevant metadata for each step.
- Export traces to a centralized backend (e.g., Jaeger, Zipkin, Azure Monitor) for end-to-end visibility and troubleshooting.
- Use OpenTelemetry to correlate frontend user actions with backend agent/subagent execution for full request lifecycle observability.
- Make OpenTelemetry tracing a non-optional requirement for all new agent and tool implementations.

---

## 4. Langraph-Based Orchestration of Subagents

Langraph is responsible for defining and executing the orchestration logic between subagents as a directed graph. The following steps detail how to implement this:

1. **Define the Orchestration Graph:**
   - Model the overall research workflow as a Langraph graph.
   - Each node in the graph represents a subagent/tool (e.g., MetadataAgent, EntitlementAgent, DataAgent, AggregationAgent).
   - Edges define the flow of data and control between nodes.

2. **Node Implementation:**
   - Each subagent/tool is implemented as a Langraph node with a clear input/output contract.
   - Nodes can be:
     - Synchronous (wait for result before proceeding)
     - Asynchronous/parallel (multiple nodes can execute in parallel if their dependencies are satisfied)

3. **Parallel Execution:**
   - Use Langraph’s parallel execution features to run independent subagents (e.g., MetadataAgent and EntitlementAgent) concurrently.
   - The orchestrator node triggers parallel execution by connecting multiple downstream nodes to a single upstream node.

4. **Aggregation and Synchronization:**
   - Use an AggregationAgent node to collect and combine results from multiple subagents.
   - The AggregationAgent node should wait for all required inputs before executing.

5. **Error Handling:**
   - Define error-handling logic in the graph (e.g., retry nodes, fallback nodes, or error aggregation nodes).
   - Langraph supports conditional edges to handle different execution paths based on node outputs.

6. **Dynamic Graph Construction:**
   - For complex queries, dynamically construct the Langraph graph at runtime based on the user’s intent and required subtasks.
   - Use persona/intent detection results to determine which subagents/nodes to include in the graph.

7. **Memory and Context Passing:**
   - Use Langraph’s context-passing features to share memory, intermediate results, and conversation history between nodes.
   - Ensure that each node receives the necessary context to perform its task.

8. **Chain-of-Thought Tracing:**
   - Enable Langraph’s trace/streaming APIs to emit execution traces for each node/subagent.
   - Stream these traces to the frontend for real-time transparency.

**Example (Pseudocode):**
```python
import langraph

# Define nodes
metadata_node = langraph.Node(MetadataAgent)
entitlement_node = langraph.Node(EntitlementAgent)
data_node = langraph.Node(DataAgent)
aggregation_node = langraph.Node(AggregationAgent)

# Define graph
graph = langraph.Graph()
graph.add_node(metadata_node)
graph.add_node(entitlement_node)
graph.add_node(data_node)
graph.add_node(aggregation_node)

# Define edges (parallel execution)
graph.add_edge('start', metadata_node)
graph.add_edge('start', entitlement_node)
graph.add_edge(metadata_node, data_node)
graph.add_edge(entitlement_node, data_node)
graph.add_edge(data_node, aggregation_node)

# Execute graph
result = graph.run(input_context)
```

This section provides actionable guidance for using Langraph to orchestrate subagent workflows. Update and extend as needed for your specific use case.

---

## 5. Advanced Prompt Engineering Principles (Based on Anthropic's Research)

### 5.1 Agent Simulation and Mental Models
- **Think like your agents:** Build simulations using Console with exact prompts and tools to understand agent behavior step-by-step
- **Identify failure modes early:** Watch for agents continuing when sufficient results exist, using verbose search queries, or selecting incorrect tools
- **Develop accurate mental models:** Understanding agent behavior makes impactful prompt changes obvious

### 5.2 Orchestrator Delegation Patterns
- **Detailed task descriptions:** Each subagent needs:
  - Clear objective and scope
  - Specific output format requirements
  - Tool and source guidance
  - Explicit task boundaries to prevent overlap
- **Avoid vague instructions:** Replace simple instructions like "research semiconductor shortage" with specific, bounded tasks
- **Division of labor:** Ensure subagents explore different aspects (e.g., one explores 2021 automotive crisis, another investigates current 2025 supply chains)

### 5.3 Effort Scaling Rules
- **Simple fact-finding:** 1 agent with 3-10 tool calls
- **Direct comparisons:** 2-4 subagents with 10-15 calls each  
- **Complex research:** 10+ subagents with clearly divided responsibilities
- **Embed scaling rules in prompts:** Prevent overinvestment in simple queries through explicit guidelines

### 5.4 Tool Design as Agent-Computer Interface
- **Tool interfaces are critical:** Agent-tool interfaces are as important as human-computer interfaces
- **Right tool selection:** Often strictly necessary, not just efficient
- **Specialized over generic:** Prefer domain-specific tools over generic search
- **Clear tool contracts:** Define precise input/output schemas and error handling

## 6. Token Economics and Performance Optimization

### 6.1 Token Usage Patterns (Based on Anthropic's Analysis)
- **Multi-agent systems use ~15× more tokens than chat interactions**
- **Token usage explains 80% of performance variance** in browsing/research tasks
- **Other performance factors:** Number of tool calls (15%) and model choice (5%)
- **Economic viability:** Requires tasks where value justifies increased token cost

### 6.2 Performance Scaling Strategies
- **Parallel reasoning:** Distribute work across agents with separate context windows
- **Model efficiency multipliers:** Upgrading to better models provides larger gains than doubling token budget
- **Context window optimization:** Use separate contexts for parallel exploration, then compress for lead agent

### 6.3 Task Suitability Assessment
- **Good fit for multi-agent:**
  - Heavy parallelization opportunities
  - Information exceeding single context windows
  - Complex tool interfaces and coordination
  - Breadth-first queries with independent directions
- **Poor fit for multi-agent:**
  - Shared context requirements
  - Many dependencies between agents
  - Real-time coordination needs
  - Simple, sequential tasks

## 7. Production Reliability Engineering

### 7.1 Stateful Error Management
- **Errors compound in agent systems:** Minor failures can cascade into large behavioral changes
- **Resume from checkpoints:** Build systems that resume from error points, not restart from beginning
- **Graceful degradation:** Use model intelligence to handle tool failures adaptively
- **Deterministic safeguards:** Combine AI adaptability with retry logic and regular checkpoints

### 7.2 Advanced Debugging Approaches
- **Non-deterministic challenges:** Agents make dynamic decisions, hard to reproduce issues
- **Full production tracing:** Monitor agent decision patterns and interaction structures without accessing conversation contents
- **Root cause analysis:** Track search queries, source selection, tool failures systematically
- **Pattern monitoring:** Identify unexpected behaviors and common failure modes

### 7.3 Stateful System Deployment
- **Rainbow deployments:** Gradually shift traffic from old to new versions while keeping both running
- **Prevent disruption:** Avoid breaking existing agents mid-process during deployments
- **Stateful coordination:** Manage prompts, tools, and execution logic updates carefully

### 7.4 Execution Model Trade-offs
- **Current synchronous approach:** Lead agent waits for subagent sets to complete
- **Bottleneck identification:** Single subagent can block entire system
- **Future asynchronous vision:** Agents working concurrently, creating subagents when needed
- **Complexity trade-offs:** Async adds challenges in result coordination, state consistency, error propagation

## 8. Evaluation and Quality Assurance

### 8.1 Multi-Agent Evaluation Strategies
- **End-state evaluation:** Focus on final outcomes rather than turn-by-turn analysis for state-mutating agents
- **Checkpoint-based assessment:** Evaluate discrete state changes rather than every intermediate step
- **Alternative path acceptance:** Acknowledge agents may find different valid paths to same goal

### 8.2 Long-Horizon Conversation Management
- **Context overflow prevention:** Summarize completed work phases before proceeding
- **External memory storage:** Store essential information outside conversation context
- **Fresh subagent spawning:** Create new agents with clean contexts while maintaining continuity
- **Conversation coherence:** Preserve context across extended interactions through careful handoffs

### 8.3 Output Fidelity Optimization
- **Artifact systems:** Allow subagents to create persistent outputs bypassing coordinator
- **Minimize "telephone game":** Direct subagent outputs to filesystem/storage reduce information loss
- **Lightweight references:** Pass references back to coordinator instead of copying large outputs
- **Specialized prompt advantages:** Subagent specialized prompts produce better results than general coordinator filtering

### 8.4 Human-AI Evaluation Balance
- **Automated evaluation:** Use LLM-as-judge for scalable assessment of hundreds of outputs
- **Human evaluation necessity:** Catch edge cases automation misses (hallucinations, system failures, source biases)
- **Source quality heuristics:** Address preference for SEO-optimized content over authoritative sources
- **Manual testing value:** Essential even with automated evaluations for edge case discovery

## 9. Best Practices (Updated with Anthropic Insights)
- Use orchestrator-worker (lead agent + subagents) pattern with FastMCP tools
- Parallelize subagent execution for speed and coverage with separate context windows
- Use explicit, detailed prompts with clear objectives, output formats, and boundaries
- Scale agent effort to query complexity with embedded guidelines
- Prefer specialized tools over generic ones as agent-computer interfaces
- Start with broad queries, then narrow down through iterative refinement
- Guide agent thinking with planning and scratchpad steps
- Store intermediate results in external memory/artifacts, not just conversation context
- Evaluate agent outcomes (end-state) not just process (turn-by-turn)
- Use LLM-as-judge for scalable output evaluation and quality control
- Add comprehensive observability and tracing for debugging agent decision patterns
- Implement stateful error handling with checkpoints and graceful degradation
- Build agent simulations for prompt engineering and failure mode identification
- Design for token economics with clear value justification for increased usage

---

## 10. Implementation Priorities (Based on Anthropic's Production Experience)

### Phase 1: Core Multi-Agent Foundation
1. **Build agent simulation environment** for prompt engineering and failure mode identification
2. **Scaffold orchestrator FastMCP server** with basic multi-agent coordination
3. **Implement external memory systems** for persistent research plans and context storage
4. **Create artifact storage infrastructure** for direct subagent outputs

### Phase 2: Specialized Subagents and Tool Design
5. **Develop specialized subagent tools** (MetadataAgent, EntitlementAgent, DataAgent) with clear contracts
6. **Implement detailed task decomposition** with explicit boundaries and output formats
7. **Add effort scaling rules** embedded in orchestrator prompts
8. **Create domain-specific tools** rather than generic search interfaces

### Phase 3: Production Reliability
9. **Implement stateful error handling** with checkpoints and graceful degradation
10. **Add comprehensive tracing and observability** for agent decision pattern monitoring  
11. **Build evaluation systems** with end-state assessment and LLM-as-judge quality control
12. **Develop rainbow deployment strategy** for stateful agent system updates

### Phase 4: Advanced Features and Optimization
13. **Enhance frontend** for multi-agent progress visibility and chain-of-thought streaming
14. **Implement token usage optimization** and cost monitoring for economic viability
15. **Add human evaluation workflows** to catch edge cases and biases
16. **Plan for asynchronous execution** to eliminate bottlenecks in future iterations

## 11. Success Metrics and Validation

### Performance Benchmarks (Aligned with Anthropic's Findings)
- **Token efficiency:** Monitor token usage patterns and cost per research task
- **Parallelization effectiveness:** Measure speedup from multi-agent vs single-agent approaches  
- **Research quality:** Use both automated LLM-as-judge and human evaluation
- **System reliability:** Track agent failure rates, error recovery, and checkpoint usage

### Quality Indicators
- **Source quality:** Ensure preference for authoritative sources over SEO-optimized content
- **Task completion:** Measure end-state success rather than process adherence
- **User satisfaction:** Track research task value delivery and time savings
- **Edge case handling:** Monitor performance on unusual or complex queries

## 12. Next Steps

### Immediate Actions (Week 1-2)
1. Set up agent simulation environment using Console with exact prompts and tools
2. Start with simple orchestrator FastMCP server and basic subagent coordination
3. Implement external memory storage for research plans and context persistence
4. Create initial prompt templates with detailed task descriptions and effort scaling rules

### Short-term Goals (Month 1)
5. Deploy specialized subagent tools with clear input/output contracts
6. Add comprehensive logging and tracing for agent decision patterns
7. Implement basic evaluation with LLM-as-judge for output quality assessment
8. Begin human evaluation processes to identify edge cases and failure modes

### Medium-term Objectives (Months 2-3)
9. Scale system for production reliability with stateful error handling
10. Optimize token usage and implement cost monitoring for economic viability
11. Enhance frontend with multi-agent progress visibility and chain-of-thought streaming
12. Plan transition to asynchronous execution model for eliminating bottlenecks

*Remember: Multi-agent systems burn through tokens 15× faster than chat, so ensure tasks justify the increased performance and cost.*

---

*This plan is tailored for FastMCP-based agent orchestration and can be iteratively refined as the system evolves.*
