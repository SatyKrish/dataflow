# Multi-Agent Research System Implementation Plan (FastMCP Orchestration)

## 0. TECH STACK UPDATE 

**This implementation plan is updated for the following stack:**
- **Langraph** for agent logic and graph-based workflows (https://langraph.com/)
- **FastMCP** for agent orchestration (multi-agent coordination, tool calls, persona/entitlement subagents)
- **Azure OpenAI** as the LLM backend for all agent reasoning and generation

**MVP Key integration points:**
- **Single MCP server** under `/mcp/agent/` exposed to chat interface for clean architecture
- Internal subagent components coordinate via Langraph graphs within the main MCP server
- Use FastMCP client connections to call existing external MCP tools (denodo/, demo/)
- Use Azure OpenAI API for all LLM calls (via Langraph or FastMCP tool wrappers)
- **PostgreSQL** as primary data store with schema files under `/data/` folder
- **Redis** as cache layer for active session coordination and real-time agent status
- Focus on reliable metadata discovery and data retrieval across multiple sources via existing MCP tools
- Use Langraph's streaming and trace APIs for basic observability and debugging

---

## 1. System Overview (MVP)
- **Goal:** Enable users to use natural language for data/metadata queries across multiple data sources with intelligent agent orchestration.
- **MVP Features:**
  - Multi-agent orchestration (lead agent + subagents) using FastMCP
  - Metadata discovery and data retrieval from multiple sources
  - On-demand entitlement checks
  - Parallel subagent execution for efficiency
  - Basic conversation storage and session management
  - Observable and reliable multi-agent coordination

---

## 2. High-Level Architecture (Enhanced with Anthropic's Multi-Agent Pattern)

### 2.1 Orchestrator-Worker Pattern (Single MCP Server Architecture)

- **Main Agent MCP Server (Orchestrator):**
  - Implemented as a FastMCP server under `/mcp/agent/` (following existing structure with demo/ and denodo/)
  - **Only MCP server exposed to chat interface** - provides single point of interaction
  - Exposes a `multi_agent_research` tool and supporting tools via FastMCP protocol
  - **Research Planning:** Analyzes user query, develops strategy, saves plan to persistent memory
  - **Task Decomposition:** Breaks down complex queries into specific, bounded subtasks for internal subagents
  - **Parallel Coordination:** Spawns specialized subagents as internal components with separate context windows
  - **Iterative Research:** Evaluates subagent results and determines if additional research rounds are needed
  - **Synthesis & Aggregation:** Combines and analyzes findings from all subagents for final response

- **Internal Specialized Subagents (Components, not MCP servers):**
  - **MetadataAgent:** Explores data schemas, table structures, and semantic relationships across data sources
  - **EntitlementAgent:** Validates user permissions and data access rights
  - **DataAgent:** Retrieves and processes actual data based on metadata findings
  - **AggregationAgent:** Synthesizes results from multiple data sources and subagents
  - Each subagent operates as internal components within the main MCP server:
    - Clear objectives and output format specifications
    - Dedicated context windows for parallel exploration
    - Access to existing MCP tools (denodo/, demo/, etc.) via internal clients
    - Independent reasoning and tool execution capabilities

### 2.2 Dynamic Multi-Step Search vs Static RAG
- **Traditional RAG limitations:** Static retrieval fetches similarity-based chunks without adaptation
- **Our dynamic approach:** Multi-step search that:
  - Adapts to intermediate findings during research process
  - Follows leads that emerge from initial investigations  
  - Uses intelligent filtering through subagents as context compression mechanisms
  - Continuously refines search strategy based on discoveries
  - Operates across multiple independent context windows simultaneously

### 2.3 Context and Memory Architecture (Postgres-Backed)

#### 2.3.1 Primary Data Store: PostgreSQL

**Why PostgreSQL for Multi-Agent Orchestration:**
- **ACID transactions** ensure data consistency when multiple agents update session state simultaneously
- **Strong consistency** prevents race conditions in multi-agent coordination
- **SQL analytical functions** for session analysis and performance optimization
- **JSONB support** for flexible session memory and subagent result storage
- **Mature ecosystem** with excellent monitoring, backup/recovery, and scaling capabilities
- **Performance optimization** with specialized indexes for complex queries

#### 2.3.2 MVP Database Schema Design
```sql
-- Basic user management for MVP
users (
  user_id UUID PRIMARY KEY,
  email VARCHAR(255),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Research sessions for multi-agent orchestration
research_sessions (
  session_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  initial_query TEXT,
  research_plan JSONB,
  final_outcome JSONB,
  token_usage INTEGER,
  session_duration INTERVAL,
  status VARCHAR(50), -- 'active', 'completed', 'failed'
  created_at TIMESTAMP
);

-- Subagent execution tracking
subagent_executions (
  execution_id UUID PRIMARY KEY,
  session_id UUID REFERENCES research_sessions(session_id),
  agent_type VARCHAR(50), -- 'metadata', 'entitlement', 'data', 'aggregation'
  task_description TEXT,
  tool_calls JSONB,
  results JSONB,
  status VARCHAR(50), -- 'running', 'completed', 'failed'
  execution_time_ms INTEGER,
  created_at TIMESTAMP
);

-- Session memory for context management
session_memory (
  memory_id UUID PRIMARY KEY,
  session_id UUID REFERENCES research_sessions(session_id),
  memory_type VARCHAR(50), -- 'research_plan', 'intermediate_results', 'context_summary'
  content JSONB,
  created_at TIMESTAMP,
  expires_at TIMESTAMP
);
```

**Example MVP Queries:**
```sql
-- Track session success and token usage patterns
SELECT 
    agent_type,
    AVG(execution_time_ms) as avg_execution_time,
    COUNT(*) as total_executions,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_executions
FROM subagent_executions 
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY agent_type;

-- Session analysis for multi-agent optimization
SELECT 
    rs.session_id,
    rs.token_usage,
    rs.session_duration,
    COUNT(se.execution_id) as total_subagents,
    STRING_AGG(se.agent_type, ',') as agents_used
FROM research_sessions rs
LEFT JOIN subagent_executions se ON rs.session_id = se.session_id
WHERE rs.status = 'completed'
GROUP BY rs.session_id, rs.token_usage, rs.session_duration;

-- Find failed subagent patterns for debugging
SELECT agent_type, tool_calls, COUNT(*) as failure_count
FROM subagent_executions 
WHERE status = 'failed' 
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY agent_type, tool_calls
ORDER BY failure_count DESC;
```

#### 2.3.3 Database Artifacts Organization
- **Database artifacts under `/data/` folder:**
  - SQL schema definitions and migrations
  - Database initialization scripts
  - Seed data and test fixtures
  - Backup and recovery scripts
  
#### 2.3.4 Complementary Storage Systems
- **Redis Cache Layer:**
  - Session-level memory for active research processes
  - Entitlement check caching to avoid redundant API calls
  - Real-time agent coordination and status tracking
  
- **File System/Object Storage:**
  - Large artifact storage (reports, visualizations, datasets)
  - Subagent output files with Postgres storing lightweight references
  - Binary data and media files generated during research

### 2.4 Supporting Components (MVP)
- **Session Management:** Tracks research sessions, subagent execution, and basic user interaction patterns
- **Health Monitoring:** Tracks agent performance, success rates, and system reliability
- **Basic Observability:** Session tracking, token usage monitoring, and error logging for debugging

---

## 3. Implementation Steps (with FastMCP)

### A. Main Agent MCP Server (Single Exposed Server)
- Scaffold a FastMCP server under `/mcp/agent/` (following existing demo/, denodo/ structure).
- **Only MCP server exposed to chat interface** - single point of interaction
- Expose a `multi_agent_research` tool:
  - Accepts user query and session info.
  - Analyzes intent using internal query analysis components.
  - Decomposes query into subtasks for internal subagents.
  - Coordinates internal subagents and calls external MCP tools (denodo/, demo/) as needed.
  - Aggregates results and returns structured response.
- Add a `health_check` tool for monitoring.

### B. Internal Subagent Design (Components within Main MCP Server)
- **MetadataAgent:** Internal component that calls existing Denodo MCP server's `denodo_query` tool with `mode=metadata`.
- **EntitlementAgent:** Internal component for entitlement checks (may call external services).
- **DataAgent:** Internal component that calls existing Denodo MCP server's `denodo_query` tool with `mode=data`.
- **AggregationAgent:** Internal component that aggregates results from other subagents.
- Each internal subagent component should:
  - Operate within the main MCP server process.
  - Use MCP client connections to call existing external MCP tools as needed.
  - Return structured results for orchestrator coordination.

### C. Tooling & Integration
- Use FastMCP client to call tools on other MCP servers (Demo, Denodo, Entitlement, etc.).
- Add new MCP tools as needed for new data sources or entitlement checks.

### D. Basic Query Analysis (MVP)
- **Simple Intent Detection:**
  - Implement as FastMCP tool: `analyze_query_intent`
  - Classify queries as: metadata exploration, data retrieval, cross-source analysis
  - Determine appropriate subagent allocation based on query type
  - Store basic query patterns in session for debugging and optimization

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

### G. Memory & Context Management (Postgres + Redis Architecture)
- **PostgreSQL for Persistent Memory:**
  - Store research plans, session outcomes, and compressed context in `agent_memory` table
  - Use JSONB for flexible memory content storage with automatic expiration policies
  - Enable complex queries across historical research patterns for profile learning
  - Implement incremental updates with database transactions for consistency
  
- **Redis for Active Session Memory:**
  - Cache current research session state and subagent coordination data
  - Store real-time agent status and intermediate results for fast access
  - Implement session-level memory with TTL expiration for automatic cleanup
  - Enable pub/sub patterns for real-time agent coordination and progress updates
  
- **Context Compression Strategies:** 
  - Store full context in Postgres `agent_memory` before compression
  - Use intelligent summarization with compression levels tracked in database
  - Preserve key research findings and methodology in structured JSONB format
  - Implement context retrieval queries that reconstruct essential information
  
- **Artifact-based Output Storage:**
  - Store large outputs (reports, visualizations) in filesystem/object storage
  - Store metadata and lightweight references in `subagent_executions` table
  - Enable direct subagent-to-Postgres workflows with file system references
  - Track artifact relationships and dependencies in relational structure
  
- **Memory Retrieval Patterns:**
  - Use PostgreSQL full-text search and JSONB queries for context retrieval
  - Implement semantic similarity searches on research plans and outcomes
  - Enable cross-session pattern matching for user preference learning
  - Support checkpoint resumption through database transaction rollback/recovery

### H. Session Storage & Basic Analytics (MVP)
- **Session Data Collection:**
  - Store research sessions in `research_sessions` table with basic audit trail
  - Track subagent executions with performance metrics for debugging
  - Record session outcomes and token usage for optimization
  - Implement basic data retention policies
  
- **Simple Analytics:**
  - Track successful vs failed sessions for system reliability
  - Monitor subagent performance patterns for optimization
  - Identify common failure modes for debugging
  - Basic token usage analysis for cost optimization

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

### 5.3 Effort Scaling Rules (MVP)
- **Simple fact-finding:** 1-2 agents (MetadataAgent → DataAgent) with 3-10 tool calls
- **Cross-source queries:** 2-3 subagents (MetadataAgent, EntitlementAgent, DataAgent) with 10-15 calls each  
- **Complex analysis:** 3-4 subagents with AggregationAgent for synthesis
- **Embed scaling rules in prompts:** Prevent overinvestment in simple queries through explicit guidelines
- **Query-type based scaling:** Use basic intent detection to determine agent allocation
  - **Metadata exploration:** Start with MetadataAgent only
  - **Data retrieval:** MetadataAgent → EntitlementAgent → DataAgent pipeline
  - **Cross-source analysis:** Parallel MetadataAgents → EntitlementAgent → DataAgent → AggregationAgent

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

## 9. Best Practices (MVP Focus with Anthropic Insights)
- Use orchestrator-worker (lead agent + subagents) pattern with FastMCP tools
- Parallelize subagent execution for speed and coverage with separate context windows
- Use explicit, detailed prompts with clear objectives, output formats, and boundaries
- Scale agent effort to query complexity with embedded guidelines (1-4 agents for MVP)
- Prefer specialized tools over generic ones as agent-computer interfaces
- Start with metadata discovery, then narrow down to specific data retrieval
- Guide agent thinking with planning and scratchpad steps
- Store intermediate results in external memory/artifacts, not just conversation context
- Evaluate agent outcomes (end-state) not just process (turn-by-turn)
- Use LLM-as-judge for scalable output evaluation and quality control
- Add comprehensive observability and tracing for debugging agent decision patterns
- Implement stateful error handling with checkpoints and graceful degradation
- Build agent simulations for prompt engineering and failure mode identification
- Design for token economics with clear value justification for increased usage
- Focus on reliable multi-agent coordination before adding advanced personalization features

---

## 10. Implementation Priorities (Based on Anthropic's Production Experience)

### Phase 1: Core Multi-Agent Foundation (MVP)
1. **Set up PostgreSQL + Redis data architecture** with schema files under `/data/` folder
2. **Create main agent MCP server** under `/mcp/agent/` (single server exposed to chat interface)
3. **Build agent simulation environment** for prompt engineering and failure mode identification
4. **Implement internal subagent components** (MetadataAgent, EntitlementAgent, DataAgent, AggregationAgent)
5. **Add MCP client connections** to existing external MCP servers (denodo/, demo/)
6. **Implement multi-agent orchestration** with parallel internal subagent execution and result aggregation
7. **Add basic session storage and analytics** for debugging and optimization

### Phase 2: Advanced Features and Personality Profiling
8. **Implement persistent personality profiling** with comprehensive user behavior analysis
9. **Add profile-driven agent optimization** and personalized research strategies
10. **Enhance detailed task decomposition** with user preference-based boundaries and formats
11. **Create advanced analytics** for cross-session pattern analysis and user evolution tracking

### Phase 3: Production Reliability
10. **Implement stateful error handling** with database-backed checkpoints and graceful degradation
11. **Add comprehensive tracing and observability** for agent decision pattern monitoring using Postgres analytics
12. **Build evaluation systems** with end-state assessment and LLM-as-judge quality control stored in database
13. **Develop rainbow deployment strategy** for stateful agent system updates with database migrations

### Phase 4: Advanced Features and Optimization
14. **Enhance frontend** for multi-agent progress visibility and chain-of-thought streaming from database
15. **Implement token usage optimization** and cost monitoring using historical Postgres data analysis
16. **Add human evaluation workflows** to catch edge cases and biases with feedback stored in database
17. **Plan for asynchronous execution** to eliminate bottlenecks with Redis pub/sub coordination

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

### Immediate Actions (Week 1-2) - MVP Focus
1. Create `/data/` folder with PostgreSQL schema definitions and setup scripts
2. Set up PostgreSQL + Redis with basic session and subagent execution tables
3. Create main agent MCP server under `/mcp/agent/` (single server exposed to chat)
4. Build agent simulation environment using Console with exact prompts and tools

### Short-term Goals (Month 1) - Core Multi-Agent Functionality
5. Implement internal subagent components (MetadataAgent, EntitlementAgent, DataAgent, AggregationAgent)
6. Add MCP client connections to existing external MCP servers (denodo/, demo/)
7. Implement parallel internal subagent execution with proper session tracking
8. Add comprehensive logging and observability for debugging agent coordination

### Medium-term Objectives (Months 2-3) - Production Readiness
9. Implement stateful error handling with database-backed checkpoints
10. Add basic evaluation and quality control mechanisms
11. Optimize token usage and implement cost monitoring
12. **Begin Phase 2: Add persistent personality profiling and advanced personalization**

*MVP Focus: Get reliable multi-agent orchestration working before adding complex personalization features.*

---

*This plan is tailored for FastMCP-based agent orchestration and can be iteratively refined as the system evolves.*
